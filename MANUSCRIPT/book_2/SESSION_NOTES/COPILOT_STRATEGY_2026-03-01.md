# GitHub Copilot — Division of Labour Strategy
## The Nephilim Chronicles Book 2 Production
*Prepared by GitHub Copilot (Claude Sonnet 4.6) — March 1, 2026*
*Handoff document for Claude.ai (Agent 1 — Content Creator)*

---

## Context

This document records the agreed division of labour across the four-platform 
production stack for TNC Book 2. It was prepared during the ingestion window 
while `ingest_jubilees.py` was processing (~34,721 vectors; ~52,742 total 
projected in Qdrant `nephilim_chronicles` collection).

The Cowork Setup Guide (`TNC_Book2_Cowork_Setup.md`) was designed around 
Claude Desktop as the VS Code seat. GitHub Copilot now occupies that seat 
instead — with direct file access, terminal control, and workspace awareness. 
This changes the division of labour for infrastructure tasks.

---

## Platform Roles (Updated)

### GitHub Copilot (VS Code — DESKTOP-SINGULA)
**Always on. Requires active VS Code session.**

This is the **infrastructure engineer and file manager** for the project. 
It has direct read/write access to the entire workspace and can run terminal 
commands, making it faster and more reliable than any agent for file operations.

**Handles:**
- All Python script fixes and maintenance (`build_manuscript.py`, 
  `ingest_jubilees.py`, `canon_search_api.py`, `kdp_format_server.py`)
- PowerShell infrastructure (`SINGULA-LAUNCH.ps1`, `RUN-INGESTION.ps1`)
- Scaffolding new files and folder structures directly into the workspace
- Firing n8n webhooks from terminal and interpreting results
- Checking Qdrant vector counts and collection health
- Canon file search via grep across all workspace files
- Session log creation and maintenance (`ARCHIVE/session_logs/`)
- Patching canon files for simple, targeted additions
- Debugging any component of the SINGULA stack

**Does NOT handle:**
- Primary creative writing (that's Agent 1 / Claude.ai)
- `.xlsx` output (requires Cowork Agents 4, 5)
- `.docx` read/write for KDP QC (requires Cowork Agent 7)
- Long uninterrupted manuscript analysis sessions (use Cowork)
- Empyreal register dialogue (use Claude.ai)

---

### Claude.ai — Agent 1 (Content Creator)
**Browser-based. Project memory. Primary creative seat.**

This is where the book gets written. All theology, character development, 
plot architecture, Raphael's empyreal register, and canon decisions originate 
here. GitHub Copilot then handles the file/infrastructure consequences of 
those decisions.

**Handles:**
- All Chapter drafting
- Canon decisions (tagged `### NEW CANON — [Date]`)
- Theological consistency reasoning
- Character voice (especially Liaigh/Raphael empyreal register)
- Plot architecture across the 5-book structure
- Brainstorming and world-building development

**After each Claude.ai session:**
1. Export session notes → GitHub Copilot saves them to 
   `MANUSCRIPT/book_2/SESSION_NOTES/SESSION_[DATE].md`
2. Fire `canon-update` webhook for routine NEW CANON blocks (n8n)
3. Complex canon restructuring → Cowork Agent 3

---

### Claude Desktop (Cowork) — Agents 2–8
**Async specialist analysts. Run independently on completed chapters.**

These agents run after chapters are drafted — they do not block writing. 
They are invoked per-chapter or per-batch, not per-session.

| Agent | Role | Output Format | When to Run |
|-------|------|---------------|-------------|
| Agent 2 — Drift Manager | Continuity audit | Markdown report → `DRIFT_LOG.md` | Per chapter (HIGH severity only — use n8n for routine) |
| Agent 3 — Constitution Updater | Canon integration (complex) | Updated canon files | When n8n can't handle restructuring |
| Agent 4 — Reader Matrix Analyst | Reader response scoring | `.xlsx` → `ANALYSIS/` | Weekly or per chapter batch |
| Agent 5 — Dopamine Ladder | Engagement/hook mapping | `.xlsx` → `ANALYSIS/` | Weekly or per chapter batch |
| Agent 6 — Image Prompt Designer | Chapter illustration prompts | Markdown → `IMAGE_PROMPTS/` | Per chapter when draft is final |
| Agent 7 — KDP Formatter | DOCX assembly QC | `.docx` → `KDP/` | End of manuscript only |
| Agent 8 — Combat Doctrine Specialist | Combat sequence audit | Markdown reports → `COMBAT_DOCTRINE/` | Per chapter containing combat |

**GitHub Copilot vs Cowork Agent 3 (Canon Updates):**
- **Routine** NEW CANON additions → n8n `canon-update` webhook (zero cost)
- **Targeted** file additions (single section, known location) → GitHub Copilot directly
- **Complex** restructuring, conflict resolution, multi-file coordination → Cowork Agent 3

---

### n8n (SINGULA Automation Layer)
**Background. Zero cost. Zero supervision. Docker on DESKTOP-SINGULA.**

| Workflow | ID | Trigger | Purpose |
|----------|----|---------|---------|
| DRIFT_MANAGER | `DriftMgrTNCBook2` | `POST /webhook/drift-check` | Routine drift detection via Mistral + Qdrant |
| CONSTITUTION_UPDATER | `ConstitutionUpdaterTNC` | `POST /webhook/canon-update` | NEW CANON block integration into CONSTITUTION.md |
| KDP_FORMATTER | `KdpFormatterTNC` | `POST /webhook/kdp-format` | Triggers `build_manuscript.py` → DOCX output |

---

## Recommended Per-Session Workflow

```
WRITE ──────────────────────── Claude.ai (Agent 1)
         │
         ▼
SAVE SESSION NOTES ─────────── GitHub Copilot saves file directly
         │
         ▼
FIRE CANON UPDATE ──────────── n8n webhook (routine NEW CANON)
   OR  ─────────────────────── Cowork Agent 3 (complex restructuring)
         │
         ▼
PUSH CHAPTER FILE ──────────── GitHub Copilot scaffolds/saves to CHAPTERS/
         │
         ▼
COMBAT AUDIT ───────────────── Cowork Agent 8 (async)
DRIFT CHECK ────────────────── n8n routine, OR Cowork Agent 2 (HIGH severity)
IMAGE PROMPTS ──────────────── Cowork Agent 6 (async)
         │
         ▼
WEEKLY: READER MATRIX ──────── Cowork Agent 4
        DOPAMINE LADDER ─────── Cowork Agent 5
         │
         ▼
END OF BOOK: KDP BUILD ─────── n8n KDP_FORMATTER webhook → DOCX
             KDP QC ─────────── Cowork Agent 7
```

---

## Infrastructure Changes Made This Session (March 1, 2026)

### 1. `build_manuscript.py` — Env Var Override Fix
**Lines 24–25 updated** to read `KDP_MANUSCRIPT_DIR` and `KDP_OUTPUT_FILE` 
from environment variables, with existing hardcoded paths as fallbacks. 
This enables the `kdp-format` n8n webhook to build Book 2 DOCX without 
hardcode changes.

```python
# Usage for Book 2:
# $env:KDP_MANUSCRIPT_DIR = "...\MANUSCRIPT\book_2\CHAPTERS"
# $env:KDP_OUTPUT_FILE    = "...\NephilimChronicles_Book2_MANUSCRIPT.docx"
# python build_manuscript.py
```

### 2. Combat Doctrine Scaffolding
All 5 Agent 8 reference files created under `MANUSCRIPT/book_2/COMBAT_DOCTRINE/`:
- `WEAPONS_REGISTRY.md` — pre-populated with full Book 1 canon loadout
- `TACTICAL_GLOSSARY.md` — stub, ready for Agent 8 population
- `ERA_TRANSITIONS.md` — stub, ready for Agent 8 population
- `DUDAEL_OPS_BRIEF.md` — stub, ready for Agent 8 population

---

## Deferred Items (Status as of March 1, 2026)

| Priority | Item | Status | Owner |
|----------|------|--------|-------|
| HIGH | Jubilees ingestion (`ingest_jubilees.py`) | ⏳ Running | Auto (SINGULA) |
| MED | Verify Qdrant count post-ingestion | ⏳ Pending completion | GitHub Copilot |
| MED | Test Jubilees queries via Canon Search API | ⏳ Pending completion | GitHub Copilot |
| MED | n8n API key renewal (expires 2026-04-27) | ⚠️ Not done | Chris (manual) |
| LOW | Book 2 Chapter 1 entry point decision | 🔴 Open — blocks drafting | Claude.ai (Agent 1) |

---

## Canon Quick Reference for Book 2 Opening

**Timeline context:**
- October 2026 — Titan-1 launches to Mars (Book 1 Epilogue end point)
- Book 2 opens from this point forward

**Three candidate Chapter 1 openers (unresolved):**
1. Miriam on Titan-1 — new setting, immediate curiosity hook, separates her from Cian
2. Cian in Iceland — familiar POV anchor, risk of feeling like Book 1 restart
3. Parallel opening — cinematic tension split, confusion risk in Ch1

This decision should be made in Claude.ai before drafting begins, then 
tagged `### NEW CANON` and fired through the `canon-update` webhook.

---

*Document prepared by GitHub Copilot (Claude Sonnet 4.6)*
*For handoff to Claude.ai Agent 1 — Content Creator*
*Next review: After Chapter 1 first draft complete*
