Write-Host ""
Write-Host "========================================================"
Write-Host "  NEPHILIM CHRONICLES -- CANON INGESTION"
Write-Host "  Installing dependencies and running pipeline..."
Write-Host "========================================================"
Write-Host ""

$scriptDir = "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles"
Set-Location $scriptDir

Write-Host "[1/2] Installing Python dependencies..."
pip install qdrant-client requests --quiet
Write-Host "  Dependencies: READY"

Write-Host ""
Write-Host "[2/2] Running ingestion pipeline..."
Write-Host "  This will embed all Chronicles files using your RTX 3080."
Write-Host "  Expected time: 5-15 minutes depending on corpus size."
Write-Host ""

python ingest_canon.py

Write-Host ""
Write-Host "  Done. Your Chronicles canon is now searchable in Qdrant."
Write-Host ""
