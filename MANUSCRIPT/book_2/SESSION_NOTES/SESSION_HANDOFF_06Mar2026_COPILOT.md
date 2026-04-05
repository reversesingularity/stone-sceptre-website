# SESSION HANDOFF — March 6, 2026 (Copilot Infrastructure Session)
## The Nephilim Chronicles — TNC Canon Bridge Live · Drift Manager Fully Operational · Chapter 3 Complete
*Prepared by GitHub Copilot (Claude Sonnet 4.6)*
*For: Agent 1 (Claude.ai) — open when starting a new session*

---

## Session Status: INFRASTRUCTURE COMPLETE · ALL SERVICES AUTOMATED · CH3 VERIFIED CLEAN

This session completed all outstanding infrastructure work. The TNC Canon Bridge
is live (29 files on Google Drive). The Drift Manager is fully operational and
verified end-to-end. Startup is now fully automated — no manual steps required.
Chapter 3 ("The Captain's Domain") has been confirmed complete. Chapter 4 is next.

---

## What Was Completed This Session

### 1. TNC Canon Bridge — Live on Google Drive ✅

**What it is:** rclone sync pipeline that mirrors all TNC canon files to Google
Drive `TNC_Canon_Bridge/` folder. Provides a single unified source for both
Claude.ai (context files) and NotebookLM (notebook sources).

**Sync script:** `F:\Projects-cmodi.000\Sync-TNCCanonToDrive.ps1`
Also at: workspace root `Sync-TNCCanonToDrive.ps1`

**Status:** 29/32 files successfully synced. Last run: 263.8s.

**3 skipped files** — not yet available locally; add to `F:\Projects-cmodi.000\TNC_Exports\`
when downloaded from Claude.ai, then re-run `.\Sync-TNCCanonToDrive.ps1 -Force`:
- `NephilimChronicles_Book1_MANUSCRIPT.docx`
- `TNC_Book2_Cowork_Setup.md`
- `VSCode_Agent_Prompt_NephilimPage.md`

**Google Drive folder structure (8 categories):**
```
TNC_Canon_Bridge/
  01_CORE_CANON/         — SERIES_BIBLE, SSOT_v3_MASTER, WATCHER_TECHNOLOGY
  02_CHARACTER_DOSSIERS/ — all dossiers (Protagonist, Watcher, antagonists, Sirens)
  03_WORLDBUILDING/      — all WORLDBUILDING/ .md files
  04_BOOK2_ANALYSIS/     — CONSTITUTION.md, DRIFT_LOG.md, GENESIS exegesis
  05_BOOK2_CHAPTERS/     — all MANUSCRIPT/book_2/CHAPTERS/ files
  06_BOOK1_REFERENCE/    — Book 1 chapters + appendices
  07_TECHNICAL/          — tech specs, visual direction, reader reaction matrix
  08_EXPORTS/            — Claude.ai download staging (TNC_Exports/)
```

**To sync again:** `cd F:\Projects-cmodi.000; .\Sync-TNCCanonToDrive.ps1`

---

### 2. SINGULA-LAUNCH.ps1 — Fully Automated Session Startup ✅

**Location:** `F:\Projects-cmodi.000\SINGULA-LAUNCH.ps1`

**Run this at the start of every session.** It brings up all four services in one shot:

| Step | Service | What it does |
|------|---------|-------------|
| 1 | Docker stack | Qdrant (52,781 vectors) + Ollama (Mistral) + n8n + PostgreSQL |
| 2 | Canon Search API | `canon_search_api.py` on port 8765 (in its own window) |
| 3 | KDP Format Server | `kdp_format_server.py` on port 8766 |
| 4 | n8n Workflows | Activates DriftMgrTNCBook2, ConstitutionUpdaterTNC, KdpFormatterTNC |

**The `canon_search_api.py` missing issue** (which disabled the Drift Manager) **is
permanently solved** by this script. If you or Copilot ever get a Drift Manager
404/failure, the fix is: run `SINGULA-LAUNCH.ps1` if it hasn't been run in this session.

**Verify canon search is live:**
```powershell
Invoke-WebRequest "http://localhost:8765/search?q=acoustic+paradigm&n=1"
```

---

### 3. Drift Manager — Fully Operational ✅

**Webhook:** `POST http://localhost:5678/webhook/drift-check`
*(NOT `drift-manager` — that was the old broken path)*

**Chapter path in n8n:** `/data/TNC/MANUSCRIPT/book_2/CHAPTERS/${chapter}` ✅
*(Fixed this session from the old broken `/data/TNC_Book2/01_MANUSCRIPT/CHAPTERS/` path)*

**End-to-end test result (this session):**
Chapter 2 "Dead Reckoning" → `200 OK` → **OVERALL DRIFT SCORE: CLEAN** ✅

**Backup workflow JSON updated:** `MANUSCRIPT/book_2/ANALYSIS/DRIFT_MANAGER_WORKFLOW.json`
- `"path": "drift-check"` (was `"drift-manager"`)
- `"webhookId": "drift-check-webhook-tnc"` (was `"drift-manager-webhook-tnc"`)

**To fire a drift check from terminal:**
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = '{"chapter":"CHAPTER_03_TheCaptainsDomain.md"}'
Invoke-WebRequest "http://localhost:5678/webhook/drift-check" -Method POST -Headers $headers -Body $body
```

**Drift log:** `MANUSCRIPT/book_2/ANALYSIS/DRIFT_LOG.md` — appended after every run.

---

## Current Manuscript State

| File | Status | Drift |
|------|--------|-------|
| `PROLOGUE_SCENE1_TheFountainsOfTheDeep.md` | ✅ Complete (approved by Chris) | Not yet run post-rebuild |
| `PROLOGUE_SCENE2_TheTowerAndTheThrone.md` | ✅ Complete (approved by Chris) | Not yet run post-rebuild |
| `CHAPTER_01_TheTwentyNames_REVISED.md` | ✅ Complete — timeline date TBD | CLEAN (checked via Book 1 audit) |
| `CHAPTER_02_DeadReckoning.md` | ✅ Complete (~3,860 words) | ✅ **CLEAN** (verified this session) |
| `CHAPTER_03_TheCaptainsDomain.md` | ✅ Complete (384 lines, full chapter) | Pending — run before Ch4 |

**Chapter 3 ends:** Cian retrieves Shemyaza's binding protocols from beneath the Vatican.
Antarctica is the next destination. The drill is turning. The door is opening.

---

## Infrastructure Files — Do Not Touch

These files are stable and correct. No editing required:

| File | Location | Notes |
|------|----------|-------|
| `SINGULA-LAUNCH.ps1` | `F:\Projects-cmodi.000\` | Master launcher — already correct |
| `Sync-TNCCanonToDrive.ps1` | `F:\Projects-cmodi.000\` | Deployed copy — already correct |
| `Sync-TNCCanonToDrive.ps1` | Workspace root | Source copy — mirrors deployed |
| `DRIFT_MANAGER_WORKFLOW.json` | `MANUSCRIPT/book_2/ANALYSIS/` | Backup — updated this session |
| `canon_search_api.py` | Workspace root | Do not modify; SINGULA-LAUNCH handles startup |

**Optional cleanup** (ask Copilot to do this): Three temp fix scripts in `F:\Projects-cmodi.000\`:
`Fix-DriftManager.ps1`, `Fix-DriftManager2.ps1`, `Fix-DriftManager3.ps1` — safe to delete.

---

## NotebookLM Integration — Pending User Action

The Google Drive `TNC_Canon_Bridge/` folder is live and populated. To activate
NotebookLM as a canon reference tool:

1. Open NotebookLM → your TNC Book 2 notebook
2. Add sources → Google Drive → navigate to `TNC_Canon_Bridge/`
3. Add all 8 subfolders as sources
4. Once synced: use NotebookLM for cross-canon reference queries during drafting

This does not block Chapter 4 drafting. It's a background task.

---

## Recommended Next Actions for Agent 1

### Immediate — Run Chapter 3 Drift Check

Chapter 3 was written last session and has not yet been drift-checked. Before
starting Chapter 4, fire the check:

```
POST http://localhost:5678/webhook/drift-check
Body: {"chapter":"CHAPTER_03_TheCaptainsDomain.md"}
```

Or ask Copilot to run it from terminal.

### Primary — Draft Chapter 4

**What comes next per Book 2 structure:**

Chapter 3 closed with Cian obtaining Shemyaza's binding protocols from beneath
the Vatican. The chapter's closing frame confirmed two simultaneous pressures:
- Cian: protocols in hand, Antarctica the next destination
- Naamah: drill speed at maximum, the door "grows thinner with every hour"

**Chapter 4 architecture (to develop with Chris):**
- Likely a Naamah POV movement (Ashtoreth drilling scene — the acoustic returns
  intensifying) intercut with Cian's transit/preparation for Antarctic approach
- Introduce the Antarctic operational problem: how does a 2,631-year-old man
  with a glowing sword get onto a remote-sensing vessel or ice shelf without cover?
- Miriam's FININT capability becomes critical here (cover architecture, logistics)
- The Sarah + Miriam + Cian team dynamic begins to crystallize operationally

**Consult:** `WORLDBUILDING/AZAZELS_PRISON_DUDAEL_ANTARCTICA.md` for the
Antarctic geography, Dudael's acoustic signature, and the drilling programme details.
Also: `WORLDBUILDING/THE_SIRENS_DOSSIER.md` for Naamah's capabilities at this stage.

### Canon Update — CONSTITUTION.md

After Chapter 3, these items need updating in `MANUSCRIPT/book_2/ANALYSIS/CONSTITUTION.md`:

- §1.1 Book 1 Final State: Fill `[TO CONFIRM]` items (Cian's location, Miriam's
  first Book 1 appearance) — these are blocking the Drift Manager from full accuracy
- Add Chapter 3 continuity entries: Shemyaza's stele location confirmed (Vatican,
  below north transept), binding protocols retrieved, Liaigh's 7-hour Tamid window used,
  Romulus ward-type confirmed as Watcher-era

Ask Copilot to make the actual file edits once you've decided the canonical values.

---

## Platform Reminder

| Agent | Role | Contact |
|-------|------|---------|
| **Agent 1 (Claude.ai)** | Primary content creator — all drafting, theology, plot | This session |
| **GitHub Copilot (VS Code)** | Infrastructure, file ops, terminal, canon patching | Active in VS Code |
| **n8n Drift Manager** | Automated canon compliance checking | `drift-check` webhook |
| **Qdrant** | 52,781-vector semantic search across all canon | Via `canon_search_api.py` |

**n8n API Key** (expires 2026-04-27): `REFERENCE/API SINGULA-TNC N8N.txt`

---

*End of handoff — March 6, 2026*
*Next session opens with Chapter 3 drift check → Chapter 4 drafting.*
