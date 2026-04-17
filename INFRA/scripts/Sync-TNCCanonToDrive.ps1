<#
.SYNOPSIS
    TNC Canon Bridge — Syncs Nephilim Chronicles canon files to Google Drive
    for shared access by Claude.ai and NotebookLM.

.DESCRIPTION
    Collects canon, prose, infrastructure, and reference files from multiple
    local paths on DESKTOP-SINGULA and syncs them to a Google Drive folder
    structure using rclone. Both Claude.ai (via google_drive_search/fetch)
    and NotebookLM (via Drive import) can then read from the same source.

    Requires: rclone (https://rclone.org) configured with a Google Drive remote.

.NOTES
    Kerman Gild Publishing — Auckland, New Zealand
    The Nephilim Chronicles: Team Book Two (Timbuktu)
    Created: 2026-03-06 | Author: Agent 1 (Claude.ai)

.PARAMETER DryRun
    Show what would be synced without making changes.

.PARAMETER Verbose
    Show detailed rclone output.

.PARAMETER Force
    Skip confirmation prompt.

.EXAMPLE
    .\Sync-TNCCanonToDrive.ps1
    .\Sync-TNCCanonToDrive.ps1 -DryRun
    .\Sync-TNCCanonToDrive.ps1 -Force -Verbose
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force
)

# ============================================================================
# CONFIGURATION — Edit these paths to match your SINGULA layout
# ============================================================================

# rclone remote name (set during `rclone config`)
$RcloneRemote = "gdrive"

# Google Drive destination folder
$DriveRoot = "TNC_Canon_Bridge"

# Local source paths on DESKTOP-SINGULA
$LocalPaths = @{
    # Primary project repository (nephilim-chronicles MCP path)
    MCP_Root    = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles"

    # Book 2 manuscript and analysis (Docker-mounted canon volume)
    Book2_Root  = "F:\Projects-cmodi.000\self-hosted-ai-starter-kit\data\TNC"

    # Claude.ai project exports (manually saved session outputs)
    Exports     = "F:\Projects-cmodi.000\TNC_Exports"
}

# ============================================================================
# FILE MANIFEST — What goes where in the Drive folder
# ============================================================================
#
# Each entry: @{ Source = "local path"; Dest = "Drive subfolder"; Filter = "pattern" }
#
# Drive structure:
#   TNC_Canon_Bridge/
#   ├── 01_CORE_CANON/           ← Series Bible, Constitution, SSOT
#   ├── 02_CHARACTER_DOSSIERS/   ← All character files
#   ├── 03_WORLDBUILDING/        ← Watcher tech, weapons, locations
#   ├── 04_BOOK2_PROSE/          ← Prologue + chapters (current drafts)
#   ├── 05_HEBREW_THEOLOGY/      ← Hebrew analysis, theological docs
#   ├── 06_BOOK1_REFERENCE/      ← Published manuscript, KDP files
#   ├── 07_INFRASTRUCTURE/       ← Cowork setup, agent prompts, drift log
#   └── 08_SESSION_NOTES/        ← Latest handoff docs only
#

$SyncManifest = @(

    # ── 01 CORE CANON ────────────────────────────────────────────────
    @{
        Source = "$($LocalPaths.MCP_Root)\CANON\SERIES_BIBLE.md"
        Dest   = "01_CORE_CANON"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\SSOT_v3_MASTER.md"
        Dest   = "01_CORE_CANON"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\CANON\SSOT_v3_MASTER.md"
        Dest   = "01_CORE_CANON"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\ANALYSIS\CONSTITUTION.md"
        Dest   = "01_CORE_CANON"
        Type   = "file"
    },
    @{
        # Session logs contain all canon update records (SESSION_CANON_*, SESSION_HANDOFF_*)
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\session_logs"
        Dest   = "01_CORE_CANON/canon_updates"
        Type   = "folder"
    },

    # ── 02 CHARACTER DOSSIERS ────────────────────────────────────────
    @{
        # CANON\dossiers contains PROTAGONIST, ANTAGONIST, NEPHILIM, WATCHER dossiers
        Source = "$($LocalPaths.MCP_Root)\CANON\dossiers"
        Dest   = "02_CHARACTER_DOSSIERS"
        Type   = "folder"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\THE_SIRENS_DOSSIER.md"
        Dest   = "02_CHARACTER_DOSSIERS"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\BEAST_VESSEL_DOSSIER.md"
        Dest   = "02_CHARACTER_DOSSIERS"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\integrated\INTELLIGENCE_ASSESSMENTS.md"
        Dest   = "02_CHARACTER_DOSSIERS"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\ENDGAME_FATES.md"
        Dest   = "02_CHARACTER_DOSSIERS"
        Type   = "file"
    },

    # ── 03 WORLDBUILDING ─────────────────────────────────────────────
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\MO_CHRA_SWORD_LORE.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\AZAZELS_PRISON_DUDAEL_ANTARCTICA.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\integrated\MARS_ANTARCTICA_INTEGRATION.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\THE_CYDONIA_REVELATION.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\ATMOSPHERIC_SCENES_MARS_ANTARCTICA.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\BEAST_SYSTEM_GEOPOLITICS.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\CANON\WATCHER_TECHNOLOGY.md"
        Dest   = "03_WORLDBUILDING"
        Type   = "file"
    },

    # ── 04 BOOK 2 PROSE ──────────────────────────────────────────────
    # Drafts live in the MCP repo at MANUSCRIPT\book_2\CHAPTERS\
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\CHAPTERS\PROLOGUE_SCENE1_TheFountainsOfTheDeep.md"
        Dest   = "04_BOOK2_PROSE"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\CHAPTERS\PROLOGUE_SCENE2_TheTowerAndTheThrone.md"
        Dest   = "04_BOOK2_PROSE"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\CHAPTERS\CHAPTER_01_TheTwentyNames_REVISED.md"
        Dest   = "04_BOOK2_PROSE"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\CHAPTERS\CHAPTER_02_DeadReckoning.md"
        Dest   = "04_BOOK2_PROSE"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\CHAPTERS\CHAPTER_03_TheCaptainsDomain.md"
        Dest   = "04_BOOK2_PROSE"
        Type   = "file"
    },

    # ── 05 HEBREW & THEOLOGY ─────────────────────────────────────────
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\ANALYSIS\GENESIS_10_8-9_HEBREW_ANALYSIS.md"
        Dest   = "05_HEBREW_THEOLOGY"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\superseded\THE_SECOND_WITNESS_CONFIRMED.md"
        Dest   = "05_HEBREW_THEOLOGY"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\superseded\THE_TWO_WITNESSES.md"
        Dest   = "05_HEBREW_THEOLOGY"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\WORLDBUILDING\THE_BRIDE_OF_CHRIST.md"
        Dest   = "05_HEBREW_THEOLOGY"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\superseded\WATCHER_RELEASE_TIMING_OPTIONS.md"
        Dest   = "05_HEBREW_THEOLOGY"
        Type   = "file"
    },

    # ── 06 BOOK 1 REFERENCE ──────────────────────────────────────────
    @{
        # Full Book 1 manuscript folder (chapters, KDP, front matter, images)
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_1"
        Dest   = "06_BOOK1_REFERENCE/early_drafts"
        Type   = "folder"
    },
    @{
        # If a standalone MANUSCRIPT.docx was exported from Claude.ai, place it in TNC_Exports
        Source = "$($LocalPaths.Exports)\NephilimChronicles_Book1_MANUSCRIPT.docx"
        Dest   = "06_BOOK1_REFERENCE"
        Type   = "file"
    },

    # ── 07 INFRASTRUCTURE ────────────────────────────────────────────
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\ANALYSIS\DRIFT_LOG.md"
        Dest   = "07_INFRASTRUCTURE"
        Type   = "file"
    },
    @{
        # Place TNC_Book2_Cowork_Setup.md and VSCode_Agent_Prompt_NephilimPage.md
        # in TNC_Exports after downloading from Claude.ai sessions
        Source = "$($LocalPaths.Exports)\TNC_Book2_Cowork_Setup.md"
        Dest   = "07_INFRASTRUCTURE"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.Exports)\VSCode_Agent_Prompt_NephilimPage.md"
        Dest   = "07_INFRASTRUCTURE"
        Type   = "file"
    },

    # ── 08 SESSION NOTES ─────────────────────────────────────────────
    # Latest handoffs from repo — update after each session
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\session_logs\SESSION_HANDOFF_06Mar2026_COPILOT.md"
        Dest   = "08_SESSION_NOTES"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\ARCHIVE\session_logs\SESSION_HANDOFF_06Mar2026_Session2.md"
        Dest   = "08_SESSION_NOTES"
        Type   = "file"
    },
    @{
        Source = "$($LocalPaths.MCP_Root)\MANUSCRIPT\book_2\SESSION_NOTES\CHAPTER_04_ARCHITECTURE_REVISED.md"
        Dest   = "08_SESSION_NOTES"
        Type   = "file"
    }
)

# ============================================================================
# SYNC ENGINE
# ============================================================================

function Test-Rclone {
    try {
        $null = & rclone version 2>&1
        return $true
    } catch {
        return $false
    }
}

function Test-RcloneRemote {
    param([string]$Remote)
    $remotes = & rclone listremotes 2>&1
    return ($remotes -match "^${Remote}:")
}

function Sync-Item {
    param(
        [string]$Source,
        [string]$Dest,
        [string]$Type,
        [switch]$DryRun
    )

    $drivePath = "${RcloneRemote}:${DriveRoot}/${Dest}"

    if (-not (Test-Path $Source)) {
        Write-Warning "  SKIP (not found): $Source"
        return @{ Status = "skipped"; Reason = "not found"; Path = $Source }
    }

    $rcloneArgs = @()

    if ($Type -eq "folder") {
        $rcloneArgs = @("sync", $Source, $drivePath)
    } else {
        # For single files, copy to the destination folder
        $rcloneArgs = @("copyto", $Source, "$drivePath/$(Split-Path $Source -Leaf)")
    }

    if ($DryRun) {
        $rcloneArgs += "--dry-run"
    }

    # Suppress noisy output unless verbose
    if (-not $PSCmdlet.MyInvocation.BoundParameters['Verbose']) {
        $rcloneArgs += "--quiet"
    }

    $rcloneArgs += "--stats-one-line"

    Write-Host "  $(if($DryRun){'[DRY RUN] '})$Type → $drivePath" -ForegroundColor $(if($DryRun){'Yellow'}else{'Green'})

    & rclone @rcloneArgs 2>&1 | ForEach-Object {
        if ($PSCmdlet.MyInvocation.BoundParameters['Verbose']) {
            Write-Verbose $_
        }
    }

    return @{ Status = "synced"; Path = $Source; Dest = $drivePath }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

$banner = @"

╔══════════════════════════════════════════════════════════════╗
║  TNC Canon Bridge — Google Drive Sync                       ║
║  Kerman Gild Publishing · Auckland, New Zealand             ║
║  "And they shall prophesy 1,260 days." — Revelation 11:3   ║
╚══════════════════════════════════════════════════════════════╝

"@

Write-Host $banner -ForegroundColor Cyan

# Pre-flight checks
if (-not (Test-Rclone)) {
    Write-Error @"
rclone not found. Install it first:
  winget install Rclone.Rclone
Then configure a Google Drive remote:
  rclone config
  → New remote → name: gdrive → type: drive → follow OAuth prompts
"@
    exit 1
}

if (-not (Test-RcloneRemote $RcloneRemote)) {
    Write-Error @"
rclone remote '$RcloneRemote' not configured.
Run: rclone config
  → New remote → name: $RcloneRemote → type: 18 (Google Drive)
  → Follow OAuth prompts → Verify with: rclone lsd ${RcloneRemote}:
"@
    exit 1
}

# Confirmation
if (-not $Force -and -not $DryRun) {
    Write-Host "This will sync $($SyncManifest.Count) items to ${RcloneRemote}:${DriveRoot}/" -ForegroundColor Yellow
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y') {
        Write-Host "Aborted." -ForegroundColor Red
        exit 0
    }
}

# Execute sync
Write-Host "`nSyncing $($SyncManifest.Count) items...`n" -ForegroundColor White

$results = @()
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($item in $SyncManifest) {
    $result = Sync-Item -Source $item.Source -Dest $item.Dest -Type $item.Type -DryRun:$DryRun
    $results += $result
}

$stopwatch.Stop()

# Summary
$synced  = ($results | Where-Object { $_.Status -eq "synced" }).Count
$skipped = ($results | Where-Object { $_.Status -eq "skipped" }).Count

Write-Host "`n────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Synced:  $synced" -ForegroundColor Green
Write-Host "  Skipped: $skipped" -ForegroundColor $(if($skipped -gt 0){'Yellow'}else{'Green'})
Write-Host "  Time:    $($stopwatch.Elapsed.TotalSeconds.ToString('F1'))s" -ForegroundColor DarkGray
Write-Host "────────────────────────────────────────`n" -ForegroundColor DarkGray

if ($skipped -gt 0) {
    Write-Host "Skipped files (not found at expected path):" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -eq "skipped" } | ForEach-Object {
        Write-Host "  $($_.Path)" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Update the paths in the `$SyncManifest section of this script," -ForegroundColor Yellow
    Write-Host "or create the TNC_Exports folder and copy files there first." -ForegroundColor Yellow
}

if ($DryRun) {
    Write-Host "[DRY RUN complete — no files were modified]" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to execute the sync.`n" -ForegroundColor Yellow
}