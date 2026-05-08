# File Watcher Script for Auto-Sync
# Monitors workspace for changes and auto-deploys to GitHub

param(
    [string]$WatchPath = "C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app",
    [string]$GitRepo = "C:\temp\stone-sceptre-website",
    [int]$CheckInterval = 30  # seconds
)

Write-Host "🔄 Starting Web App Auto-Sync Watcher..." -ForegroundColor Green
Write-Host "Watching: $WatchPath" -ForegroundColor Yellow
Write-Host "Target: $GitRepo\book2\" -ForegroundColor Yellow
Write-Host "Check Interval: $CheckInterval seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor White
Write-Host ""

# Function to sync files
function Sync-Files {
    param($Source, $Destination)
    
    try {
        $changes = $false
        
        # Check if source files are newer
        $sourceFiles = Get-ChildItem $Source -Recurse -File
        
        foreach ($file in $sourceFiles) {
            $relativePath = $file.FullName.Substring($Source.Length + 1)
            $destFile = Join-Path $Destination $relativePath
            
            if (!(Test-Path $destFile) -or $file.LastWriteTime -gt (Get-Item $destFile).LastWriteTime) {
                $changes = $true
                break
            }
        }
        
        if ($changes) {
            Write-Host "📋 Changes detected! Syncing files..." -ForegroundColor Yellow
            
            # Create destination directory if it doesn't exist
            $destDir = Join-Path $Destination "book2"
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            # Copy files
            Copy-Item "$Source\*" $destDir -Recurse -Force
            
            # Git operations
            Set-Location $Destination
            git add .
            $commitMessage = "Auto-update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            git commit -m $commitMessage
            git push origin main
            
            Write-Host "✅ Successfully deployed changes!" -ForegroundColor Green
            Write-Host "🌐 Live site will update in 1-2 minutes" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host "❌ Error during sync: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main watch loop
$lastCheck = Get-Date
while ($true) {
    Start-Sleep $CheckInterval
    
    Write-Host "⏰ Checking for changes... $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Sync-Files $WatchPath $GitRepo
}