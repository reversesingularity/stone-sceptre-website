param()
$ErrorActionPreference = 'Stop'

$token   = gh auth token
$authHdr = @{ Authorization = "token $token"; Accept = "application/vnd.github+json" }
$repo    = "reversesingularity/nephilim-chronicles"
$base    = "https://api.github.com/repos/$repo/contents"
$local   = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles"

function Push-File {
    param(
        [string]$LocalPath,
        [string]$RepoPath,
        [string]$CommitMessage
    )

    Write-Host "`n--- Pushing: $RepoPath ---"
    $apiUri = "$base/$RepoPath"

    # Get current SHA
    $fileSha = $null
    try {
        $existing = Invoke-RestMethod -Uri $apiUri -Headers $authHdr -ErrorAction Stop
        $fileSha  = $existing.sha
        Write-Host "  Existing SHA: $fileSha"
    } catch {
        Write-Host "  New file (no existing SHA)"
    }

    # Read and encode
    $text  = [System.IO.File]::ReadAllText($LocalPath, [System.Text.Encoding]::UTF8)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $b64   = [Convert]::ToBase64String($bytes)

    # Build payload
    $payload = @{ message = $CommitMessage; content = $b64; branch = "main" }
    if ($fileSha) { $payload.sha = $fileSha }
    $body = $payload | ConvertTo-Json -Depth 5

    $resp = Invoke-RestMethod -Uri $apiUri -Method Put -Headers $authHdr -Body $body -ContentType "application/json"
    Write-Host "  Commit: $($resp.commit.sha)"
}

# ── Push governance documents ────────────────────────────────────────────────────
Push-File `
    -LocalPath "$local\AUTHOR_TASK_LIST.md" `
    -RepoPath  "AUTHOR_TASK_LIST.md" `
    -CommitMessage "Update AUTHOR_TASK_LIST: AUDIOBOOK_ASSEMBLER pipeline deployed v2.2 (May 4, 2026)"

Push-File `
    -LocalPath "$local\TODO.md" `
    -RepoPath  "TODO.md" `
    -CommitMessage "Update TODO: AUDIOBOOK_ASSEMBLER pipeline complete (May 4, 2026)"

Push-File `
    -LocalPath "$local\N8N_AGENT_WIRING.md" `
    -RepoPath  "N8N_AGENT_WIRING.md" `
    -CommitMessage "N8N_AGENT_WIRING v2.2: Agent 15 + WF15 AUDIOBOOK_ASSEMBLER documented"

Push-File `
    -LocalPath "$local\governance.py" `
    -RepoPath  "governance.py" `
    -CommitMessage "governance: add AGENT_15 permissions (audiobook_assemble)"

Push-File `
    -LocalPath "$local\Start-TNCSwarm.ps1" `
    -RepoPath  "Start-TNCSwarm.ps1" `
    -CommitMessage "Start-TNCSwarm: add port 8776 audiobook_prep_server to \$Services"

Push-File `
    -LocalPath "$local\n8n_deploy_workflows.py" `
    -RepoPath  "n8n_deploy_workflows.py" `
    -CommitMessage "n8n: add WF15 AUDIOBOOK_ASSEMBLER + audiobook_prep to PYTHON_SERVICES"

Push-File `
    -LocalPath "$local\conductor_server.py" `
    -RepoPath  "conductor_server.py" `
    -CommitMessage "conductor: register audiobook_assemble task type + intent fallback"

Push-File `
    -LocalPath "$local\CANON\PHONETIC_GLOSSARY.md" `
    -RepoPath  "CANON/PHONETIC_GLOSSARY.md" `
    -CommitMessage "CANON: add PHONETIC_GLOSSARY.md (60+ IPA + plain-English entries for TTS)"

Push-File `
    -LocalPath "$local\INFRA\agents\audiobook_prep_server.py" `
    -RepoPath  "INFRA/agents/audiobook_prep_server.py" `
    -CommitMessage "INFRA: add audiobook_prep_server.py port 8776 (4-stage audiobook pipeline)"

Write-Host "`n=== Governance documents synced to GitHub ==="
