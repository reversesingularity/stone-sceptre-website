# Web App Backup Script
# Creates a complete backup of all web app files and configurations

param(
    [string]$BackupPath = "C:\Users\cmodi.000\book_writer_ai_toolkit\backups\webapp-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
)

Write-Host "🔄 Creating Web App Backup..." -ForegroundColor Green
Write-Host "Backup Location: $BackupPath" -ForegroundColor Yellow

# Create backup directory
New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null

# Source paths
$SourceWebApp = "C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app"
$GitHubRepo = "C:\temp\stone-sceptre-website"

try {
    # 1. Backup original web app files
    Write-Host "📁 Backing up original web app files..." -ForegroundColor Cyan
    $WebAppBackup = Join-Path $BackupPath "original-webapp"
    Copy-Item $SourceWebApp $WebAppBackup -Recurse -Force

    # 2. Backup deployed GitHub repository
    if (Test-Path $GitHubRepo) {
        Write-Host "📁 Backing up deployed repository..." -ForegroundColor Cyan
        $RepoBackup = Join-Path $BackupPath "deployed-repo"
        Copy-Item $GitHubRepo $RepoBackup -Recurse -Force
    }

    # 3. Create settings export
    Write-Host "⚙️ Exporting settings..." -ForegroundColor Cyan
    $SettingsPath = Join-Path $BackupPath "settings"
    New-Item -ItemType Directory -Path $SettingsPath -Force | Out-Null

    # Export configuration details
    @"
# Web App Configuration Export
Generated: $(Get-Date)

## Repository Information
GitHub Repository: https://github.com/reversesingularity/stone-sceptre-website
Live URL Book 1: https://reversesingularity.github.io/stone-sceptre-website/
Live URL Book 2: https://reversesingularity.github.io/stone-sceptre-website/book2/

## File Structure
Original Source: $SourceWebApp
GitHub Repo: $GitHubRepo
Backup Location: $BackupPath

## Critical Files Backed Up:
- All web app source files
- GitHub repository (if available)
- Configuration documentation
- Deployment scripts
- README files
- Asset files and images

## Recovery Instructions:
1. Restore files from backup location
2. Re-deploy to GitHub using git commands
3. Verify GitHub Pages configuration
4. Test both Book 1 and Book 2 URLs

## Last Successful Deployment:
Date: October 1, 2025
Commit: "Complete series integration: Add Book 2 navigation, update README, and add cross-linking"
Status: Production ready with full Book 2 integration
"@ | Out-File -FilePath (Join-Path $SettingsPath "configuration-export.txt") -Encoding UTF8

    # 4. Create file inventory
    Write-Host "📋 Creating file inventory..." -ForegroundColor Cyan
    $InventoryPath = Join-Path $SettingsPath "file-inventory.txt"
    
    "WEB APP BACKUP INVENTORY" | Out-File $InventoryPath -Encoding UTF8
    "========================" | Out-File $InventoryPath -Append -Encoding UTF8
    "Backup Date: $(Get-Date)" | Out-File $InventoryPath -Append -Encoding UTF8
    "" | Out-File $InventoryPath -Append -Encoding UTF8
    
    "ORIGINAL WEB APP FILES:" | Out-File $InventoryPath -Append -Encoding UTF8
    Get-ChildItem $WebAppBackup -Recurse | ForEach-Object { 
        $_.FullName.Replace($WebAppBackup, "") 
    } | Out-File $InventoryPath -Append -Encoding UTF8
    
    if (Test-Path $RepoBackup) {
        "" | Out-File $InventoryPath -Append -Encoding UTF8
        "DEPLOYED REPOSITORY FILES:" | Out-File $InventoryPath -Append -Encoding UTF8
        Get-ChildItem $RepoBackup -Recurse | ForEach-Object { 
            $_.FullName.Replace($RepoBackup, "") 
        } | Out-File $InventoryPath -Append -Encoding UTF8
    }

    # 5. Create restoration script
    Write-Host "🔧 Creating restoration script..." -ForegroundColor Cyan
    $RestoreScript = Join-Path $BackupPath "RESTORE-WEBAPP.ps1"
    
    @"
# Web App Restoration Script
# Run this script to restore the web app from backup

param(
    [string]`$TargetPath = "C:\temp\webapp-restore-`$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
)

Write-Host "🔄 Restoring Web App from Backup..." -ForegroundColor Green

# Restore original web app
Copy-Item "`$PSScriptRoot\original-webapp" "`$TargetPath\original-webapp" -Recurse -Force

# Restore deployed repository (if exists)
if (Test-Path "`$PSScriptRoot\deployed-repo") {
    Copy-Item "`$PSScriptRoot\deployed-repo" "`$TargetPath\deployed-repo" -Recurse -Force
}

Write-Host "✅ Restoration complete!" -ForegroundColor Green
Write-Host "Files restored to: `$TargetPath" -ForegroundColor Yellow
Write-Host "" 
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review restored files" -ForegroundColor White
Write-Host "2. Re-deploy to GitHub if needed" -ForegroundColor White
Write-Host "3. Test web applications" -ForegroundColor White
"@ | Out-File $RestoreScript -Encoding UTF8

    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Backup Location: $BackupPath" -ForegroundColor Yellow
    Write-Host "📁 Files backed up:" -ForegroundColor Cyan
    Write-Host "   - Original web app source files" -ForegroundColor White
    if (Test-Path $RepoBackup) {
        Write-Host "   - Deployed GitHub repository" -ForegroundColor White
    }
    Write-Host "   - Configuration settings" -ForegroundColor White
    Write-Host "   - File inventory" -ForegroundColor White
    Write-Host "   - Restoration script" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 To restore: Run RESTORE-WEBAPP.ps1 in the backup folder" -ForegroundColor Green

} catch {
    Write-Host "❌ Backup failed: $($_.Exception.Message)" -ForegroundColor Red
    throw
}