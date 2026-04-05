Write-Host ""
Write-Host "========================================================"
Write-Host "  NEPHILIM CHRONICLES -- CANON SEARCH SERVER"
Write-Host "========================================================"
Write-Host ""
Write-Host "  Starting search interface at http://localhost:8765"
Write-Host "  Opening browser..."
Write-Host ""
Write-Host "  Press Ctrl+C in this window to stop the server."
Write-Host ""

Set-Location "F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles"

# Open browser after 2 seconds
Start-Process "http://localhost:8765"

# Start the server
python canon_search_api.py
