# KDP Image Resize Script — Book 3 "The Edenic Mandate"
# Trim: 6"x9" | Paper: Cream | 300 DPI
#
# KDP Specs:
#   Kindle eBook cover:   1600 x 2560 px (portrait)
#   Paperback full wrap:  4125 x 2775 px (back + spine + front + bleed)
#   Interior images:      300 DPI, max width 1650px (5.5" printable area)
#
# Run AFTER upscale_book3.ps1 has populated the upscaled/chapters folder.

$basePath  = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_3\IMAGES"
$upscaled  = "$basePath\upscaled"
$kdpReady  = "$basePath\kdp_ready"

# Create output directories
New-Item -ItemType Directory -Force -Path "$kdpReady\covers", "$kdpReady\chapters" | Out-Null

Write-Host "=== Book 3 KDP Cover Processing ===" -ForegroundColor Cyan

# --- Kindle eBook Cover ---
$kindleSrc = "$upscaled\covers\kindle-ebook-cover.png"
if (Test-Path $kindleSrc) {
    Write-Host "Processing Kindle eBook cover..."
    magick $kindleSrc -resize 1600x2560 -density 300 -units PixelsPerInch -quality 100 "$kdpReady\covers\kindle-ebook-cover.jpg"
    Write-Host "  -> kindle-ebook-cover.jpg (1600x2560, 300 DPI)" -ForegroundColor Green
} else {
    Write-Host "  SKIP: Kindle cover not found at $kindleSrc" -ForegroundColor DarkGray
}

# --- Paperback Full Cover ---
$pbSrc = "$upscaled\covers\paperback-fullcover.png"
if (Test-Path $pbSrc) {
    Write-Host "Processing Paperback full cover..."
    magick $pbSrc -resize 4125x2775! -density 300 -units PixelsPerInch -quality 100 "$kdpReady\covers\paperback-fullcover.jpg"
    magick $pbSrc -resize 4125x2775! -density 300 -units PixelsPerInch -colorspace CMYK "$kdpReady\covers\paperback-fullcover.pdf"
    Write-Host "  -> paperback-fullcover.jpg (4125x2775, 300 DPI, RGB)" -ForegroundColor Green
    Write-Host "  -> paperback-fullcover.pdf (4125x2775, 300 DPI, CMYK)" -ForegroundColor Green
} else {
    Write-Host "  SKIP: Paperback cover not found at $pbSrc" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Book 3 KDP Interior Image Processing ===" -ForegroundColor Cyan

# --- Chapter/Map Interior Images ---
# Target: max 1650px wide (5.5" at 300 DPI), maintain aspect ratio, 300 DPI
# Input:  upscaled/chapters/*.png   (4x upscaled by Real-ESRGAN)
# Output: kdp_ready/chapters/*.png  (capped at 1650px, 300 DPI)

$chapterSrc = "$upscaled\chapters"
if (Test-Path $chapterSrc) {
    $images = Get-ChildItem "$chapterSrc\*" -Include *.png, *.jpg -File
    $total  = $images.Count
    $done   = 0

    foreach ($img in $images) {
        $done++
        $outName = [System.IO.Path]::ChangeExtension($img.Name, ".png")
        $outPath = "$kdpReady\chapters\$outName"
        Write-Host "[$done/$total] Processing: $($img.Name)..." -ForegroundColor Yellow -NoNewline

        # Resize to max 1650px wide, maintaining aspect ratio
        # Lanczos filter for best quality downscale from 4x upscaled source
        magick $img.FullName -filter Lanczos -resize "1650x>" -density 300 -units PixelsPerInch -quality 100 $outPath

        if (Test-Path $outPath) {
            $dims = magick identify -format "%wx%h" $outPath
            $sizeMB = [math]::Round((Get-Item $outPath).Length / 1MB, 2)
            Write-Host " $dims, 300 DPI ($sizeMB MB)" -ForegroundColor Green
        } else {
            Write-Host " FAILED" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  ERROR: upscaled/chapters not found at $chapterSrc" -ForegroundColor Red
    Write-Host "  Run upscale_book3.ps1 first." -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
$coverCount   = (Get-ChildItem "$kdpReady\covers"   -File -ErrorAction SilentlyContinue).Count
$chapterCount = (Get-ChildItem "$kdpReady\chapters" -File -ErrorAction SilentlyContinue).Count
Write-Host "Covers:   $coverCount file(s) in $kdpReady\covers"   -ForegroundColor Green
Write-Host "Chapters: $chapterCount file(s) in $kdpReady\chapters" -ForegroundColor Green
Write-Host ""

# Dimension verification
Write-Host "=== Dimension Verification ===" -ForegroundColor Cyan
Get-ChildItem "$kdpReady" -Recurse -Include *.jpg, *.png, *.pdf | ForEach-Object {
    $dims = magick identify -units PixelsPerInch -format "%wx%h %x DPI" $_.FullName 2>$null
    [PSCustomObject]@{Name=$_.Name; Dimensions=$dims; Folder=$_.Directory.Name}
} | Format-Table -AutoSize

Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host "KDP-ready files: $kdpReady\chapters" -ForegroundColor Green
Write-Host "Run 'KDP_BOOK=3 python build_manuscript.py' to assemble the DOCX." -ForegroundColor Cyan
