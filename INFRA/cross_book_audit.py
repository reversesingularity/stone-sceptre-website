"""
Cross-Book Continuity Audit — The Nephilim Chronicles v2.0
==========================================================
Nightly auditor that loads all draft chapters from Books 3, 4, and 5
alongside the SSOT and character dossiers, then checks for continuity
violations using Nemotron (via router) or Ollama fallback.

Designed to be triggered nightly at 02:00 by Nemoclaw daemon via n8n
webhook /webhook/nightly-continuity-prep, or run manually.

Output:
    02_ANALYSIS/NIGHTLY_AUDIT_<YYYY-MM-DD>.md   — full audit report
    LOGS/AUDIT_SUMMARY.log                       — rolling one-liner log

Usage:
    python cross_book_audit.py
    python cross_book_audit.py --books 3,4 --verbose
    python cross_book_audit.py --chapter MANUSCRIPT/book_3/CHAPTER_01.md --fast
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

PROJECT_ROOT   = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
MANUSCRIPT_DIR = PROJECT_ROOT / "MANUSCRIPT"
CANON_DIR      = PROJECT_ROOT / "CANON"
DOSSIERS_DIR   = CANON_DIR / "dossiers"
OUTPUT_DIR     = PROJECT_ROOT / "02_ANALYSIS"
LOG_DIR        = PROJECT_ROOT / "LOGS"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

SSOT_PATH      = CANON_DIR / "SSOT_v3_MASTER.md"
SERIES_BIBLE   = CANON_DIR / "SERIES_BIBLE.md"

NEMOTRON_ROUTER  = "http://localhost:8768"
OLLAMA_URL       = "http://localhost:11434"
N8N_BASE         = "http://localhost:5678"
CANON_SEARCH_URL = "http://localhost:8765"

AUDIT_MODEL_LOCAL = "llama3.1"
MAX_CONTEXT_CHARS = 200_000   # conservative for Ollama fallback; router handles 1M for Nemotron

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CROSS-AUDIT] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("cross_audit")


# ── File Loading ──────────────────────────────────────────────────────────────

def load_text(path: Path, max_chars: int = None) -> str:
    """Read a file; return empty string if not found."""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars:
        text = text[:max_chars]
    return text


def load_book_chapters(book_num: int) -> list[dict]:
    """Load all .md files from MANUSCRIPT/book_N/, sorted by name."""
    book_dir = MANUSCRIPT_DIR / f"book_{book_num}"
    if not book_dir.exists():
        return []

    chapters = []
    for f in sorted(book_dir.glob("*.md")):
        text = load_text(f)
        if text.strip():
            chapters.append({
                "book":     book_num,
                "filename": f.name,
                "path":     str(f),
                "text":     text,
                "chars":    len(text),
            })
    logger.info(f"  Book {book_num}: {len(chapters)} chapters loaded")
    return chapters


def load_dossiers() -> str:
    """Concatenate all dossier files into a single string."""
    if not DOSSIERS_DIR.exists():
        return ""
    parts = []
    for f in sorted(DOSSIERS_DIR.glob("*.md")):
        parts.append(f"# {f.name}\n" + load_text(f, 3000))
    return "\n\n---\n\n".join(parts)


# ── Audit Prompt Builder ──────────────────────────────────────────────────────

AUDIT_SYSTEM = """You are THE NEPHILIM CHRONICLES continuity auditor. You have:
- The canonical SSOT v3 (constitutionally binding)
- All relevant character dossiers
- Multiple chapters spanning Books 3–5

Your task: find CONTINUITY VIOLATIONS — contradictions between chapters or against canon.

VIOLATION CATEGORIES:
1. CANON_CONTRADICTION — fact in chapter contradicts SSOT_v3_MASTER.md
2. CHARACTER_STATE — character ability, age, or status inconsistency across chapters
3. TIMELINE_ERROR — event placed at wrong point on 2024–2030 timeline
4. ACOUSTIC_PARADIGM — supernatural tech using electromagnetic/visual mechanisms (not acoustic)
5. THEOLOGY_DRIFT — theologically inconsistent with Christian apocalyptic framework
6. CONTINUITY_GAP — character/object appears without proper introduction or disappears without explanation
7. DUPLICATE_EVENT — same event described differently in two chapters

For each violation:
- Classify it (category above)
- Quote the offending passage
- Cite the canon source that contradicts it
- Suggest the correction

If no violations found, say: NO_VIOLATIONS_DETECTED

Return structured JSON only."""

AUDIT_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "report_continuity_violations",
        "description": "Report all continuity violations found",
        "parameters": {
            "type": "object",
            "properties": {
                "violations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category":    {"type": "string"},
                            "severity":    {"type": "string", "enum": ["CRITICAL", "MAJOR", "MINOR"]},
                            "chapter":     {"type": "string"},
                            "book":        {"type": "integer"},
                            "passage":     {"type": "string"},
                            "canon_ref":   {"type": "string"},
                            "correction":  {"type": "string"},
                        },
                        "required": ["category", "severity", "chapter", "book", "passage", "correction"]
                    }
                },
                "summary": {"type": "string"},
            },
            "required": ["violations", "summary"]
        }
    }
}


def build_audit_prompt(chapters: list[dict], ssot_excerpt: str, dossier_excerpt: str) -> str:
    """Build the audit prompt, respecting context limits."""
    chapter_blocks = []
    for ch in chapters:
        block = (
            f"### Book {ch['book']} — {ch['filename']}\n"
            f"{ch['text'][:3000]}\n"
            f"{'[...truncated...]' if ch['chars'] > 3000 else ''}"
        )
        chapter_blocks.append(block)

    chapters_text = "\n\n---\n\n".join(chapter_blocks)

    return f"""## SSOT v3 MASTER EXCERPTS (binding canon)
{ssot_excerpt[:8000]}

## CHARACTER DOSSIERS (excerpts)
{dossier_excerpt[:4000]}

## CHAPTERS TO AUDIT
{chapters_text}

Conduct a full cross-book continuity audit. Return JSON tool call ONLY:"""


# ── Nemotron Audit ────────────────────────────────────────────────────────────

def run_nemotron_audit(prompt: str) -> dict:
    """Send audit request to Nemotron via tool router."""
    r = requests.post(
        f"{NEMOTRON_ROUTER}/route",
        json={
            "task_type":    "cross_book_audit",
            "system":       AUDIT_SYSTEM,
            "prompt":       prompt,
            "tool_schemas": [AUDIT_TOOL_SCHEMA],
            "max_tokens":   4096,
        },
        timeout=600,
    )
    r.raise_for_status()
    data = r.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    # Extract tool call result
    tool_calls = data.get("_tool_calls", [])
    if tool_calls:
        args_raw = tool_calls[0].get("function", {}).get("arguments", "{}")
        if isinstance(args_raw, str):
            return json.loads(args_raw)
        return args_raw

    # Fall back to parsing content
    choices = data.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
        return parse_audit_json(content)

    return {"violations": [], "summary": "No response from Nemotron"}


def run_ollama_audit(prompt: str) -> dict:
    """Run audit locally with Ollama (slower, smaller context)."""
    full_prompt = f"{AUDIT_SYSTEM}\n\n{prompt}"
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model":  AUDIT_MODEL_LOCAL,
            "prompt": full_prompt[:MAX_CONTEXT_CHARS],
            "stream": False,
            "options": {"num_predict": 4096},
        },
        timeout=600,
    )
    r.raise_for_status()
    content = r.json().get("response", "")
    return parse_audit_json(content)


def parse_audit_json(text: str) -> dict:
    """Extract JSON from LLM response text."""
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {"violations": [], "summary": "Parse failed — no JSON in response"}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {"violations": [], "summary": f"Parse failed — invalid JSON"}


# ── Report Writer ─────────────────────────────────────────────────────────────

def write_audit_report(result: dict, books_audited: list[int], chapter_count: int) -> Path:
    """Write full audit report to 02_ANALYSIS/."""
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = OUTPUT_DIR / f"NIGHTLY_AUDIT_{today}.md"

    violations = result.get("violations", [])
    summary    = result.get("summary", "")

    critical = [v for v in violations if v.get("severity") == "CRITICAL"]
    major    = [v for v in violations if v.get("severity") == "MAJOR"]
    minor    = [v for v in violations if v.get("severity") == "MINOR"]

    lines = [
        f"# Cross-Book Continuity Audit — {today}",
        f"**Books audited:** {', '.join(f'Book {b}' for b in books_audited)}",
        f"**Chapters processed:** {chapter_count}",
        f"**Generated:** {datetime.now().isoformat()}",
        "",
        "## Summary",
        summary,
        "",
        f"## Violations: {len(violations)} total "
        f"({len(critical)} critical, {len(major)} major, {len(minor)} minor)",
        "",
    ]

    for sev, vlist in [("CRITICAL", critical), ("MAJOR", major), ("MINOR", minor)]:
        if vlist:
            lines.append(f"### {sev} ({len(vlist)})")
            for i, v in enumerate(vlist, 1):
                lines.extend([
                    f"**{i}. [{v.get('category', '?')}]** — Book {v.get('book', '?')}, {v.get('chapter', '?')}",
                    f"> {v.get('passage', '')}",
                    f"",
                    f"**Canon ref:** {v.get('canon_ref', 'N/A')}",
                    f"**Correction:** {v.get('correction', 'N/A')}",
                    "",
                ])

    if not violations:
        lines.append("**NO VIOLATIONS DETECTED** ✓")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Audit report written: {out_path}")
    return out_path


def append_summary_log(report_path: Path, violations: list, books: list):
    """Append one-liner to rolling summary log."""
    log_path = LOG_DIR / "AUDIT_SUMMARY.log"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    critical_count = sum(1 for v in violations if v.get("severity") == "CRITICAL")
    flag = "⚠ CRITICAL" if critical_count > 0 else ("⚠ " if violations else "✓")
    line = (f"{ts}  {flag}  Books={','.join(str(b) for b in books)}  "
            f"violations={len(violations)} (critical={critical_count})  "
            f"report={report_path.name}")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def notify_n8n_if_critical(violations: list, report_path: Path):
    """Post desktop alert via n8n if critical violations found."""
    critical = [v for v in violations if v.get("severity") == "CRITICAL"]
    if not critical:
        return

    try:
        requests.post(
            f"{N8N_BASE}/webhook/nightly-continuity-prep",
            json={
                "event":          "critical_violations",
                "critical_count": len(critical),
                "report_path":    str(report_path),
            },
            timeout=10,
        )
        logger.warning(f"{len(critical)} CRITICAL violations — n8n alert triggered")
    except Exception as e:
        logger.warning(f"Could not notify n8n of critical violations: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_audit(books: list[int], fast: bool = False, single_chapter: str = None) -> dict:
    logger.info("═" * 60)
    logger.info("  CROSS-BOOK CONTINUITY AUDIT")
    logger.info(f"  Books: {books}  |  Fast: {fast}")
    logger.info("═" * 60)

    # Load canon context
    ssot_text    = load_text(SSOT_PATH, 20000)
    dossier_text = load_dossiers()

    if not ssot_text:
        logger.warning(f"SSOT not found at {SSOT_PATH}")

    # Load chapters
    if single_chapter:
        chapter_path = Path(single_chapter)
        chapters = [{
            "book":     0,
            "filename": chapter_path.name,
            "path":     str(chapter_path),
            "text":     load_text(chapter_path),
            "chars":    chapter_path.stat().st_size if chapter_path.exists() else 0,
        }]
    else:
        chapters = []
        for b in books:
            chapters.extend(load_book_chapters(b))

    if not chapters:
        logger.warning("No chapters found to audit.")
        return {"violations": [], "summary": "No chapters found."}

    logger.info(f"Total chapters for audit: {len(chapters)}")

    # Build prompt
    prompt = build_audit_prompt(chapters, ssot_text, dossier_text)

    # Run audit
    result = {}
    try:
        logger.info("Sending to Nemotron via tool router...")
        result = run_nemotron_audit(prompt)
        logger.info(f"Nemotron audit complete: {len(result.get('violations', []))} violations")
    except Exception as e:
        logger.warning(f"Nemotron unavailable ({e}) — falling back to Ollama")
        try:
            result = run_ollama_audit(prompt)
            logger.info(f"Ollama audit complete: {len(result.get('violations', []))} violations")
        except Exception as e2:
            logger.error(f"All audit backends failed: {e2}")
            result = {"violations": [], "summary": f"Audit failed: {e2}"}

    violations = result.get("violations", [])

    # Write report
    report_path = write_audit_report(result, books, len(chapters))
    append_summary_log(report_path, violations, books)
    notify_n8n_if_critical(violations, report_path)

    result["report_path"] = str(report_path)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Cross-book continuity audit for The Nephilim Chronicles"
    )
    parser.add_argument("--books",   default="3,4,5",
                        help="Comma-separated book numbers to audit (default: 3,4,5)")
    parser.add_argument("--chapter", default="",
                        help="Audit a single chapter file instead of full books")
    parser.add_argument("--fast",    action="store_true",
                        help="Fast mode: reduce context — quicker but less thorough")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    books = [int(b.strip()) for b in args.books.split(",") if b.strip().isdigit()]

    result = run_audit(books, fast=args.fast, single_chapter=args.chapter or None)

    violations = result.get("violations", [])
    critical   = sum(1 for v in violations if v.get("severity") == "CRITICAL")

    print(f"\nAudit complete: {len(violations)} violations ({critical} critical)")
    print(f"Report: {result.get('report_path', 'N/A')}")

    if critical > 0:
        sys.exit(1)   # non-zero exit code flags CI/CD pipelines


if __name__ == "__main__":
    main()
