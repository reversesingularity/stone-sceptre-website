param()
$ErrorActionPreference = 'Stop'

$token   = gh auth token
$authHdr = @{ Authorization = "token $token"; Accept = "application/vnd.github+json" }
$repo    = "reversesingularity/stone-sceptre-website"
$base    = "https://api.github.com/repos/$repo/contents"
$website = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\WEBSITE"

function Push-File {
    param(
        [string]$LocalPath,
        [string]$RepoPath,
        [string]$CommitMessage,
        [bool]$Binary = $false
    )

    Write-Host "`n--- Pushing: $RepoPath ---"
    $apiUri = "$base/$RepoPath"

    # Get current SHA (null for new files)
    $fileSha = $null
    try {
        $existing = Invoke-RestMethod -Uri $apiUri -Headers $authHdr -ErrorAction Stop
        $fileSha  = $existing.sha
        Write-Host "  Existing SHA: $fileSha"
    } catch {
        Write-Host "  New file (no existing SHA)"
    }

    # Read and base64-encode content
    if ($Binary) {
        $bytes = [System.IO.File]::ReadAllBytes($LocalPath)
    } else {
        $text  = [System.IO.File]::ReadAllText($LocalPath, [System.Text.Encoding]::UTF8)
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    }
    $b64 = [Convert]::ToBase64String($bytes)

    # Build payload
    $payload = @{ message = $CommitMessage; content = $b64; branch = "main" }
    if ($fileSha) { $payload.sha = $fileSha }
    $body = $payload | ConvertTo-Json -Depth 5

    $resp = Invoke-RestMethod -Uri $apiUri -Method Put -Headers $authHdr -Body $body -ContentType "application/json"
    Write-Host "  Commit: $($resp.commit.sha)"
}

# ── 1. nephilim/index.html (updated: Book 3 in nav, teaser, footer) ────────────
Push-File `
    -LocalPath "$website\nephilim\index.html" `
    -RepoPath  "nephilim/index.html" `
    -CommitMessage "Add Book 3 (The Edenic Mandate) to Nephilim Book 1 page — nav, teaser, footer"

# ── 2. nephilim/book2/index.html (updated: Book 3 in nav, teaser, footer) ──────
Push-File `
    -LocalPath "$website\nephilim\book2\index.html" `
    -RepoPath  "nephilim/book2/index.html" `
    -CommitMessage "Add Book 3 (The Edenic Mandate) to Nephilim Book 2 page — nav, teaser, footer"

# ── 3. nephilim/book3/index.html (NEW) ─────────────────────────────────────────
Push-File `
    -LocalPath "$website\nephilim\book3\index.html" `
    -RepoPath  "nephilim/book3/index.html" `
    -CommitMessage "Add Nephilim Book 3 (The Edenic Mandate) landing page"

# ── 4. nephilim/book3/styles.css (NEW — copy of book2 styles) ──────────────────
Push-File `
    -LocalPath "$website\nephilim\book3\styles.css" `
    -RepoPath  "nephilim/book3/styles.css" `
    -CommitMessage "Add styles.css for Nephilim Book 3 page"

# ── 5. nephilim/book3/script.js (NEW — copy of book2 scripts) ──────────────────
Push-File `
    -LocalPath "$website\nephilim\book3\script.js" `
    -RepoPath  "nephilim/book3/script.js" `
    -CommitMessage "Add script.js for Nephilim Book 3 page"

# ── 6. nephilim/book3/images/book-cover.jpg (NEW — AI-upscaled cover) ──────────
Push-File `
    -LocalPath "$website\nephilim\book3\images\book-cover.jpg" `
    -RepoPath  "nephilim/book3/images/book-cover.jpg" `
    -CommitMessage "Add Book 3 cover image (AI-upscaled 1600x2560)" `
    -Binary $true

# ── 7. Root index.html (updated: Book 3 card + footer link) ────────────────────
Push-File `
    -LocalPath "$website\index.html" `
    -RepoPath  "index.html" `
    -CommitMessage "Add Nephilim Book 3 card and footer link to landing page"

Write-Host "`n=== All files deployed successfully! ==="
Write-Host "Live at: https://kermangildpublishing.org/nephilim/book3/"
