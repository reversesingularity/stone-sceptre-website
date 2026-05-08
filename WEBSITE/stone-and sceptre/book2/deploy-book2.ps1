# PowerShell Script to Deploy Book 2 to GitHub Pages
# deploy-book2.ps1

Write-Host "🚀 Deploying Book 2 to stone-sceptre-website GitHub Pages..." -ForegroundColor Green

# Configuration
$GitHubRepo = "https://github.com/reversesingularity/stone-sceptre-website.git"
$Book2SourcePath = "C:\Users\cmodi.000\book_writer_ai_toolkit\output\book_2_red_hand_chronicle\web-app"
$TempDir = "C:\temp\stone-sceptre-deploy"

try {
    # Step 1: Clone or update the repository
    Write-Host "📥 Cloning repository..." -ForegroundColor Yellow
    
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force
    }
    
    git clone $GitHubRepo $TempDir
    Set-Location $TempDir
    
    # Step 2: Create book2 directory structure
    Write-Host "📁 Creating Book 2 directory structure..." -ForegroundColor Yellow
    
    if (!(Test-Path "book2")) {
        New-Item -ItemType Directory -Path "book2"
    }
    
    if (!(Test-Path "book2\images")) {
        New-Item -ItemType Directory -Path "book2\images"
    }
    
    # Step 3: Copy Book 2 files
    Write-Host "📋 Copying Book 2 files..." -ForegroundColor Yellow
    
    Copy-Item "$Book2SourcePath\index.html" "book2\index.html" -Force
    Copy-Item "$Book2SourcePath\qr-code.html" "book2\qr-code.html" -Force
    Copy-Item "$Book2SourcePath\styles.css" "book2\styles.css" -Force
    Copy-Item "$Book2SourcePath\script.js" "book2\script.js" -Force
    
    if (Test-Path "$Book2SourcePath\images\book-cover.jpg") {
        Copy-Item "$Book2SourcePath\images\book-cover.jpg" "book2\images\book-cover.jpg" -Force
    }
    
    # Step 4: Add to git and commit
    Write-Host "📤 Committing changes..." -ForegroundColor Yellow
    
    git add .
    git commit -m "Add Book 2: The Red Hand & The Eternal Throne web app"
    
    # Step 5: Push to GitHub
    Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
    
    git push origin main
    
    Write-Host "✅ Success! Book 2 has been deployed to GitHub Pages!" -ForegroundColor Green
    Write-Host "🌐 Your Book 2 will be available at:" -ForegroundColor Cyan
    Write-Host "   https://reversesingularity.github.io/stone-sceptre-website/book2/" -ForegroundColor White
    Write-Host "" 
    Write-Host "⏰ Note: GitHub Pages may take a few minutes to update." -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Clean up
    Set-Location "C:\"
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force
    }
}

Write-Host "🎉 Deployment process complete!" -ForegroundColor Green