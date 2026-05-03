# Upscale-FullCoverKDP.ps1
# Full-cover upscale + KDP resize pipeline for "The Edenic Mandate" (Book 3)
#
# KDP Paperback Full Cover Specs (6"x9", cream paper, ~500pp):
#   Dimensions: 4125 x 2775 px at 300 DPI
#   Width:  13.75" = back (6.125") + spine (~1.5") + front (6.125")
#   Height:  9.25" = 9" + 0.125" bleed top + 0.125" bleed bottom
#   Colour:  RGB, sRGB IEC61966-2.1
#   Format:  JPG (KDP upload), PDF/CMYK (print vendor reference)
#
# Source: COVERS/paperback-fullcover-book3.png  (1536x1024, ~2.7MB)
# Step 1: ESRGAN x4plus  -->  upscaled/covers/paperback-fullcover.png  (6144x4096)
# Step 2: ImageMagick    -->  kdp_ready/covers/paperback-fullcover.jpg  (4125x2775, 300 DPI)
#                        -->  kdp_ready/covers/paperback-fullcover.pdf  (4125x2775, 300 DPI, CMYK)
#
# Run from any directory — all paths are absolute.

$basePath  = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_3\IMAGES"
$toolsPath = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_2\IMAGES\tools"
$esrgan    = "$toolsPath\realesrgan-ncnn-vulkan.exe"

$srcFile   = "$basePath\COVERS\paperback-fullcover-book3.png"
$upscaled  = "$basePath\upscaled\covers\paperback-fullcover.png"
$kdpJpg    = "$basePath\kdp_ready\covers\paperback-fullcover.jpg"
$kdpPdf    = "$basePath\kdp_ready\covers\paperback-fullcover.pdf"

# ─── Pre-flight checks ────────────────────────────────────────────────────────

if (-not (Test-Path $esrgan)) {
    Write-Error "Real-ESRGAN binary not found: $esrgan"
    exit 1
}
if (-not (Test-Path $srcFile)) {
    Write-Error "Source cover not found: $srcFile"
    exit 1
}
if (-not (Get-Command magick -ErrorAction SilentlyContinue)) {
    Write-Error "ImageMagick 'magick' not found in PATH. Install from https://imagemagick.org"
    exit 1
}

# ─── Directories ──────────────────────────────────────────────────────────────

New-Item -ItemType Directory -Force -Path (Split-Path $upscaled) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $kdpJpg)   | Out-Null

# ─── Step 1: Real-ESRGAN 4x Upscale ──────────────────────────────────────────

Write-Host ""
Write-Host "=== STEP 1: Real-ESRGAN x4plus Upscale ===" -ForegroundColor Cyan

$srcInfo = magick identify -format "%wx%h" $srcFile 2>&1
Write-Host "  Source : $srcFile" -ForegroundColor Gray
Write-Host "  Size   : $srcInfo" -ForegroundColor Gray
Write-Host "  Output : $upscaled" -ForegroundColor Gray
Write-Host ""

# Report if overwriting a pre-existing upscaled file
if (Test-Path $upscaled) {
    $existing = magick identify -format "%wx%h" $upscaled 2>&1
    Write-Host "  NOTE: Replacing existing upscaled file ($existing)" -ForegroundColor Yellow
    Remove-Item $upscaled -Force
}

Write-Host "  Running ESRGAN (this may take 1-3 minutes on GPU) ..." -ForegroundColor Yellow

& $esrgan -i $srcFile -o $upscaled -n realesrgan-x4plus -s 4 -f png 2>&1 | ForEach-Object {
    if ($_ -match '\S') { Write-Host "  [ESRGAN] $_" -ForegroundColor DarkGray }
}

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $upscaled)) {
    Write-Error "ESRGAN upscale FAILED (exit $LASTEXITCODE)"
    exit 1
}

$upscaledInfo = magick identify -format "%wx%h" $upscaled 2>&1
$upscaledMB   = [math]::Round((Get-Item $upscaled).Length / 1MB, 1)
Write-Host "  OK: $upscaledInfo  ($upscaledMB MB)" -ForegroundColor Green

# ─── Step 2: ImageMagick — Resize to KDP Final Spec ─────────────────────────

Write-Host ""
Write-Host "=== STEP 2: ImageMagick — Resize to KDP Spec ===" -ForegroundColor Cyan
Write-Host "  Target: 4125 x 2775 px  |  300 DPI  |  sRGB (JPG) + CMYK (PDF)" -ForegroundColor Gray
Write-Host ""

# JPG — RGB, sRGB, quality 100 (KDP upload format)
Write-Host "  [1/2] Generating paperback-fullcover.jpg (RGB/sRGB) ..." -ForegroundColor Yellow
magick $upscaled `
    -resize 4125x2775! `
    -density 300 -units PixelsPerInch `
    -colorspace sRGB `
    -quality 100 `
    $kdpJpg 2>&1 | ForEach-Object { if ($_ -match '\S') { Write-Host "  $_" -ForegroundColor DarkGray } }

if ($LASTEXITCODE -ne 0) { Write-Error "JPG resize failed"; exit 1 }

$jpgInfo = magick identify -format "%wx%h @ %x x %y DPI" $kdpJpg 2>&1
$jpgMB   = [math]::Round((Get-Item $kdpJpg).Length / 1MB, 1)
Write-Host "  OK: $jpgInfo  ($jpgMB MB)" -ForegroundColor Green

# PDF — CMYK, 300 DPI (print vendor / offset reference)
Write-Host ""
Write-Host "  [2/2] Generating paperback-fullcover.pdf (CMYK/300 DPI) ..." -ForegroundColor Yellow
magick $upscaled `
    -resize 4125x2775! `
    -density 300 -units PixelsPerInch `
    -colorspace CMYK `
    $kdpPdf 2>&1 | ForEach-Object { if ($_ -match '\S') { Write-Host "  $_" -ForegroundColor DarkGray } }

if ($LASTEXITCODE -ne 0) { Write-Error "PDF resize failed"; exit 1 }

$pdfMB = [math]::Round((Get-Item $kdpPdf).Length / 1MB, 1)
Write-Host "  OK: paperback-fullcover.pdf  ($pdfMB MB)" -ForegroundColor Green

# ─── Summary ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=== KDP Cover Pipeline Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "  Upscaled (ESRGAN 4x) : $upscaled" -ForegroundColor White
Write-Host "  KDP Upload (JPG)     : $kdpJpg" -ForegroundColor White
Write-Host "  Print Ref  (PDF)     : $kdpPdf" -ForegroundColor White
Write-Host ""
Write-Host "  KDP Upload checklist:" -ForegroundColor Cyan
Write-Host "    [x] 4125 x 2775 px (300 DPI)" -ForegroundColor Green
Write-Host "    [x] sRGB colour space (JPG)" -ForegroundColor Green
Write-Host "    [x] No transparency (flattened)" -ForegroundColor Green
Write-Host "    [ ] Spine text aligned within safe zone (verify visually)" -ForegroundColor Yellow
Write-Host "    [ ] Barcode area clear (back cover lower-right, ~2.0 x 1.2 in)" -ForegroundColor Yellow
Write-Host "    [ ] Upload .jpg to KDP Cover Creator or print-ready PDF to IngramSpark" -ForegroundColor Yellow
Write-Host ""
