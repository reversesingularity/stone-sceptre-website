# NEPHILIM CHRONICLES — FOLDER REORGANIZATION COMMANDS
## Execute in VS Code Terminal or PowerShell
**Generated:** February 6, 2026

---

## IMPORTANT: BACKUP FIRST!

Before running any commands, create a backup:

```powershell
# Create backup of entire project
$backupPath = "C:\Users\$env:USERNAME\Documents\nephilim-backup-$(Get-Date -Format 'yyyy-MM-dd')"
Copy-Item -Path "PATH_TO_YOUR_PROJECT" -Destination $backupPath -Recurse
Write-Host "Backup created at: $backupPath"
```

---

## STEP 1: CREATE NEW FOLDER STRUCTURE

```powershell
# Navigate to your project root
cd "PATH_TO_YOUR_PROJECT"

# Create new folders
New-Item -ItemType Directory -Path "CANON" -Force
New-Item -ItemType Directory -Path "CANON\dossiers" -Force
New-Item -ItemType Directory -Path "MANUSCRIPT" -Force
New-Item -ItemType Directory -Path "MANUSCRIPT\book_1" -Force
New-Item -ItemType Directory -Path "WORLDBUILDING" -Force
New-Item -ItemType Directory -Path "REFERENCE" -Force
New-Item -ItemType Directory -Path "ARCHIVE" -Force
New-Item -ItemType Directory -Path "ARCHIVE\session_logs" -Force
New-Item -ItemType Directory -Path "ARCHIVE\superseded" -Force
New-Item -ItemType Directory -Path "ARCHIVE\integrated" -Force
New-Item -ItemType Directory -Path ".github" -Force

Write-Host "Folder structure created!"
```

---

## STEP 2: MOVE SESSION LOGS TO ARCHIVE

```powershell
# Move all session logs
Move-Item -Path "SESSION_BRAINSTORM.md" -Destination "ARCHIVE\session_logs\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "SESSION_LOG_JAN22_2026.md" -Destination "ARCHIVE\session_logs\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "SESSION_LOG_JAN_19-21_2026.md" -Destination "ARCHIVE\session_logs\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "SESSION_SUMMARY_JAN7-9_2026.md" -Destination "ARCHIVE\session_logs\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "SESSION_CANON_2026-01-19.md" -Destination "ARCHIVE\session_logs\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "SESSION_JAN20-30_CONFLICTS_ANALYSIS" -Destination "ARCHIVE\session_logs\" -Force -ErrorAction SilentlyContinue

# Move obsolete handoff doc
Move-Item -Path "CLAUDE_SESSION_HANDOFF.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue

Write-Host "Session logs archived!"
```

---

## STEP 3: MOVE SUPERSEDED DOCUMENTS

```powershell
# Move old SSOT
Move-Item -Path "SSOT_v2" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue

# Move revision/addition files (content should be in source docs)
Move-Item -Path "CANON_REVISIONS_JAN_2026.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "NEW_CANON_JANUARY_5_2026.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "APPENDIX_UPDATES.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "APPLIED_README.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "WATCHER_DOSSIER_REVISIONS.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "WATCHER_DOSSIER_GADREEL_UPDATE.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "NEPHILIM_DOSSIERS_REVISIONS.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "GADREEL_EVE_INCIDENT.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "AZAZEL_NEPHILIM_DOSSIER_N004.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "BEAST_IDENTITY_INVESTIGATION.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "THE_SECOND_WITNESS_CONFIRMED.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "THE_TWO_WITNESSES.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "WATCHER_RELEASE_TIMING_OPTIONS.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CYDONIA_ASSESSMENT.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue

# Move ADDITIONS files (after extracting content to SSOT)
Move-Item -Path "SERIES_BIBLE_ADDITIONS.md" -Destination "ARCHIVE\integrated\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "SERIES_BIBLE_ADDITIONS_1.md" -Destination "ARCHIVE\integrated\" -Force -ErrorAction SilentlyContinue

Write-Host "Superseded documents archived!"
```

---

## STEP 4: ORGANIZE CANON FOLDER

```powershell
# Move/copy core canon documents
# NOTE: SSOT_v3_MASTER.md and dossiers should be placed in CANON after creation
Move-Item -Path "SERIES_BIBLE" -Destination "CANON\SERIES_BIBLE.md" -Force -ErrorAction SilentlyContinue
Move-Item -Path "WATCHER_DOSSIERS.md" -Destination "CANON\dossiers\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "NEPHILIM_DOSSIERS.md" -Destination "CANON\dossiers\" -Force -ErrorAction SilentlyContinue

# After creating new dossiers, place them here:
# CANON\SSOT_v3_MASTER.md
# CANON\dossiers\PROTAGONIST_DOSSIERS.md
# CANON\dossiers\ANTAGONIST_DOSSIERS.md

Write-Host "Canon folder organized!"
```

---

## STEP 5: ORGANIZE MANUSCRIPT FOLDER

```powershell
# Move active manuscript files
Move-Item -Path "BOOK_1_PROLOGUE.md" -Destination "MANUSCRIPT\book_1\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CHAPTER_01_THE_AWAKENING.md" -Destination "MANUSCRIPT\book_1\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CHAPTER_02_THE_HUNTER.md" -Destination "MANUSCRIPT\book_1\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CHAPTER_03_THE_COORDINATES_v3_2" -Destination "MANUSCRIPT\book_1\CHAPTER_03_THE_COORDINATES.md" -Force -ErrorAction SilentlyContinue
Move-Item -Path "BOOK_1_CHAPTER_OUTLINE.md" -Destination "MANUSCRIPT\book_1\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "BOOK_1_EPILOGUE_THE_DIGGING_BEGINS.md" -Destination "MANUSCRIPT\book_1\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "BOOK_1_CHAPTERS_4-9_FRAMEWORK.md" -Destination "MANUSCRIPT\book_1\" -Force -ErrorAction SilentlyContinue

# Archive older chapter versions
Move-Item -Path "CHAPTER_03_THE_COORDINATES.md" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CHAPTER_03_THE_COORDINATES_v2_1" -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue

Write-Host "Manuscript folder organized!"
```

---

## STEP 6: ORGANIZE WORLDBUILDING FOLDER

```powershell
# Move narrative/scene documents
Move-Item -Path "THE_CYDONIA_REVELATION.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "ATMOSPHERIC_SCENES_MARS_ANTARCTICA.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "AZAZELS_PRISON_DUDAEL_ANTARCTICA.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "ENDGAME_FATES.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "THE_BRIDE_OF_CHRIST.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "INTELLIGENCE_ASSESSMENTS.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "MO_CHRA_SWORD_LORE.md" -Destination "WORLDBUILDING\" -Force -ErrorAction SilentlyContinue

# Move character source files to integrated (after extraction to dossiers)
Move-Item -Path "LORD_VARCOLAC_DOSSIER.md" -Destination "ARCHIVE\integrated\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "MIRIAM_ASHFORD_UPDATED.md" -Destination "ARCHIVE\integrated\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "THE_SIRENS_DOSSIER.md" -Destination "ARCHIVE\integrated\" -Force -ErrorAction SilentlyContinue

Write-Host "Worldbuilding folder organized!"
```

---

## STEP 7: ORGANIZE REFERENCE FOLDER

```powershell
# Move technical/reference documents
Move-Item -Path "TECHNICAL_REFERENCE_MARS_MISSION.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "VISUAL_DIRECTION.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "FIVE_BOOK_STRUCTURE.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "BEAST_SYSTEM_GEOPOLITICS.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "STRATEGIC_DEPLOYMENT_MARS_ANTARCTICA.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CONSTITUTIONAL_AMENDMENT_MARS_ANTARCTICA.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "MARS_ANTARCTICA_INTEGRATION.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "BEAST_VESSEL_DOSSIER.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "CANON_AMENDMENT_ANTI-SINGULARITY_ACOUSTIC_PARADIGM.md" -Destination "REFERENCE\" -Force -ErrorAction SilentlyContinue

Write-Host "Reference folder organized!"
```

---

## STEP 8: HANDLE DUPLICATE/EXTENSION-LESS FILES

```powershell
# These files appear to be duplicates without .md extension
# Review them first, then archive if duplicates

# Check if these are duplicates:
# ANTAGONISTS, CIAN_MAC_MORNA, CYDONIA_ASSESSMENT, ELIJAH_THE_PROPHET
# INTELLIGENCE_ASSESSMENTS, MIRIAM_ASHFORD, NEPHILIM_DOSSIERS
# SERIES_BIBLE, SESSION_BRAINSTORM, THE_ANGEL, THE_BRIDE_OF_CHRIST
# THE_CYDONIA_REVELATION, THE_SECOND_WITNESS_CONFIRMED, THE-SIRENS-DOSSIER
# WATCHER_DOSSIER, BOOK_1_PROLOGUE, CHAPTER_01_THE_AWAKENING
# CHAPTER_03_THE_COORDINATES_v2_1, CHAPTER_03_THE_COORDINATES_v3_2
# BEAST_IDENTITY_INVESTIGATION, Cian_s_Gear, SSOT_v2

# After confirming duplicates, archive them:
$extensionlessFiles = @(
    "ANTAGONISTS",
    "CIAN_MAC_MORNA", 
    "CYDONIA_ASSESSMENT",
    "ELIJAH_THE_PROPHET",
    "MIRIAM_ASHFORD",
    "THE_ANGEL",
    "THE-SIRENS-DOSSIER",
    "WATCHER_DOSSIER",
    "Cian_s_Gear"
)

foreach ($file in $extensionlessFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "ARCHIVE\superseded\" -Force -ErrorAction SilentlyContinue
        Write-Host "Archived: $file"
    }
}

Write-Host "Extension-less files reviewed!"
```

---

## STEP 9: CREATE COPILOT INSTRUCTIONS FILE

Save this content to `.github/copilot-instructions.md`:

```powershell
$copilotInstructions = @'
# NEPHILIM CHRONICLES — VS Code Copilot Instructions

## CANON AUTHORITY HIERARCHY
1. **SERIES_BIBLE.md** — Constitution (INVIOLABLE)
2. **SSOT_v3_MASTER.md** — Consolidated factual canon
3. **Dossiers** — Character/entity details
4. **Book outlines** — Plot structure

**RULE:** If any document contradicts SSOT_v3, SSOT_v3 prevails.

## CRITICAL CANON FACTS (VERIFY BEFORE WRITING)
- Cian commissioned: **586 BCE** (not 200 BC, not 628 BC)
- Azazel is **NEPHILIM** (son of Gadreel), NOT a Watcher
- Asael ≠ Azazel (different entities)
- Miriam was **TARGET** of SRA, NOT survivor
- Miriam has **NO CONNECTION** to Niamh's bloodline
- Liaigh **IS** Raphael (same entity)

## RAPHAEL'S THREE LIMITATIONS
| Limitation | Rule |
|------------|------|
| THE BAN | Cannot intervene against mortal humans |
| HEAVENLY LITURGY | Unavailable 9-10 AM, 3-4 PM; Sabbath; High Holy Days |
| NAME CONSEQUENCE | If Cian learns true name, direct communication ends |

## EMPYREAL REGISTER (MANDATORY FOR ANGELS)
- Pronouns: Thee, thou, thy, thine
- Vocabulary: Elevated, archaic, formal
- Proclamations: ALL CAPS
- Contractions: NEVER

## ACOUSTIC PARADIGM
All supernatural technology operates through SOUND/VIBRATION, not visual means.
God SPOKE creation into being. Stone has memory.

## FILE ORGANIZATION
- **CANON/** — SSOT, Series Bible, Dossiers
- **MANUSCRIPT/** — Active chapters
- **WORLDBUILDING/** — Scene/story reference
- **REFERENCE/** — Technical specs
- **ARCHIVE/** — Historical only

## PRE-DRAFT CHECKLIST
Before writing ANY scene:
- [ ] Character ages/states match SSOT_v3
- [ ] Timeline placement correct
- [ ] Raphael's limitations respected
- [ ] Empyreal Register for angelic dialogue
- [ ] No contradictions with locked canon
'@

$copilotInstructions | Out-File -FilePath ".github\copilot-instructions.md" -Encoding utf8

Write-Host "Copilot instructions created!"
```

---

## STEP 10: VERIFY FINAL STRUCTURE

```powershell
# Display final folder structure
Write-Host "`n=== FINAL FOLDER STRUCTURE ===" -ForegroundColor Green
Get-ChildItem -Recurse -Directory | Select-Object FullName

Write-Host "`n=== FILES BY FOLDER ===" -ForegroundColor Green
Get-ChildItem -Recurse -File | Group-Object DirectoryName | ForEach-Object {
    Write-Host "`n$($_.Name):" -ForegroundColor Cyan
    $_.Group | ForEach-Object { Write-Host "  - $($_.Name)" }
}
```

---

## EXPECTED FINAL STRUCTURE

```
NEPHILIM_CHRONICLES/
├── .github/
│   └── copilot-instructions.md
├── CANON/
│   ├── SSOT_v3_MASTER.md
│   ├── SERIES_BIBLE.md
│   └── dossiers/
│       ├── WATCHER_DOSSIERS.md
│       ├── NEPHILIM_DOSSIERS.md
│       ├── PROTAGONIST_DOSSIERS.md
│       └── ANTAGONIST_DOSSIERS.md
├── MANUSCRIPT/
│   └── book_1/
│       ├── BOOK_1_PROLOGUE.md
│       ├── CHAPTER_01_THE_AWAKENING.md
│       ├── CHAPTER_02_THE_HUNTER.md
│       ├── CHAPTER_03_THE_COORDINATES.md
│       ├── BOOK_1_CHAPTER_OUTLINE.md
│       ├── BOOK_1_EPILOGUE_THE_DIGGING_BEGINS.md
│       └── BOOK_1_CHAPTERS_4-9_FRAMEWORK.md
├── WORLDBUILDING/
│   ├── THE_CYDONIA_REVELATION.md
│   ├── INTELLIGENCE_ASSESSMENTS.md
│   ├── MO_CHRA_SWORD_LORE.md
│   ├── ATMOSPHERIC_SCENES_MARS_ANTARCTICA.md
│   ├── AZAZELS_PRISON_DUDAEL_ANTARCTICA.md
│   ├── ENDGAME_FATES.md
│   └── THE_BRIDE_OF_CHRIST.md
├── REFERENCE/
│   ├── TECHNICAL_REFERENCE_MARS_MISSION.md
│   ├── VISUAL_DIRECTION.md
│   ├── FIVE_BOOK_STRUCTURE.md
│   ├── BEAST_SYSTEM_GEOPOLITICS.md
│   ├── BEAST_VESSEL_DOSSIER.md
│   ├── STRATEGIC_DEPLOYMENT_MARS_ANTARCTICA.md
│   ├── CONSTITUTIONAL_AMENDMENT_MARS_ANTARCTICA.md
│   ├── MARS_ANTARCTICA_INTEGRATION.md
│   └── CANON_AMENDMENT_ANTI-SINGULARITY_ACOUSTIC_PARADIGM.md
└── ARCHIVE/
    ├── session_logs/
    │   ├── SESSION_BRAINSTORM.md
    │   ├── SESSION_LOG_*.md
    │   └── SESSION_JAN20-30_CONFLICTS_ANALYSIS
    ├── superseded/
    │   ├── SSOT_v2
    │   ├── CLAUDE_SESSION_HANDOFF.md
    │   ├── *_REVISIONS.md files
    │   └── older chapter versions
    └── integrated/
        ├── SERIES_BIBLE_ADDITIONS.md
        ├── LORD_VARCOLAC_DOSSIER.md
        ├── MIRIAM_ASHFORD_UPDATED.md
        └── THE_SIRENS_DOSSIER.md
```

---

## MAINTENANCE RULES (PREVENT FUTURE DRIFT)

### After EVERY Writing Session:
1. New canon → Update SSOT immediately
2. Character state changes → Update relevant dossier
3. Session logs → `/ARCHIVE/session_logs/` directly

### GOLDEN RULE:
**NEVER create files named:**
- `*_ADDITIONS.md`
- `*_UPDATED.md`
- `*_REVISIONS.md`
- `*_v2.md` (without archiving v1)

**ALWAYS edit the source document directly.**

### The SSOT is a living document. Feed it constantly.

---

*End of FOLDER_REORGANIZATION_COMMANDS.md*
