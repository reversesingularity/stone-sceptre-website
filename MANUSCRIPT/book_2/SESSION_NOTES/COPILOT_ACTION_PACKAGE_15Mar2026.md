# COPILOT ACTION PACKAGE — March 15, 2026
## The Nephilim Chronicles Book 2 — File, Correct, and Deploy
*Prepared by Agent 1 (Claude.ai) for GitHub Copilot (Project Structure Agent)*

---

## PURPOSE

This package contains every filing, correction, and deployment action from:
- The **March 15, 2026 creative session** (Ch4 draft, domain registry, canon corrections)
- The **March 15, 2026 rules session** (Boris Method workflow rules, project brain document)

Copilot should execute these in the order listed. Each action has a verification step.

---

## PRIORITY 1: FILE MISSING SESSION OUTPUTS

These two files were produced in the March 15 session but are NOT yet in the repository.
Chris: you will need to provide the file content to Copilot, or paste them from the
Claude.ai session that produced them.

### Action 1A: File Chapter 4 Draft
```
Source:    March 15 Claude.ai session output
Filename:  CHAPTER_04_TheSameWord.md
Dest:      MANUSCRIPT/book_2/CHAPTERS/CHAPTER_04_TheSameWord.md
Words:     ~5,539
Status:    First draft — author review pending before drift check
Verify:    File exists, four section headers present:
           I.   THE HEBREW BENEATH THE ENGLISH
           II.  THE ROOM AFTER
           III. THE WEIGHT OF AN HONEST QUESTION
           IV.  THE FILING CABINET
```
**COMPLETED by Copilot — March 15, 2026**

### Action 1B: File Watcher Domain Registry
```
Source:    March 15 Claude.ai session output
Filename:  WATCHER_DOMAIN_REGISTRY.md
Dest:      MANUSCRIPT/book_2/ANALYSIS/WATCHER_DOMAIN_REGISTRY.md
Words:     ~3,056
Status:    Draft — 3 domain assignments pending author confirmation
Verify:    File exists, 4 locked domains listed:
           Shemyaza = Italy, Gadreel = Antarctica,
           Tamiel = Peru, Kokabel = Central Africa
```
**BLOCKED — Content not provided. Chris must paste the file content from the Claude.ai session.**

---

## PRIORITY 2: CHAPTER 1 LEVANT CORRECTIONS (3 LINE EDITS)

**File:** `MANUSCRIPT/book_2/CHAPTERS/CHAPTER_01_TheTwentyNames_REVISED.md`

This is a **geographic canon error**. Shemyaza's domain is the Italian Peninsula
(his stele is beneath the Vatican), NOT the Levant. Three lines propagated this
error uncorrected.

### Action 2A: Line 212 — COMPLETED
```
FIND:    "the Levant"  (in the six-land-sites list)
REPLACE: "the Italian peninsula"
```

### Action 2B: Line 214 — COMPLETED
```
FIND:    "The Levant stele is Shemyaza's"
REPLACE: "The Italian stele is Shemyaza's"
```

### Action 2C: Line 476 — COMPLETED
```
FIND:    "Shemyaza in the Levant"
REPLACE: "Shemyaza in Italy"
```

### Verification — PASSED
Zero remaining Shemyaza-Levant references in the file. (One false positive:
"relevant" at line 438 — substring match only, not a geographic reference.)

---

## PRIORITY 3: FIRE CANON-UPDATE WEBHOOK

Two sessions' worth of NEW CANON blocks are pending deployment. Both must fire.

### Action 3A: March 6 NEW CANON (from SESSION_HANDOFF_06Mar2026.md)
```powershell
$headers = @{ "Content-Type" = "application/json" }
Invoke-WebRequest -Uri "http://localhost:5678/webhook/canon-update" `
  -Method POST -Headers $headers `
  -Body '{"session_note": "SESSION_HANDOFF_06Mar2026.md — see NEW CANON block"}' `
  -TimeoutSec 10
```

### Action 3B: March 15 NEW CANON (from SESSION_HANDOFF_15Mar2026.md)
```powershell
Invoke-WebRequest -Uri "http://localhost:5678/webhook/canon-update" `
  -Method POST -Headers $headers `
  -Body '{"session_note": "SESSION_HANDOFF_15Mar2026.md — see NEW CANON block"}' `
  -TimeoutSec 10
```

### New Canon Summary (March 15)
- Shemyaza domain = Italian Peninsula (geographic correction)
- Chapter 4 first draft complete (structure and content decisions)
- Watcher domain model clarified (stele = domain infrastructure, not binding locations)
- 4 locked domain assignments confirmed
- 2 pending domain assignments flagged (Armaros/Carpathians, Khem/Egypt)

### Verification
Check CONSTITUTION.md after webhook fires. New entries should appear.

---

## PRIORITY 4: FIRE DRIFT CHECKS

### Action 4A: Chapter 3 Drift Check
```powershell
# Confirm the 768-line version is in repo FIRST
$headers = @{ "Content-Type" = "application/json" }
$body = '{"chapter":"CHAPTER_03_TheCaptainsDomain.md"}'
Invoke-WebRequest "http://localhost:5678/webhook/drift-check" -Method POST -Headers $headers -Body $body
```
**Prerequisite:** Verify CHAPTER_03_TheCaptainsDomain.md in repo is the 768-line
version with the Liaigh archangel-reference fix applied (from March 6 session).

### Action 4B: Chapter 4 Drift Check
```powershell
$body = '{"chapter":"CHAPTER_04_TheSameWord.md"}'
Invoke-WebRequest "http://localhost:5678/webhook/drift-check" -Method POST -Headers $headers -Body $body
```
**Prerequisite:** Chapter 4 must be filed (Action 1A) AND author-reviewed first.

---

## PRIORITY 5: PROJECT RULES DEPLOYMENT

### Action 5A: Boris Method Workflow Rules — COMPLETED
```
Filename:  TNC_WORKFLOW_RULES.md
Dest:      MANUSCRIPT/book_2/ANALYSIS/TNC_WORKFLOW_RULES.md
```
Filed alongside CONSTITUTION.md in ANALYSIS/.

### Action 5B: Update CHAPTER_04_ARCHITECTURE_REVISED.md Status — COMPLETED
```
File:   MANUSCRIPT/book_2/SESSION_NOTES/CHAPTER_04_ARCHITECTURE_REVISED.md
Line 5: "*Status: FIRST DRAFT COMPLETE — Filed as CHAPTER_04_TheSameWord.md*"
```

---

## PRIORITY 6: SESSION HANDOFF FILING

### Action 6A: File This Action Package — COMPLETED
```
Filename:  COPILOT_ACTION_PACKAGE_15Mar2026.md
Dest:      MANUSCRIPT/book_2/SESSION_NOTES/COPILOT_ACTION_PACKAGE_15Mar2026.md
```

### Action 6B: Confirm SESSION_HANDOFF_15Mar2026.md is Filed
```
Verify:    SESSION_HANDOFF_15Mar2026.md exists in MANUSCRIPT/book_2/SESSION_NOTES/
```
**BLOCKED — File does not exist in repo. Chris must file from Claude.ai session.**

---

## CHECKLIST — Copilot Completion Tracker

| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1A | File CHAPTER_04_TheSameWord.md | 🔴 HIGH | ✅ DONE |
| 1B | File WATCHER_DOMAIN_REGISTRY.md | 🔴 HIGH | ⛔ BLOCKED — needs content |
| 2A | Ch1 line 212 Levant → Italian peninsula | 🔴 HIGH | ✅ DONE |
| 2B | Ch1 line 214 Levant stele → Italian stele | 🔴 HIGH | ✅ DONE |
| 2C | Ch1 line 476 Levant → Italy | 🔴 HIGH | ✅ DONE |
| 2V | Verify zero Shemyaza-Levant refs remain | 🔴 HIGH | ✅ DONE |
| 3A | Fire canon-update webhook (March 6) | 🟡 MEDIUM | ☐ Needs SINGULA running |
| 3B | Fire canon-update webhook (March 15) | 🟡 MEDIUM | ⛔ BLOCKED — SESSION_HANDOFF_15Mar2026.md missing |
| 3V | Verify CONSTITUTION.md updated | 🟡 MEDIUM | ☐ Pending webhook |
| 4A | Fire Ch3 drift check (768-line version) | 🟡 MEDIUM | ☐ Needs SINGULA running |
| 4B | Fire Ch4 drift check (after author review) | 🟡 MEDIUM | ☐ Needs author review first |
| 5A | Deploy TNC_WORKFLOW_RULES.md | 🟡 MEDIUM | ✅ DONE |
| 5B | Update Ch4 architecture status line | 🟢 LOW | ✅ DONE |
| 6A | File this action package | 🟢 LOW | ✅ DONE |
| 6B | Confirm handoff filed | 🟢 LOW | ⛔ BLOCKED — file missing |

---

## BLOCKING NOTES FOR COPILOT

- **Actions 1A and 1B** require Chris to provide the file content from the
  Claude.ai session that produced them — they are NOT in the project files.
  Copilot cannot generate these; only file them.
- **Action 4B** (Ch4 drift check) is gated on **Action 1A** (filing the draft)
  AND Chris completing his author review.
- **SINGULA services must be running** for Actions 3A, 3B, 4A, 4B.
  Run `SINGULA-LAUNCH.ps1` first if needed.
- **API key SINGULA-TNC expires 2026-04-27** (~43 days). Flag for renewal
  before next month's sessions.

---

*Kerman Gild Publishing · Auckland, New Zealand · The Nephilim Chronicles*
