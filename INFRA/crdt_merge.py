"""
DESKTOP-SINGULA — CRDT Canon Merge Utility
===========================================
Implements Conflict-Free Replicated Data Type (CRDT)-inspired merge semantics
for the SSOT_v3_MASTER.md canon document.

Multiple async agents (Drift Manager, Theological Guard, Story Prototype Manager)
can propose canon updates simultaneously. This utility merges them without
file-locking or corrupting the document.

CRDT Rules Applied:
    SAFE      — Non-overlapping proposals: apply all (G-Set additive)
    ADDITIVE  — Same section, APPEND operation: append both chronologically
    CONFLICT  — Same section, MODIFY operation: route to LWW or escalate to Author
    DEPRECATE — Mark canon as superseded: safe if section not LOCKED

Usage:
    python crdt_merge.py [--staging-dir /path] [--dry-run] [--verbose]
    python crdt_merge.py --scan          # just scan and report pending proposals
"""

import os
import re
import sys
import json
import time
import shutil
import hashlib
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
SSOT_PATH     = PROJECT_ROOT / "CANON" / "SSOT_v3_MASTER.md"
TODO_PATH     = PROJECT_ROOT / "TODO.md"
ARCHIVE_DIR   = PROJECT_ROOT / "ARCHIVE" / "superseded"
CHANGES_LOG   = PROJECT_ROOT / "ARCHIVE" / "session_logs" / "CONSTITUTION_CHANGES.md"
STAGING_DIR   = PROJECT_ROOT / "STAGING" / "crdt_proposals"

# Section headers that are immutably LOCKED — no agent may modify these
LOCKED_SECTIONS = {
    "§1",   # Series Bible Constitutional Axioms
    "§2",   # The Acoustic Paradigm
    "§3",   # Timeline Lock
    "§4.2", # Raphael's Three Limitations
    "§5",   # Knowledge Transmission Chain
    "§9.1", # Empyreal Register
}

# Agents and their permitted operation types (deontic permissions)
AGENT_PERMISSIONS = {
    "AGENT_0":  {"APPEND", "MODIFY", "DEPRECATE"},   # Conductor — full
    "AGENT_2":  {"APPEND"},                           # Drift Manager — flag only
    "AGENT_3":  {"APPEND", "MODIFY", "DEPRECATE"},   # Constitution Updater — full
    "AGENT_8":  {"APPEND"},                           # Story Prototype — add only
    "AGENT_9":  {"APPEND"},                           # Theological Guard — flag only
    "AGENT_10": {"APPEND"},                           # Cross-Book Continuity — flag only
    "AGENT_11": {"APPEND"},                           # Self-Refine Scorer — flag only
    "ADAMEM":   {"APPEND", "MODIFY"},                 # AdaMem initializer
    "NEMOCLAW": {"APPEND"},                           # Daemon — add only
    "AUTHOR":   {"APPEND", "MODIFY", "DEPRECATE"},   # Chris — unrestricted
}

# Confidence for automated merges without author sign-off
SAFE_CONFIDENCE_LEVELS = {"CONFIRMED", "PROPOSED"}   # Do NOT auto-merge LOCKED triples


# ── Proposal Schema ───────────────────────────────────────────────────────────
#
# Proposal JSON file structure:
# {
#   "proposal_id": "AGENT_8_1712578200",
#   "agent_id": "AGENT_8",
#   "section": "§7.3 — Azazel's Release",
#   "operation": "APPEND",        // APPEND | MODIFY | DEPRECATE
#   "proposed_text": "...",
#   "confidence": "CONFIRMED",    // LOCKED | CONFIRMED | PROPOSED | INFERRED
#   "conflicts_with": [],
#   "timestamp": "ISO8601",
#   "source_chapter": "Book3_Ch4"  // optional provenance
# }

def load_proposals(staging_dir):
    """Load all pending .json proposal files from staging directory."""
    staging = Path(staging_dir)
    if not staging.exists():
        staging.mkdir(parents=True, exist_ok=True)
        return []

    proposals = []
    for f in sorted(staging.glob("proposal_*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
                data["_filepath"] = str(f)
                proposals.append(data)
        except Exception as e:
            print(f"  WARNING: Could not parse {f.name}: {e}")
    return proposals


def validate_proposal(proposal):
    """
    Validate a proposal against schema and permission rules.
    Returns (is_valid, reason_if_rejected).
    """
    required = {"agent_id", "section", "operation", "proposed_text",
                 "confidence", "timestamp"}
    missing = required - set(proposal.keys())
    if missing:
        return False, f"Missing required fields: {missing}"

    agent   = proposal["agent_id"]
    op      = proposal["operation"]
    conf    = proposal["confidence"]
    section = proposal["section"]

    # Check deontic permissions
    allowed_ops = AGENT_PERMISSIONS.get(agent, set())
    if op not in allowed_ops:
        return False, (f"Agent {agent} does not have permission for operation {op}. "
                       f"Allowed: {allowed_ops}")

    # LOCKED sections are immutable
    for locked_sec in LOCKED_SECTIONS:
        if section.startswith(locked_sec):
            return False, (f"Section '{section}' is LOCKED (matches {locked_sec}). "
                            "No agent may modify LOCKED sections.")

    # Agents cannot submit LOCKED confidence — that's an author privilege
    if conf == "LOCKED":
        return False, "Agents may not submit proposals with confidence=LOCKED."

    return True, None


# ── Conflict Classification ───────────────────────────────────────────────────

def classify_conflicts(proposals):
    """
    Classify a list of proposals into conflict categories.
    Returns {
      "safe": [proposals],       -- no section overlap
      "additive": [groups],      -- same section, all APPEND
      "conflict": [groups],      -- same section, has MODIFY
      "deprecate": [proposals],  -- DEPRECATE operations
    }
    """
    by_section = {}
    for p in proposals:
        sec = p["section"]
        by_section.setdefault(sec, []).append(p)

    result = {"safe": [], "additive": [], "conflict": [], "deprecate": []}

    for section, group in by_section.items():
        ops = {p["operation"] for p in group}

        deprecate_ps = [p for p in group if p["operation"] == "DEPRECATE"]
        modify_ps    = [p for p in group if p["operation"] == "MODIFY"]
        append_ps    = [p for p in group if p["operation"] == "APPEND"]

        if deprecate_ps:
            result["deprecate"].extend(deprecate_ps)
        if modify_ps:
            # MODIFY on same section = conflict, regardless of APPEND presence
            result["conflict"].append({"section": section, "proposals": modify_ps + append_ps})
        elif len(append_ps) == 1:
            result["safe"].extend(append_ps)
        elif len(append_ps) > 1:
            result["additive"].append({"section": section, "proposals": append_ps})
        elif not deprecate_ps:
            result["safe"].extend(group)

    return result


# ── SSOT Operations ───────────────────────────────────────────────────────────

def load_ssot(ssot_path):
    with open(ssot_path, encoding="utf-8") as f:
        return f.read()


def find_section_range(content, section_header):
    """
    Locate the start and end line indices of a named section in the SSOT.
    Returns (start_line, end_line) or (-1, -1) if not found.
    Section ends at the next same-level or higher heading.
    """
    lines = content.split("\n")
    # Determine heading level from section_header (e.g., "§7.3" = look for ## or ###)
    start_idx = -1
    for i, line in enumerate(lines):
        if section_header in line and line.startswith("#"):
            start_idx = i
            break
    if start_idx == -1:
        return -1, -1

    # Determine heading level
    heading_level = len(lines[start_idx]) - len(lines[start_idx].lstrip("#"))

    # Find the next heading of same or higher level
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.startswith("#"):
            this_level = len(line) - len(line.lstrip("#"))
            if this_level <= heading_level:
                end_idx = i
                break

    return start_idx, end_idx


def apply_append(content, section_header, text_to_append):
    """Append text at the end of a section."""
    lines = content.split("\n")
    start, end = find_section_range(content, section_header)

    if start == -1:
        # Section not found — append at document end with note
        content += f"\n\n<!-- CRDT APPEND: Section '{section_header}' not found — appended at end -->\n"
        content += text_to_append.strip() + "\n"
        return content

    # Insert before the next section heading (or at end)
    insert_pos = end - 1 if end < len(lines) else len(lines)
    lines.insert(insert_pos, "\n" + text_to_append.strip() + "\n")
    return "\n".join(lines)


def apply_modify(content, section_header, new_text):
    """Replace the body of a section with new_text."""
    lines = content.split("\n")
    start, end = find_section_range(content, section_header)

    if start == -1:
        return content  # Can't find section — no-op; will be escalated

    # Keep the heading line; replace everything else in the section
    heading_line = lines[start]
    before = lines[:start + 1]
    after  = lines[end:]
    middle = [new_text.strip()]
    return "\n".join(before + middle + after)


def apply_deprecate(content, section_header, reason=""):
    """Mark a section as deprecated with a notice."""
    notice = f"\n> **[DEPRECATED — {datetime.now().strftime('%Y-%m-%d')}]** {reason}\n"
    return apply_append(content, section_header, notice)


# ── Atomic Write ─────────────────────────────────────────────────────────────

def atomic_write(new_content, ssot_path, archive_dir):
    """
    Write SSOT atomically: temp file → validate → rename.
    Archives the old version before overwriting.
    """
    ssot_path   = Path(ssot_path)
    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)

    tmp_path = ssot_path.with_suffix(".md.tmp")

    # Write temp
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)

    # Validate: check word count and heading structure
    word_count  = len(new_content.split())
    heading_cnt = len([l for l in new_content.split("\n") if l.startswith("#")])

    original_word_count = len(load_ssot(ssot_path).split())
    if word_count < original_word_count * 0.5:
        tmp_path.unlink()
        raise ValueError(
            f"ATOMIC WRITE ABORTED: New content has only {word_count} words "
            f"vs original {original_word_count}. Possible truncation."
        )

    if heading_cnt < 3:
        tmp_path.unlink()
        raise ValueError(
            f"ATOMIC WRITE ABORTED: New content has only {heading_cnt} headings. "
            "Document structure may be broken."
        )

    # Archive old version
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = archive_dir / f"SSOT_v3_{ts}.md"
    shutil.copy2(ssot_path, archive_path)

    # Rename temp → target
    tmp_path.replace(ssot_path)

    return str(archive_path)


# ── Changes Log ───────────────────────────────────────────────────────────────

def log_merge(merge_report, changes_log_path):
    """Append a summary of the merge to the constitution changes log."""
    log_path = Path(changes_log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"\n## CRDT Merge — {ts}",
        f"- Proposals processed : {merge_report['total_proposals']}",
        f"- Merged (safe)       : {merge_report['merged_safe']}",
        f"- Merged (additive)   : {merge_report['merged_additive']}",
        f"- Escalated to Author : {merge_report['escalated']}",
        f"- Rejected            : {merge_report['rejected']}",
        f"- Archive path        : {merge_report.get('archive_path', 'N/A')}",
    ]
    if merge_report.get("escalated_sections"):
        lines.append(f"- Escalated sections  : {', '.join(merge_report['escalated_sections'])}")
    if merge_report.get("rejected_reasons"):
        for reason in merge_report["rejected_reasons"]:
            lines.append(f"  - REJECTED: {reason}")

    with open(log_path, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def escalate_to_author(conflict_group, todo_path):
    """Write a human-readable query to TODO.md for author resolution."""
    todo   = Path(todo_path)
    ts     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    section = conflict_group["section"]
    proposals = conflict_group["proposals"]

    lines = [
        f"\n## ⚠ CRDT CONFLICT — Author Decision Required [{ts}]",
        f"**Section:** `{section}`",
        f"**Conflict type:** Multiple MODIFY proposals cannot be auto-merged.",
        "",
        "**Proposals:**",
    ]
    for i, p in enumerate(proposals, 1):
        lines += [
            f"### Option {i} — from {p['agent_id']} ({p['timestamp']})",
            f"Confidence: `{p['confidence']}`",
            "```",
            textwrap.indent(p["proposed_text"][:800], "  "),
            "```",
        ]
    lines += [
        "",
        "**Required action:** Edit SSOT_v3_MASTER.md section directly and mark resolved.",
        "---",
    ]

    with open(todo, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


# ── Main Merge Pipeline ───────────────────────────────────────────────────────

def run_merge(staging_dir, dry_run=False, verbose=False):
    staging_dir = Path(staging_dir)
    print("\n" + "═" * 64)
    print("  CRDT MERGE — Constitution Updater v2.0")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE MERGE'}")
    print(f"  Staging: {staging_dir}")
    print("═" * 64)

    # 1. Load proposals
    proposals = load_proposals(staging_dir)
    if not proposals:
        print("\n  No pending proposals found. Nothing to merge.\n")
        return {"total_proposals": 0}

    print(f"\n  Loaded {len(proposals)} proposal(s)")

    # 2. Validate permissions
    valid, rejected = [], []
    for p in proposals:
        ok, reason = validate_proposal(p)
        if ok:
            valid.append(p)
        else:
            rejected.append({"proposal_id": p.get("proposal_id"), "reason": reason})
            print(f"  REJECTED: {p.get('agent_id')} — {reason}")

    print(f"  Valid: {len(valid)}  Rejected: {len(rejected)}")

    if not valid:
        print("  No valid proposals to process.\n")
        return {
            "total_proposals": len(proposals),
            "merged_safe": 0,
            "merged_additive": 0,
            "escalated": 0,
            "rejected": len(rejected),
            "rejected_reasons": [r["reason"] for r in rejected],
        }

    # 3. Classify conflicts
    classified = classify_conflicts(valid)
    if verbose:
        print(f"\n  Safe     : {len(classified['safe'])}")
        print(f"  Additive : {len(classified['additive'])}")
        print(f"  Conflict : {len(classified['conflict'])}")
        print(f"  Deprecate: {len(classified['deprecate'])}")

    # 4. Load SSOT
    content = load_ssot(SSOT_PATH)
    merged_safe = 0
    merged_additive = 0
    escalated = 0
    escalated_sections = []
    archive_path = None

    # 5. Apply SAFE (no-overlap APPEND/MODIFY)
    for p in classified["safe"]:
        op      = p["operation"]
        section = p["section"]
        text    = p["proposed_text"]
        if verbose:
            print(f"  [SAFE/{op}] {section}")
        if not dry_run:
            if op == "APPEND":
                content = apply_append(content, section, text)
            elif op == "MODIFY":
                content = apply_modify(content, section, text)
            merged_safe += 1
        else:
            merged_safe += 1

    # 6. Apply ADDITIVE (multi-agent APPENDs to same section)
    for group in classified["additive"]:
        section = group["section"]
        if verbose:
            print(f"  [ADDITIVE] {section} — {len(group['proposals'])} appends")
        if not dry_run:
            combined = "\n\n".join(p["proposed_text"] for p in
                                   sorted(group["proposals"], key=lambda x: x["timestamp"]))
            content = apply_append(content, section, combined)
            merged_additive += 1
        else:
            merged_additive += 1

    # 7. Apply DEPRECATE
    for p in classified["deprecate"]:
        section = p["section"]
        reason  = p.get("proposed_text", "")
        if verbose:
            print(f"  [DEPRECATE] {section}")
        if not dry_run:
            content = apply_deprecate(content, section, reason)

    # 8. Escalate CONFLICTS to Author
    for group in classified["conflict"]:
        section = group["section"]
        print(f"  [ESCALATE] Conflict in '{section}' — Author decision required")
        escalated_sections.append(section)
        escalated += 1
        if not dry_run:
            escalate_to_author(group, TODO_PATH)

    # 9. Atomic write
    if not dry_run and (merged_safe + merged_additive > 0):
        archive_path = atomic_write(content, SSOT_PATH, ARCHIVE_DIR)
        print(f"\n  ✓ SSOT written. Old version archived: {archive_path}")

    # 10. Clean up processed proposals (not escalated ones)
    if not dry_run:
        processed_files = set()
        for p in classified["safe"] + [p for g in classified["additive"]
                                         for p in g["proposals"]] + classified["deprecate"]:
            fp = p.get("_filepath")
            if fp:
                processed_files.add(fp)
        for fp in processed_files:
            try:
                Path(fp).unlink()
            except Exception:
                pass
        print(f"  Cleaned {len(processed_files)} proposal file(s) from staging")

    report = {
        "total_proposals":   len(proposals),
        "merged_safe":       merged_safe,
        "merged_additive":   merged_additive,
        "escalated":         escalated,
        "rejected":          len(rejected),
        "rejected_reasons":  [r["reason"] for r in rejected],
        "escalated_sections": escalated_sections,
        "archive_path":      archive_path,
        "timestamp":         datetime.now().isoformat(),
    }

    # 11. Log changes
    if not dry_run:
        log_merge(report, CHANGES_LOG)

    print("\n  ── Merge Summary ─────────────────────────────────────────")
    print(f"  Merged (safe)       : {merged_safe}")
    print(f"  Merged (additive)   : {merged_additive}")
    print(f"  Escalated to Author : {escalated}")
    print(f"  Rejected            : {len(rejected)}")
    if dry_run:
        print("\n  DRY RUN — no files modified.")
    print("═" * 64 + "\n")

    return report


def scan_staging(staging_dir):
    """Quick report on pending proposals without merging."""
    proposals = load_proposals(staging_dir)
    print(f"\n  Pending proposals in staging: {len(proposals)}")
    for p in proposals:
        ts       = p.get("timestamp", "?")[:19]
        agent    = p.get("agent_id", "?")
        op       = p.get("operation", "?")
        section  = p.get("section", "?")
        conf     = p.get("confidence", "?")
        print(f"    {ts}  [{agent:12s}]  {op:10s}  {section}  ({conf})")
    return proposals


def write_proposal(agent_id, section, operation, proposed_text,
                   confidence="PROPOSED", source_chapter=None,
                   staging_dir=None):
    """
    Utility function for other scripts to write a CRDT proposal.
    Returns the path of the written proposal file.
    """
    staging = Path(staging_dir or STAGING_DIR)
    staging.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_id = f"{agent_id}_{ts}"

    proposal = {
        "proposal_id":    proposal_id,
        "agent_id":       agent_id,
        "section":        section,
        "operation":      operation,
        "proposed_text":  proposed_text,
        "confidence":     confidence,
        "conflicts_with": [],
        "timestamp":      datetime.now().isoformat(),
        "source_chapter": source_chapter,
    }

    path = staging / f"proposal_{proposal_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(proposal, f, indent=2)

    return str(path)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CRDT Canon Merge — conflict-free SSOT_v3_MASTER.md updates"
    )
    parser.add_argument("--staging-dir", default=str(STAGING_DIR),
                        help="Directory containing proposal JSON files")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Preview merge without writing any files")
    parser.add_argument("--verbose",  action="store_true",
                        help="Print per-proposal decisions")
    parser.add_argument("--scan",     action="store_true",
                        help="Scan and report pending proposals without merging")
    args = parser.parse_args()

    if args.scan:
        scan_staging(args.staging_dir)
        return

    run_merge(args.staging_dir, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
