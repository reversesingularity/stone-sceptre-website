"""
Book 1 Canonical Drift Audit — Direct Ollama
============================================
Audits all Book 1 chapters chapter-by-chapter, calling Ollama directly
(bypasses Nemotron router / GGUF entirely — avoids 600s GGUF timeout).

Checks each chapter against the 9 canonical violation categories:
  1. CANON_CONTRADICTION   — contradicts SSOT_v3_MASTER.md
  2. CHARACTER_STATE       — ability/age/status inconsistency
  3. TIMELINE_ERROR        — wrong place on 2024–2030 timeline
  4. ACOUSTIC_PARADIGM     — supernatural tech uses EM/visual, not acoustic
  5. THEOLOGY_DRIFT        — inconsistent with Christian apocalyptic framework
  6. TRINITARIAN_DRIFT     — Trinity language / Holy Spirit as Person (PROHIBITED)
  7. OIKETERION_VIOLATION  — Watcher demonstrates innate power post-descent
  8. RAPHAEL_LIMIT         — one of three canonical limits violated
  9. NAME_DRIFT            — character name diverges from official dossiers

Output:
    02_ANALYSIS/BOOK1_CANONICAL_AUDIT_<date>.md
    LOGS/AUDIT_SUMMARY.log  (appended)

Usage:
    python audit_book1_direct.py
    python audit_book1_direct.py --verbose
"""

import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
BOOK1_DIR    = PROJECT_ROOT / "MANUSCRIPT" / "book_1"
CANON_DIR    = PROJECT_ROOT / "CANON"
DOSSIERS_DIR = CANON_DIR / "dossiers"
OUTPUT_DIR   = PROJECT_ROOT / "02_ANALYSIS"
LOG_DIR      = PROJECT_ROOT / "LOGS"

SSOT_PATH    = CANON_DIR / "SSOT_v3_MASTER.md"

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"

# Context budget per chapter call (keep well within llama3.1's 8k context)
SSOT_EXCERPT_CHARS    = 5000
DOSSIER_EXCERPT_CHARS = 2500
CHAPTER_EXCERPT_CHARS = 3000
MAX_OUTPUT_TOKENS     = 2048

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [B1-AUDIT] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("b1_audit")

# ── Canon loading ─────────────────────────────────────────────────────────────

def load_text(path: Path, max_chars: int = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars] if max_chars else text


def load_dossiers(max_chars: int = DOSSIER_EXCERPT_CHARS) -> str:
    if not DOSSIERS_DIR.exists():
        return ""
    parts = []
    for f in sorted(DOSSIERS_DIR.glob("*.md")):
        parts.append(f"## {f.name}\n{load_text(f, 600)}")
    combined = "\n\n".join(parts)
    return combined[:max_chars]


def load_book1_chapters() -> list[dict]:
    chapters = []
    for f in sorted(BOOK1_DIR.glob("*.md")):
        text = load_text(f)
        if text.strip():
            chapters.append({
                "filename": f.name,
                "path": str(f),
                "text": text,
                "size_kb": round(len(text) / 1024, 1),
            })
    logger.info(f"Loaded {len(chapters)} Book 1 files")
    return chapters


# ── Audit prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a rigorous continuity auditor for THE NEPHILIM CHRONICLES, a 5-book Christian apocalyptic fiction series.

INVIOLABLE CANON RULES:
1. The Acoustic Paradigm: ALL supernatural technology operates through SOUND/VIBRATION only — never electromagnetic, visual, or chemical mechanisms.
2. Oiketerion Principle (Jude 1:6): Watchers LOST innate powers at descent. They can TEACH but never DEMONSTRATE supernatural abilities.
3. Binitarian Godhead: God = Father + Son (two Persons). Holy Spirit = shared essence/power, NOT a separate Person. NEVER call it "the Third Person" or "the Trinity."
4. Raphael's 3 limits: (a) cannot kill fallen Watchers, (b) cannot enter Cydonia-1, (c) cannot violate human free will.
5. Timeline: Book 1 begins January 2024. Titan-1-5 launch Oct 15, 2026 from Boca Chica. Fleet arrives Mars May 2027.
6. Azazel is a NEPHILIM (son of Gadreel), NOT a Watcher.
7. Brennan's surname is McNeeve — NOT "Webb" (that is a canon drift error).
8. Watchers → Nephilim → Apkallu (fish-men sages) → Sumerians → Mystery Babylon → WEF/Club of Rome.
9. Satan/Ohya/Azazel = Satanic Triumvirate (operational command triad) — NOT an "Unholy Trinity."
10. Mo Chrá produces CREATION FREQUENCIES (acoustic) — not light, not EM radiation.

Your task: Read the chapter excerpt and flag ANY violation of the above rules.

Return JSON ONLY in this format:
{
  "chapter": "<filename>",
  "violations": [
    {
      "category": "<category name>",
      "severity": "CRITICAL|MAJOR|MINOR",
      "passage": "<offending quote>",
      "canon_rule": "<which rule above>",
      "correction": "<what it should say>"
    }
  ],
  "clean": true/false,
  "notes": "<brief summary>"
}

If no violations found, return {"chapter": "<filename>", "violations": [], "clean": true, "notes": "No violations detected."}"""


def build_chapter_prompt(filename: str, chapter_text: str, ssot: str, dossiers: str) -> str:
    return f"""## SSOT CANON EXCERPT (binding)
{ssot}

## CHARACTER DOSSIERS (excerpt)
{dossiers}

## CHAPTER TO AUDIT: {filename}
{chapter_text[:CHAPTER_EXCERPT_CHARS]}
{"[...chapter truncated at 3000 chars for context budget...]" if len(chapter_text) > CHAPTER_EXCERPT_CHARS else ""}

Audit this chapter against the 10 inviolable canon rules. Return JSON only:"""


# ── Ollama call ───────────────────────────────────────────────────────────────

def audit_chapter_ollama(filename: str, chapter_text: str, ssot: str, dossiers: str) -> dict:
    prompt = build_chapter_prompt(filename, chapter_text, ssot, dossiers)

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
                "stream": False,
                "options": {
                    "num_predict": MAX_OUTPUT_TOKENS,
                    "temperature": 0.1,
                    "num_ctx": 8192,
                },
            },
            timeout=180,
        )
        r.raise_for_status()
        raw = r.json().get("response", "")
        return parse_json_response(raw, filename)
    except requests.exceptions.Timeout:
        logger.warning(f"  Ollama timeout on {filename}")
        return {"chapter": filename, "violations": [], "clean": None, "notes": "TIMEOUT — could not audit"}
    except Exception as e:
        logger.warning(f"  Ollama error on {filename}: {e}")
        return {"chapter": filename, "violations": [], "clean": None, "notes": f"ERROR: {e}"}


def parse_json_response(text: str, filename: str) -> dict:
    # Find JSON block
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {"chapter": filename, "violations": [], "clean": None, "notes": "Parse failed — no JSON"}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        return {"chapter": filename, "violations": [], "clean": None, "notes": f"JSON parse error: {e}"}


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(all_results: list[dict]) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = OUTPUT_DIR / f"BOOK1_CANONICAL_AUDIT_{today}.md"

    all_violations = []
    for r in all_results:
        for v in r.get("violations", []):
            v["_chapter"] = r.get("chapter", "?")
            all_violations.append(v)

    critical = [v for v in all_violations if v.get("severity") == "CRITICAL"]
    major    = [v for v in all_violations if v.get("severity") == "MAJOR"]
    minor    = [v for v in all_violations if v.get("severity") == "MINOR"]
    errored  = [r for r in all_results if r.get("clean") is None]
    clean    = [r for r in all_results if r.get("clean") is True]

    lines = [
        f"# Book 1 Canonical Drift Audit — {today}",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Chapters audited:** {len(all_results)}",
        f"**Clean:** {len(clean)}  |  **With violations:** {len([r for r in all_results if r.get('violations')])}  |  **Errors/timeouts:** {len(errored)}",
        f"**Total violations:** {len(all_violations)} ({len(critical)} critical, {len(major)} major, {len(minor)} minor)",
        "",
        "---",
        "",
    ]

    if critical:
        lines.append("## CRITICAL VIOLATIONS")
        for v in critical:
            lines.extend([
                f"### [{v.get('category','?')}] — {v.get('_chapter','?')}",
                f"> {v.get('passage','')}",
                f"",
                f"**Rule:** {v.get('canon_rule','N/A')}",
                f"**Correction:** {v.get('correction','N/A')}",
                "",
            ])

    if major:
        lines.append("## MAJOR VIOLATIONS")
        for v in major:
            lines.extend([
                f"### [{v.get('category','?')}] — {v.get('_chapter','?')}",
                f"> {v.get('passage','')}",
                f"",
                f"**Rule:** {v.get('canon_rule','N/A')}",
                f"**Correction:** {v.get('correction','N/A')}",
                "",
            ])

    if minor:
        lines.append("## MINOR VIOLATIONS")
        for v in minor:
            lines.extend([
                f"### [{v.get('category','?')}] — {v.get('_chapter','?')}",
                f"> {v.get('passage','')}",
                f"",
                f"**Rule:** {v.get('canon_rule','N/A')}",
                f"**Correction:** {v.get('correction','N/A')}",
                "",
            ])

    lines.append("## Chapter-by-Chapter Summary")
    for r in all_results:
        v_count = len(r.get("violations", []))
        status = "✓ CLEAN" if r.get("clean") else ("⚠ VIOLATIONS" if v_count else "? TIMEOUT/ERROR")
        notes = r.get("notes", "")
        lines.append(f"- **{r.get('chapter','?')}** — {status}  |  {v_count} violations  |  {notes}")

    if not all_violations:
        lines.append("\n---\n**NO VIOLATIONS DETECTED IN BOOK 1** ✓")

    if errored:
        lines.append("\n## Audit Errors / Timeouts")
        for r in errored:
            lines.append(f"- {r.get('chapter','?')}: {r.get('notes','')}")

    content = "\n".join(lines)
    out_path.write_text(content, encoding="utf-8")
    logger.info(f"Report written: {out_path}")
    return out_path


def append_summary_log(report_path: Path, all_violations: list, chapter_count: int):
    log_path = LOG_DIR / "AUDIT_SUMMARY.log"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    critical = sum(1 for v in all_violations if v.get("severity") == "CRITICAL")
    flag = "⚠ CRITICAL" if critical > 0 else ("⚠" if all_violations else "✓")
    line = (f"{ts}  {flag}  Book=1  chapters={chapter_count}  "
            f"violations={len(all_violations)} (critical={critical})  "
            f"report={report_path.name}")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Book 1 canonical drift audit — direct Ollama")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("  BOOK 1 CANONICAL DRIFT AUDIT (direct Ollama)")
    logger.info("=" * 60)

    # Load canon context once
    ssot     = load_text(SSOT_PATH, SSOT_EXCERPT_CHARS)
    dossiers = load_dossiers()
    chapters = load_book1_chapters()

    if not chapters:
        logger.error("No Book 1 chapters found. Exiting.")
        sys.exit(1)

    all_results = []
    for i, ch in enumerate(chapters, 1):
        logger.info(f"[{i}/{len(chapters)}] {ch['filename']} ({ch['size_kb']} KB)")
        result = audit_chapter_ollama(ch["filename"], ch["text"], ssot, dossiers)
        v_count = len(result.get("violations", []))
        status = "CLEAN" if result.get("clean") else (f"{v_count} violations" if v_count else "ERROR/TIMEOUT")
        logger.info(f"  → {status}  |  {result.get('notes','')}")
        all_results.append(result)

    # Aggregate
    all_violations = []
    for r in all_results:
        for v in r.get("violations", []):
            v["_chapter"] = r.get("chapter", "?")
            all_violations.append(v)

    critical = sum(1 for v in all_violations if v.get("severity") == "CRITICAL")

    report_path = write_report(all_results)
    append_summary_log(report_path, all_violations, len(chapters))

    print(f"\n{'=' * 60}")
    print(f"BOOK 1 AUDIT COMPLETE")
    print(f"  Chapters:   {len(chapters)}")
    print(f"  Violations: {len(all_violations)} ({critical} critical)")
    print(f"  Report:     {report_path}")
    print(f"{'=' * 60}")

    if critical > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
