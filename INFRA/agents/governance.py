"""
Governance Layer — The Nephilim Chronicles v2.0
================================================
Implements three concerns:

1. AUDIT LOGGER
   Every tool invocation across the swarm is logged with:
   agent_id, tool_name, args_summary, result_summary, timestamp
   → Append-only JSONL log at LOGS/agent_audit.jsonl

2. DEONTIC TOKEN ENFORCEMENT
   Import AGENT_PERMISSIONS from crdt_merge.py and enforce
   at the governance gate before high-risk operations execute.

3. PIMMUR COMPLIANCE CHECKER
   Six-criteria heuristic audit of drafting prompts:
   Profile diversity, authentic Interaction, persistent Memory,
   Minimal-Control prompts, Unawareness of experiment, Realism

Usage as library:
    from governance import log_invocation, check_permission, pimmur_check

Usage as CLI (PIMMUR check):
    python governance.py --check-prompt /path/to/prompt.txt

Usage as CLI (view audit log):
    python governance.py --show-audit [--last N]
    python governance.py --show-audit --agent AGENT_0
"""

import os
import sys
import json
import logging
import logging.handlers
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
LOG_DIR       = PROJECT_ROOT / "LOGS"
LOG_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_LOG     = LOG_DIR / "agent_audit.jsonl"
PIMMUR_LOG    = LOG_DIR / "pimmur_checks.jsonl"
TODO_PATH     = PROJECT_ROOT / "TODO.md"

# Import AGENT_PERMISSIONS from crdt_merge if available; else define inline.
try:
    sys.path.insert(0, str(PROJECT_ROOT))
    from crdt_merge import AGENT_PERMISSIONS, LOCKED_SECTIONS
except ImportError:
    LOCKED_SECTIONS = {"§1", "§2", "§3", "§4.2", "§5", "§9.1"}
    AGENT_PERMISSIONS = {
        "AGENT_0":  {"APPEND", "MODIFY", "DEPRECATE"},
        "AGENT_2":  {"APPEND"},
        "AGENT_3":  {"APPEND", "MODIFY", "DEPRECATE"},
        "AGENT_8":  {"APPEND"},
        "AGENT_9":  {"APPEND"},
        "AGENT_10": {"APPEND"},
        "AGENT_11": {"APPEND"},
        "AGENT_13": {"APPEND"},   # Marketing Content Agent — sabbath-aware
        "AUTHOR":   {"APPEND", "MODIFY", "DEPRECATE", "DELETE"},
    }

# HITL (Human-in-the-loop) gate: operations that require AUTHOR approval
HITL_REQUIRED_OPERATIONS = {
    "deprecate_canon_section",
    "delete_ssot_section",
    "modify_locked_section",
    "publish_manuscript",
    "push_to_kdp",
    "wipe_qdrant_collection",
    "override_locked_triple",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [GOVERNANCE] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("governance")

# Rotating JSONL loggers — max 10 MB per file, 10 backups (110 MB ceiling each)
def _make_jsonl_logger(name: str, path: Path) -> logging.Logger:
    handler = logging.handlers.RotatingFileHandler(
        str(path), maxBytes=10 * 1024 * 1024, backupCount=10, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    lg = logging.getLogger(name)
    lg.addHandler(handler)
    lg.setLevel(logging.DEBUG)
    lg.propagate = False
    return lg

_audit_logger  = _make_jsonl_logger("audit_jsonl",  AUDIT_LOG)
_pimmur_logger = _make_jsonl_logger("pimmur_jsonl", PIMMUR_LOG)


# ── 1. Audit Logger ───────────────────────────────────────────────────────────

def log_invocation(
    agent_id: str,
    tool_name: str,
    args: dict,
    result: dict | str | None,
    status: str = "success",   # "success" | "denied" | "error"
    extra: dict | None = None,
) -> str:
    """
    Append one audit entry to LOGS/agent_audit.jsonl.
    Returns the entry_id (sha256 of content) for correlation.
    """
    ts = datetime.utcnow().isoformat() + "Z"

    # Truncate large args/results to keep log manageable
    args_summary   = _truncate(args, 512)
    result_summary = _truncate(result, 512)

    entry = {
        "ts":             ts,
        "agent_id":       agent_id,
        "tool":           tool_name,
        "args_summary":   args_summary,
        "result_summary": result_summary,
        "status":         status,
    }
    if extra:
        entry["extra"] = extra

    entry_id = hashlib.sha256(
        json.dumps(entry, sort_keys=True).encode()
    ).hexdigest()[:16]
    entry["entry_id"] = entry_id

    _audit_logger.info(json.dumps(entry))

    if status in ("denied", "error"):
        logger.warning(f"[{agent_id}] {tool_name} {status.upper()}: {result_summary}")
    else:
        logger.debug(f"[{agent_id}] {tool_name} logged (id={entry_id})")

    return entry_id


def _truncate(obj, max_len: int = 512):
    """Safely truncate any value to a fixed string length."""
    if obj is None:
        return None
    if isinstance(obj, (dict, list)):
        s = json.dumps(obj, ensure_ascii=False)
    else:
        s = str(obj)
    if len(s) > max_len:
        return s[:max_len] + "…"
    return s


# ── 2. Deontic Permission Enforcement ────────────────────────────────────────

class PermissionDeniedError(PermissionError):
    pass


def check_permission(agent_id: str, operation: str, section: str = "") -> bool:
    """
    Return True if agent_id is permitted to perform `operation`.
    Raises PermissionDeniedError if denied (when raise_on_deny=True).
    Also blocks locked-section writes regardless of agent permissions.

    operation must be one of: APPEND, MODIFY, DEPRECATE, DELETE
    section is a §-prefixed SSOT section identifier (checked against LOCKED_SECTIONS)
    """
    # 1. HITL gate
    if operation.lower() in HITL_REQUIRED_OPERATIONS and agent_id != "AUTHOR":
        reason = f"Operation '{operation}' requires AUTHOR approval (HITL gate)"
        _escalate_hitl(agent_id, operation, section, reason)
        raise PermissionDeniedError(reason)

    # 2. Locked section guard
    if section and section in LOCKED_SECTIONS:
        reason = f"Section '{section}' is LOCKED — no agent may modify it"
        raise PermissionDeniedError(reason)

    # 3. Deontic permission check
    allowed = AGENT_PERMISSIONS.get(agent_id.upper(), set())
    if not isinstance(allowed, set):
        allowed = set(allowed)

    if operation.upper() not in allowed and "AUTHOR" not in allowed:
        reason = (f"Agent '{agent_id}' has no permission for '{operation}'. "
                  f"Allowed: {sorted(allowed)}")
        raise PermissionDeniedError(reason)

    return True


def gate(agent_id: str, operation: str, section: str = "") -> bool:
    """
    Convenience wrapper: logs both successful and denied checks.
    Returns True if permitted, False if denied (never raises).
    """
    try:
        check_permission(agent_id, operation, section)
        log_invocation(agent_id, f"gate:{operation}", {"section": section}, "permitted")
        return True
    except PermissionDeniedError as e:
        log_invocation(agent_id, f"gate:{operation}", {"section": section},
                       str(e), status="denied")
        return False


def _escalate_hitl(agent_id, operation, section, reason):
    """Write HITL escalation to TODO.md for human review."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## HITL GATE — {ts}\n"
        f"- **Agent:** {agent_id}\n"
        f"- **Operation:** {operation}\n"
        f"- **Section:** {section or 'N/A'}\n"
        f"- **Reason:** {reason}\n"
        f"- **Action required:** AUTHOR must review and manually approve or deny.\n"
    )
    with open(TODO_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    logger.warning(f"HITL escalation written to TODO.md: {reason}")


# ── 3. PIMMUR Compliance Checker ──────────────────────────────────────────────
#
# PIMMUR = Profile diversity, authentic Interaction, persistent Memory,
#          Minimal-Control prompts, Unawareness of experiment, Realism
#
# This checks prompts/story content heuristically for compliance issues.

PIMMUR_CRITERIA = {
    "profile_diversity": {
        "description": "Characters represent diverse cultural/ethnic backgrounds accurately",
        "keywords_fail": ["all white", "all male", "monoculture"],
        "weight": 1,
    },
    "authentic_interaction": {
        "description": "Dialogue and interaction feels organic, not scripted or expository",
        "keywords_fail": ["as you know, Bob", "this is convenient", "explain your powers"],
        "weight": 1,
    },
    "persistent_memory": {
        "description": "Characters remember prior events; no amnesia across scenes",
        "keywords_fail": [],
        "weight": 1,
    },
    "minimal_control": {
        "description": "AI prompts are not meta-prescriptive; no 'write exactly like X' over-specification",
        "keywords_fail": ["write exactly", "copy the style of", "imitate verbatim"],
        "weight": 1,
    },
    "unawareness_of_experiment": {
        "description": "Characters do not behave as if they know they are in a story",
        "keywords_fail": ["this is just a story", "in this narrative", "as a character, I"],
        "weight": 1,
    },
    "realism": {
        "description": "Internal logic is consistent; cause/effect respected even in supernatural scenes",
        "keywords_fail": ["impossible even for magic", "breaks all established rules"],
        "weight": 1,
    },
}


def pimmur_check(
    text: str,
    agent_id: str = "unknown",
    context: str = "",
) -> dict:
    """
    Run a heuristic PIMMUR compliance check on prompt text or story prose.

    Returns:
    {
        "overall": "PASS" | "WARN" | "FAIL",
        "criteria": {criterion_id: {"status": "pass"|"warn", "notes": str}},
        "issues": [str],
    }
    """
    text_lower = text.lower()
    criteria_results = {}
    issues = []

    for cid, cdef in PIMMUR_CRITERIA.items():
        status = "pass"
        notes  = ""

        for kw in cdef.get("keywords_fail", []):
            if kw.lower() in text_lower:
                status = "warn"
                notes  = f"Keyword detected: '{kw}'"
                issues.append(f"[{cid.upper()}] {notes}")
                break

        criteria_results[cid] = {"status": status, "notes": notes or cdef["description"]}

    warn_count = sum(1 for r in criteria_results.values() if r["status"] == "warn")
    overall = "PASS" if warn_count == 0 else ("WARN" if warn_count <= 2 else "FAIL")

    result = {
        "overall":  overall,
        "criteria": criteria_results,
        "issues":   issues,
        "agent_id": agent_id,
        "context":  context[:100] if context else "",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Log to PIMMUR_LOG
    _pimmur_logger.info(json.dumps(result))

    if overall != "PASS":
        logger.warning(f"PIMMUR {overall} ({warn_count} issues): {issues}")
    else:
        logger.debug(f"PIMMUR PASS for agent={agent_id}")

    return result


# ── Audit Log Reader ──────────────────────────────────────────────────────────

def read_audit_log(last_n: int = 20, agent_id: str = None) -> list[dict]:
    """Read recent entries from the audit log."""
    if not AUDIT_LOG.exists():
        return []

    entries = []
    with open(AUDIT_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if agent_id and e.get("agent_id", "").upper() != agent_id.upper():
                    continue
                entries.append(e)
            except json.JSONDecodeError:
                pass

    return entries[-last_n:]


def format_audit_table(entries: list[dict]) -> str:
    if not entries:
        return "(no audit entries)"
    lines = [f"{'Timestamp':<26} {'Agent':<10} {'Tool':<28} {'Status':<10} ID"]
    lines.append("─" * 90)
    for e in entries:
        lines.append(
            f"{e.get('ts',''):<26} "
            f"{e.get('agent_id',''):<10} "
            f"{e.get('tool',''):<28} "
            f"{e.get('status',''):<10} "
            f"{e.get('entry_id','')}"
        )
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Governance layer CLI — audit logs, permissions, PIMMUR checks"
    )
    parser.add_argument("--check-prompt", metavar="FILE",
                        help="Run PIMMUR compliance check on a text file")
    parser.add_argument("--show-audit",   action="store_true",
                        help="Print recent audit log entries")
    parser.add_argument("--last",  type=int, default=20, help="Number of entries to show")
    parser.add_argument("--agent", default="",           help="Filter by agent ID")
    parser.add_argument("--check-permission", nargs=2, metavar=("AGENT", "OP"),
                        help="Test if AGENT has permission for OP (e.g. AGENT_2 MODIFY)")
    args = parser.parse_args()

    if args.check_prompt:
        p = Path(args.check_prompt)
        if not p.exists():
            print(f"ERROR: File not found: {p}")
            sys.exit(1)
        text = p.read_text(encoding="utf-8")
        result = pimmur_check(text, agent_id="CLI", context=p.name)
        print(json.dumps(result, indent=2))
        if result["overall"] == "FAIL":
            sys.exit(1)

    elif args.show_audit:
        entries = read_audit_log(last_n=args.last, agent_id=args.agent or None)
        print(format_audit_table(entries))

    elif args.check_permission:
        agent, op = args.check_permission
        try:
            check_permission(agent, op)
            print(f"✓ PERMITTED: {agent} → {op}")
        except PermissionDeniedError as e:
            print(f"✗ DENIED: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
