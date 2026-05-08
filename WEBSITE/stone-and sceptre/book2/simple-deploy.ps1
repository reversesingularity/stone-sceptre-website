# Quick Deploy Script - Deploy Workspace Changes to Live Site
Write-Host "Quick Deploy: Workspace to Live Site" -ForegroundColor Green

$SourcePath = "C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app"
$GitRepoPath = "C:\temp\stone-sceptre-website"

Write-Host "Syncing files..." -ForegroundColor Cyan
Copy-Item "$SourcePath\*" "$GitRepoPath\book2\" -Recurse -Force

Write-Host "Deploying to GitHub..." -ForegroundColor Cyan
Set-Location $GitRepoPath
git add .

$status = git status --porcelain
if ($status) {
    $commitMessage = "Quick update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $commitMessage
    git push origin main
    
    Write-Host "Changes deployed successfully!" -ForegroundColor Green
    Write-Host "Live site will update in 1-2 minutes" -ForegroundColor Yellow
    Write-Host "Book 2: https://reversesingularity.github.io/stone-sceptre-website/book2/" -ForegroundColor White
} else {
    Write-Host "No changes detected - site is up to date" -ForegroundColor Blue
}

Write-Host "Deploy Complete!" -ForegroundColor Green