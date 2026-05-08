# Quick Deploy Script - One-Click Update
# Run this after making changes to instantly deploy to live site

Write-Host "🚀 Quick Deploy: Workspace → Live Site" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Yellow

$SourcePath = "C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app"
$GitRepoPath = "C:\temp\stone-sceptre-website"

try {
    # Step 1: Sync files
    Write-Host "📋 Step 1: Syncing files..." -ForegroundColor Cyan
    Copy-Item "$SourcePath\*" "$GitRepoPath\book2\" -Recurse -Force
    Write-Host "   ✅ Files synced successfully" -ForegroundColor Green

    # Step 2: Git operations
    Write-Host "📤 Step 2: Deploying to GitHub..." -ForegroundColor Cyan
    Set-Location $GitRepoPath
    git add .
    
    # Check if there are changes to commit
    $status = git status --porcelain
    if ($status) {
        $commitMessage = "Quick update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $commitMessage
        git push origin main
        
        Write-Host "   ✅ Changes deployed to GitHub" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Your live site will update in 1-2 minutes!" -ForegroundColor Yellow
        Write-Host "   Book 1: https://reversesingularity.github.io/stone-sceptre-website/" -ForegroundColor White
        Write-Host "   Book 2: https://reversesingularity.github.io/stone-sceptre-website/book2/" -ForegroundColor White
    } else {
        Write-Host "   ℹ️ No changes detected - site is already up to date" -ForegroundColor Blue
    }

} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check your network connection and try again." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ Quick Deploy Complete!" -ForegroundColor Green