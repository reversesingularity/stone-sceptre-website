# KDP Image Resize Script — Book 2 "The Cauldron of God"
# Trim: 6"x9" | Pages: 600 | Paper: Cream | 300 DPI
#
# KDP Specs:
#   Kindle eBook cover:   1600 x 2560 px (portrait)
#   Paperback full wrap:  4125 x 2775 px (back + spine 1.5" + front + bleed)
#   Interior images:      300 DPI, max width 1650px (5.5" printable area)

$basePath = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_2\IMAGES"
$upscaled = "$basePath\upscaled"
$kdpReady = "$basePath\kdp_ready"

# Create output directories
New-Item -ItemType Directory -Force -Path "$kdpReady\covers", "$kdpReady\chapters" | Out-Null

Write-Host "=== KDP Cover Processing ===" -ForegroundColor Cyan

# --- Kindle eBook Cover ---
# Target: 1600 x 2560 px, RGB, 300 DPI
$kindleSrc = "$upscaled\covers\kindle-ebook-cover.png"
if (Test-Path $kindleSrc) {
    Write-Host "Processing Kindle eBook cover..."
    magick $kindleSrc -resize 1600x2560 -density 300 -units PixelsPerInch -quality 100 "$kdpReady\covers\kindle-ebook-cover.jpg"
    Write-Host "  -> kindle-ebook-cover.jpg (1600x2560, 300 DPI)" -ForegroundColor Green
} else {
    Write-Host "  MISSING: $kindleSrc" -ForegroundColor Red
}

# --- Paperback Full Cover ---
# Target: 4125 x 2775 px, CMYK, 300 DPI, PDF
$pbSrc = "$upscaled\covers\paperback-fullcover.png"
if (Test-Path $pbSrc) {
    Write-Host "Processing Paperback full cover..."
    # Resize to exact KDP wrap dimensions, then output as both PDF and high-quality JPG
    magick $pbSrc -resize 4125x2775! -density 300 -units PixelsPerInch -quality 100 "$kdpReady\covers\paperback-fullcover.jpg"
    magick $pbSrc -resize 4125x2775! -density 300 -units PixelsPerInch -colorspace CMYK "$kdpReady\covers\paperback-fullcover.pdf"
    Write-Host "  -> paperback-fullcover.jpg (4125x2775, 300 DPI, RGB)" -ForegroundColor Green
    Write-Host "  -> paperback-fullcover.pdf (4125x2775, 300 DPI, CMYK)" -ForegroundColor Green
} else {
    Write-Host "  MISSING: $pbSrc" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== KDP Interior Image Processing ===" -ForegroundColor Cyan

# --- Chapter/Map Interior Images ---
# Target: max 1650px wide (5.5" at 300 DPI), maintain aspect ratio, 300 DPI
$chapterSrc = "$upscaled\chapters"
if (Test-Path $chapterSrc) {
    $images = Get-ChildItem $chapterSrc -Include *.png,*.jpg -File
    foreach ($img in $images) {
        Write-Host "Processing $($img.Name)..."
        $outName = [System.IO.Path]::ChangeExtension($img.Name, ".png")
        # Resize to max 1650px wide, maintaining aspect ratio
        # Use Lanczos filter for best quality downscale from 4x
        magick $img.FullName -filter Lanczos -resize "1650x>" -density 300 -units PixelsPerInch -quality 100 "$kdpReady\chapters\$outName"
        
        # Get output dimensions for reporting
        $dims = magick identify -format "%wx%h" "$kdpReady\chapters\$outName"
        Write-Host "  -> $outName ($dims, 300 DPI)" -ForegroundColor Green
    }
} else {
    Write-Host "  MISSING: $chapterSrc" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
$coverCount = (Get-ChildItem "$kdpReady\covers" -File -ErrorAction SilentlyContinue).Count
$chapterCount = (Get-ChildItem "$kdpReady\chapters" -File -ErrorAction SilentlyContinue).Count
Write-Host "Covers:   $coverCount files in $kdpReady\covers" -ForegroundColor Green
Write-Host "Chapters: $chapterCount files in $kdpReady\chapters" -ForegroundColor Green
Write-Host ""

# Verify dimensions
Write-Host "=== Dimension Verification ===" -ForegroundColor Cyan
Get-ChildItem "$kdpReady" -Recurse -Include *.jpg,*.png,*.pdf | ForEach-Object {
    $dims = magick identify -format "%wx%h %r %x DPI" $_.FullName 2>$null
    [PSCustomObject]@{Name=$_.Name; Details=$dims; Folder=$_.Directory.Name}
} | Format-Table -AutoSize
