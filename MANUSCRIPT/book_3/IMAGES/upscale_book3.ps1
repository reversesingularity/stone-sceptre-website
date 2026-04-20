# Book 3 Image Upscaler — "The Edenic Mandate"
# Uses Real-ESRGAN (realesrgan-x4plus) to upscale all chapter/map source JPGs 4x
# Input:  MANUSCRIPT/book_3/IMAGES/CHAPTERS/*.jpg
# Output: MANUSCRIPT/book_3/IMAGES/upscaled/chapters/*.png
#
# Mirrors the process used for Book 2.
# Run from any directory — uses absolute paths throughout.

$basePath  = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_3\IMAGES"
$srcPath   = "$basePath\CHAPTERS"
$dstPath   = "$basePath\upscaled\chapters"
$toolsPath = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_2\IMAGES\tools"
$esrgan    = "$toolsPath\realesrgan-ncnn-vulkan.exe"

# Verify the binary exists
if (-not (Test-Path $esrgan)) {
    Write-Error "Real-ESRGAN binary not found at: $esrgan"
    exit 1
}

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $dstPath | Out-Null

Write-Host "=== Book 3 Image Upscaling (Real-ESRGAN x4plus) ===" -ForegroundColor Cyan
Write-Host "Source:  $srcPath" -ForegroundColor Gray
Write-Host "Output:  $dstPath" -ForegroundColor Gray
Write-Host ""

$images = Get-ChildItem "$srcPath\*" -Include *.jpg, *.png, *.jpeg -File
$total  = $images.Count
$done   = 0
$errors = @()

foreach ($img in $images) {
    $done++
    $outName = [System.IO.Path]::GetFileNameWithoutExtension($img.Name) + ".png"
    $outPath = "$dstPath\$outName"

    if (Test-Path $outPath) {
        Write-Host "[$done/$total] SKIP (exists): $outName" -ForegroundColor DarkGray
        continue
    }

    Write-Host "[$done/$total] Upscaling: $($img.Name) → $outName ..." -ForegroundColor Yellow -NoNewline

    # Real-ESRGAN: -i input -o output -n model -s scale -f output-format
    & $esrgan -i $img.FullName -o $outPath -n realesrgan-x4plus -s 4 -f png 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0 -and (Test-Path $outPath)) {
        $sizeMB = [math]::Round((Get-Item $outPath).Length / 1MB, 1)
        Write-Host " OK ($sizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        $errors += $img.Name
    }
}

Write-Host ""
Write-Host "=== Upscaling Complete ===" -ForegroundColor Cyan
Write-Host "Processed: $total images" -ForegroundColor Green
if ($errors.Count -gt 0) {
    Write-Host "Errors ($($errors.Count)):" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
} else {
    Write-Host "All images upscaled successfully." -ForegroundColor Green
}

Write-Host ""
Write-Host "Next step: run .\resize_to_kdp.ps1 to produce KDP-ready files." -ForegroundColor Cyan
