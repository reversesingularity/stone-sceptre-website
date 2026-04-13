"""
SELF-REFINE Loop — The Nephilim Chronicles v2.0
===============================================
Implements the SELF-REFINE pattern (Madaan et al. 2024) as a standalone
scorer + optimizer loop for scene / chapter drafts.

How It Works:
    1. Receive an initial draft (prose)
    2. Score it against the 11-criterion weighted rubric (from CREATIVE_SWARM_ARCHITECTURE_v2.md)
    3. If weighted score < threshold: generate a structured critique
    4. Feed critique back as revision instructions to the drafting agent
    5. Iterate up to max_iterations; return the best-scoring version

Weighted Rubric (11 criteria, total weight = 100):
    Criterion                        Weight
    ─────────────────────────────────────────
    Canon Fidelity                    25
    Theological Consistency           15
    Character Voice Accuracy          12
    Acoustic Paradigm Adherence       10
    Timeline Consistency               8
    Plot Coherence                     8
    Prose Quality                      8
    Emotional Resonance                5
    Pacing & Structure                 5
    Foreshadowing Integration          2
    Originality                        2
    Total                            100

Usage as library:
    from self_refine_loop import refine
    final_draft, report = refine(
        initial_draft="...",
        book=3, chapter=7,
        author_notes="...",  # optional guidance
        max_iterations=3,
        pass_threshold=85,
    )

Usage as CLI:
    python self_refine_loop.py --input chapter.md --book 3 --chapter 7
    python self_refine_loop.py --input chapter.md --book 3 --chapter 7 --max-iter 3 --threshold 85
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT    = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
LOG_DIR         = PROJECT_ROOT / "LOGS"
LOG_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_URL        = "http://localhost:11434"
NEMOTRON_ROUTER   = "http://localhost:8768"
CANON_SEARCH_URL  = "http://localhost:8765"

# Local Nemotron 3 Super GGUF via llama-server (zero-cost CPU scoring)
LOCAL_NEMOTRON_PORT  = int(os.environ.get("LOCAL_NEMOTRON_PORT", "8780"))
LOCAL_NEMOTRON_URL   = f"http://localhost:{LOCAL_NEMOTRON_PORT}/v1/chat/completions"
LOCAL_NEMOTRON_MODEL = os.environ.get("LOCAL_NEMOTRON_MODEL", "nemotron-3-super")

SCORE_MODEL  = LOCAL_NEMOTRON_MODEL   # local Nemotron 3 Super (was: mistral)
REFINE_MODEL = "llama3.1"  # revision generator (Nemotron preferred via router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SELF-REFINE] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("self_refine")


# ── Rubric ────────────────────────────────────────────────────────────────────

RUBRIC = [
    {"id": "canon_fidelity",          "name": "Canon Fidelity",               "weight": 25,
     "description": "All facts consistent with SSOT_v3_MASTER.md and locked canon"},
    {"id": "theological_consistency", "name": "Theological Consistency",       "weight": 15,
     "description": "Upholds Christian apocalyptic worldview; no Gnostic drift"},
    {"id": "character_voice",         "name": "Character Voice Accuracy",      "weight": 12,
     "description": "Each character's dialogue and action matches their dossier"},
    {"id": "acoustic_paradigm",       "name": "Acoustic Paradigm Adherence",   "weight": 10,
     "description": "Supernatural tech operates via sound/vibration (not EM/visual)"},
    {"id": "timeline_consistency",    "name": "Timeline Consistency",           "weight":  8,
     "description": "Events correctly placed on the 2024–2030 locked timeline"},
    {"id": "plot_coherence",          "name": "Plot Coherence",                 "weight":  8,
     "description": "Scene advances the approved beat-plan without logical gaps"},
    {"id": "prose_quality",           "name": "Prose Quality",                  "weight":  8,
     "description": "Literary register; no purple prose; dense and evocative"},
    {"id": "emotional_resonance",     "name": "Emotional Resonance",            "weight":  5,
     "description": "Reader is moved; stakes feel real; not performative emotion"},
    {"id": "pacing_structure",        "name": "Pacing & Structure",             "weight":  5,
     "description": "Scene opens strongly, rises, resolves without padding"},
    {"id": "foreshadowing",           "name": "Foreshadowing Integration",      "weight":  2,
     "description": "Seeds planted for later books; Story Prototype foreshadow brief honoured"},
    {"id": "originality",             "name": "Originality",                    "weight":  2,
     "description": "Fresh images and approaches; avoids tropes"},
]

TOTAL_WEIGHT = sum(c["weight"] for c in RUBRIC)
assert TOTAL_WEIGHT == 100, f"Rubric weights must sum to 100, got {TOTAL_WEIGHT}"


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_draft(draft: str, book: int, chapter: int, author_notes: str = "") -> dict:
    """
    Call local scorer (Nemotron 3 Super GGUF) to rate the draft against every rubric criterion.
    Returns dict: {criterion_id: score_0_to_10, ..., "weighted_total": float}
    """
    rubric_text = "\n".join(
        f"  {i+1}. {c['name']} (weight {c['weight']}): {c['description']}"
        for i, c in enumerate(RUBRIC)
    )

    notes_block = f"\nAuthor guidance:\n{author_notes}\n" if author_notes else ""

    prompt = f"""You are a rigorous fiction editor scoring a scene draft for THE NEPHILIM CHRONICLES.
Book: {book}   Chapter: {chapter}
{notes_block}
Rate the draft 0–10 for each criterion. Return ONLY valid JSON.

Rubric:
{rubric_text}

Draft:
\"\"\"
{draft[:6000]}
\"\"\"

Return JSON format exactly:
{{
  "canon_fidelity": 0-10,
  "theological_consistency": 0-10,
  "character_voice": 0-10,
  "acoustic_paradigm": 0-10,
  "timeline_consistency": 0-10,
  "plot_coherence": 0-10,
  "prose_quality": 0-10,
  "emotional_resonance": 0-10,
  "pacing_structure": 0-10,
  "foreshadowing": 0-10,
  "originality": 0-10,
  "brief_justification": "one-sentence summary of main weakness"
}}"""

    raw = ollama_generate(SCORE_MODEL, prompt, max_tokens=512)

    # Extract JSON from response
    scores = extract_json(raw)
    if not scores:
        logger.warning("Scorer returned non-JSON; defaulting to 5s")
        scores = {c["id"]: 5 for c in RUBRIC}
        scores["brief_justification"] = "Scorer parse failure"

    # Compute normalised weighted total (0–100)
    total = 0.0
    for c in RUBRIC:
        raw_score = float(scores.get(c["id"], 5))
        raw_score = max(0.0, min(10.0, raw_score))  # clamp
        total += (raw_score / 10.0) * c["weight"]
    scores["weighted_total"] = round(total, 2)

    return scores


def weighted_score(scores: dict) -> float:
    return scores.get("weighted_total", 0.0)


# ── Critique Generation ───────────────────────────────────────────────────────

def generate_critique(draft: str, scores: dict, book: int, chapter: int) -> str:
    """
    Produce a structured revision brief from the scoring results.
    Focuses on the weakest criteria (below 7/10).
    """
    weak_items = []
    for c in RUBRIC:
        raw_score = scores.get(c["id"], 5)
        if float(raw_score) < 7.0:
            weak_items.append(
                f"- {c['name']} (scored {raw_score}/10): {c['description']}"
            )

    if not weak_items:
        return "All criteria above threshold. Minor polish only."

    weak_block = "\n".join(weak_items)
    justification = scores.get("brief_justification", "")

    prompt = f"""You are a senior editor for THE NEPHILIM CHRONICLES (Book {book}, Chapter {chapter}).
The following scene draft has weaknesses. Generate a SPECIFIC, ACTIONABLE revision brief.

Weak areas:
{weak_block}

Overall weakness: {justification}

Instructions:
- For each weak area, give 1–2 concrete revision actions
- Reference specific passages in the draft where possible
- Keep the brief to under 400 words
- Format as a numbered list

Draft:
\"\"\"
{draft[:4000]}
\"\"\"

Revision brief:"""

    return ollama_generate(REFINE_MODEL, prompt, max_tokens=600)


# ── Revision Generation ───────────────────────────────────────────────────────

def generate_revision(draft: str, critique: str, book: int, chapter: int,
                      author_notes: str = "") -> str:
    """
    Send draft + critique to Nemotron (via router) for revision.
    Falls back to Ollama if router unavailable.
    """
    notes_block = f"\nAuthor guidance:\n{author_notes}\n" if author_notes else ""

    system = (
        "You are co-authoring THE NEPHILIM CHRONICLES — literary apocalyptic fiction. "
        "Maintain the existing prose register: dense, evocative, theologically grounded. "
        "DO NOT add characters, plot events, or canon facts not present in the original. "
        "Your task is revision only — improve what is there without changing the story."
    )
    user_prompt = f"""Book {book}, Chapter {chapter} — REVISION TASK
{notes_block}
REVISION BRIEF (editor's critique to address):
{critique}

ORIGINAL DRAFT:
\"\"\"
{draft}
\"\"\"

Write the revised scene in full. Do not include any meta-commentary; output only the prose."""

    # Try Nemotron via router first
    try:
        r = requests.post(
            f"{NEMOTRON_ROUTER}/route",
            json={
                "task_type": "scene_revision",
                "system":    system,
                "prompt":    user_prompt,
                "max_tokens": 4096,
            },
            timeout=300,
        )
        r.raise_for_status()
        data = r.json()
        if "error" not in data:
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
    except Exception as e:
        logger.warning(f"Nemotron router unavailable for revision: {e}")

    # Fallback: local Ollama
    full_prompt = f"{system}\n\n{user_prompt}"
    return ollama_generate(REFINE_MODEL, full_prompt, max_tokens=4096)


# ── Main Refine Loop ──────────────────────────────────────────────────────────

def refine(
    initial_draft: str,
    book: int,
    chapter: int,
    author_notes: str = "",
    max_iterations: int = 3,
    pass_threshold: float = 85.0,
) -> tuple[str, dict]:
    """
    Run the SELF-REFINE loop.

    Returns:
        (best_draft: str, report: dict)
        report includes iteration history and final scores.
    """
    current_draft = initial_draft
    best_draft    = initial_draft
    best_score    = 0.0
    history       = []

    logger.info(f"SELF-REFINE: Book {book} Chapter {chapter} | "
                f"max_iter={max_iterations} threshold={pass_threshold}")

    for iteration in range(1, max_iterations + 1):
        logger.info(f"  Iteration {iteration}/{max_iterations}: scoring...")
        scores = score_draft(current_draft, book, chapter, author_notes)
        ws = weighted_score(scores)
        logger.info(f"  Weighted score: {ws:.1f}/100")

        history.append({
            "iteration": iteration,
            "weighted_score": ws,
            "scores": scores,
        })

        if ws > best_score:
            best_score = ws
            best_draft = current_draft

        if ws >= pass_threshold:
            logger.info(f"  PASS threshold reached ({ws:.1f} >= {pass_threshold}) — stopping")
            break

        if iteration == max_iterations:
            logger.info(f"  Max iterations reached — returning best draft ({best_score:.1f})")
            break

        # Generate critique
        logger.info(f"  Generating critique...")
        critique = generate_critique(current_draft, scores, book, chapter)

        # Generate revision
        logger.info(f"  Generating revision...")
        revised = generate_revision(current_draft, critique, book, chapter, author_notes)

        if not revised or len(revised) < 100:
            logger.warning("  Revision generation returned empty/short text — stopping")
            break

        current_draft = revised

    report = {
        "book":         book,
        "chapter":      chapter,
        "final_score":  best_score,
        "pass_threshold": pass_threshold,
        "iterations":   len(history),
        "passed":       best_score >= pass_threshold,
        "history":      history,
        "timestamp":    datetime.now().isoformat(),
    }

    logger.info(f"SELF-REFINE complete: final score {best_score:.1f}/100 "
                f"{'PASS' if report['passed'] else 'BEST-EFFORT'}")
    return best_draft, report


# ── Helpers ───────────────────────────────────────────────────────────────────

def ollama_generate(model: str, prompt: str, max_tokens: int = 2048) -> str:
    """Generate via Ollama or — if model matches local Nemotron — via llama-server."""
    if model == LOCAL_NEMOTRON_MODEL:
        return local_nemotron_generate(prompt, max_tokens)
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False,
              "options": {"num_predict": max_tokens}},
        timeout=300,
    )
    r.raise_for_status()
    return r.json().get("response", "")


def local_nemotron_generate(prompt: str, max_tokens: int = 2048) -> str:
    """Call local Nemotron 3 Super GGUF via llama-server's OpenAI-compatible API."""
    try:
        r = requests.post(
            LOCAL_NEMOTRON_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": LOCAL_NEMOTRON_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            },
            timeout=600,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Local Nemotron scorer failed ({e}), falling back to Ollama llama3.1")
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "llama3.1", "prompt": prompt, "stream": False,
                  "options": {"num_predict": max_tokens}},
            timeout=300,
        )
        r.raise_for_status()
        return r.json().get("response", "")


def extract_json(text: str) -> dict | None:
    """Find and parse the first JSON object in text."""
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return None


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SELF-REFINE loop for TNC scene drafts"
    )
    parser.add_argument("--input",     required=True, help="Path to draft .md file")
    parser.add_argument("--book",      type=int, required=True, help="Book number (3–5)")
    parser.add_argument("--chapter",   type=int, required=True, help="Chapter number")
    parser.add_argument("--notes",     default="", help="Author guidance notes")
    parser.add_argument("--max-iter",  type=int, default=3, help="Max refinement iterations")
    parser.add_argument("--threshold", type=float, default=85.0, help="Pass threshold (0–100)")
    parser.add_argument("--output",    default="", help="Save refined draft to file")
    args = parser.parse_args()

    draft_path = Path(args.input)
    if not draft_path.exists():
        print(f"ERROR: File not found: {draft_path}")
        sys.exit(1)

    initial_draft = draft_path.read_text(encoding="utf-8")
    logger.info(f"Loaded draft: {draft_path.name} ({len(initial_draft):,} chars)")

    best_draft, report = refine(
        initial_draft,
        book=args.book,
        chapter=args.chapter,
        author_notes=args.notes,
        max_iterations=args.max_iter,
        pass_threshold=args.threshold,
    )

    print("\n" + "═" * 60)
    print(f"SELF-REFINE REPORT")
    print(f"  Final score:  {report['final_score']:.1f}/100")
    print(f"  Threshold:    {report['pass_threshold']}")
    print(f"  Result:       {'✓ PASS' if report['passed'] else '⚠ BEST-EFFORT'}")
    print(f"  Iterations:   {report['iterations']}")
    print("═" * 60)

    for h in report["history"]:
        just = h["scores"].get("brief_justification", "")
        print(f"  Iter {h['iteration']}: {h['weighted_score']:.1f}/100  — {just}")

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(best_draft, encoding="utf-8")
        print(f"\nRefined draft saved: {out_path}")

        report_path = out_path.with_suffix(".refine_report.json")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Refinement report:  {report_path}")
    else:
        print("\n--- REFINED DRAFT ---\n")
        print(best_draft[:2000])
        if len(best_draft) > 2000:
            print(f"\n... [{len(best_draft) - 2000:,} more chars] ...")


if __name__ == "__main__":
    main()
