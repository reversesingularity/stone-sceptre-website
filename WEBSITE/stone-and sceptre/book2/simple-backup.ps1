# Simple Web App Backup Script
param(
    [string]$BackupPath = "C:\Users\cmodi.000\book_writer_ai_toolkit\backups\webapp-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
)

Write-Host "Creating Web App Backup..." -ForegroundColor Green
Write-Host "Backup Location: $BackupPath" -ForegroundColor Yellow

# Create backup directory
New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null

# Source paths
$SourceWebApp = "C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app"
$GitHubRepo = "C:\temp\stone-sceptre-website"

# Backup original web app files
Write-Host "Backing up original web app files..." -ForegroundColor Cyan
$WebAppBackup = Join-Path $BackupPath "original-webapp"
Copy-Item $SourceWebApp $WebAppBackup -Recurse -Force

# Backup deployed GitHub repository if it exists
if (Test-Path $GitHubRepo) {
    Write-Host "Backing up deployed repository..." -ForegroundColor Cyan
    $RepoBackup = Join-Path $BackupPath "deployed-repo"
    Copy-Item $GitHubRepo $RepoBackup -Recurse -Force
}

# Create backup info file
$InfoContent = @"
WEB APP BACKUP INFORMATION
==========================
Backup Date: $(Get-Date)
Created by: backup-webapp.ps1

REPOSITORY INFORMATION:
- GitHub Repository: https://github.com/reversesingularity/stone-sceptre-website
- Live URL Book 1: https://reversesingularity.github.io/stone-sceptre-website/
- Live URL Book 2: https://reversesingularity.github.io/stone-sceptre-website/book2/

BACKUP CONTENTS:
- original-webapp/     : Complete source files for Book 2 web app
- deployed-repo/       : Full GitHub repository with both books
- backup-info.txt      : This information file

RESTORATION:
1. Copy files from original-webapp/ to desired location
2. To redeploy: Clone GitHub repo and copy files to book2/ directory
3. Test locally with: python -m http.server 8000

LAST DEPLOYMENT STATUS:
- Status: Production ready with full Book 2 integration
- Both books fully functional and cross-linked
- All documentation and deployment scripts included
"@

$InfoContent | Out-File -FilePath (Join-Path $BackupPath "backup-info.txt") -Encoding UTF8

Write-Host "Backup completed successfully!" -ForegroundColor Green
Write-Host "Backup Location: $BackupPath" -ForegroundColor Yellow