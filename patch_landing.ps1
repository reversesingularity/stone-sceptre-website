param()
$ErrorActionPreference = 'Stop'

# 1. Download
$token = gh auth token
$authHdr = @{ Authorization = "token $token" }
$rawUri  = "https://raw.githubusercontent.com/reversesingularity/stone-sceptre-website/main/index.html"
$html    = (Invoke-WebRequest -Uri $rawUri -Headers $authHdr -UseBasicParsing).Content
Write-Host "Downloaded: $($html.Length) chars"

# 2. Book 2 card HTML
$book2Card = @"

                <!-- Nephilim Book 2 -->
                <article class="book-card nephilim-card">
                    <div class="book-card-header">
                        <div class="book-cover-container">
                            <img src="./nephilim/book2/images/book-cover.jpg"
                                 alt="The Cauldron of God - Book 2 of The Nephilim Chronicles by Kerman Gild" />
                        </div>
                        <div class="book-card-info">
                            <span class="book-number-label">BOOK TWO</span>
                            <h3>The Cauldron of God</h3>
                            <p class="book-subtitle">The Nephilim Chronicles</p>
                            <p class="book-stats">~130,000 words &bull; Available Now</p>
                        </div>
                    </div>
                    <div class="book-card-body">
                        <p>Seven weeks after Mars. Two kilometres beneath Antarctic ice, something five thousand years old is waking up.</p>
                        <p>Cian mac Morna has never lost a war. He has never descended into a Watcher-era prison with a depleted sword and a finite clock. Until now. Naamah has found Dudael &mdash; the antediluvian prison of Azazel &mdash; and she is two kilometres from breaking the final seal.</p>
                        <div class="book-quote">
                            <p>&ldquo;Bind Azazel hand and foot, and cast him into the darkness: and make an opening in the desert which is in Dudael.&rdquo;</p>
                            <cite>&mdash; 1 Enoch 10:4</cite>
                        </div>
                        <div class="book-card-buttons">
                            <a href="https://www.amazon.com.au/" class="btn btn-primary" target="_blank" rel="noopener">Buy on Amazon</a>
                            <a href="./nephilim/book2/" class="btn btn-secondary">Explore Book 2</a>
                        </div>
                    </div>
                </article>
"@

# 3. Insertion: find Nephilim Book 1 Explore link, then find the closing </article></div> after it
$anchor    = './nephilim/" class="btn btn-secondary">Explore Book 1</a>'
$anchorIdx = $html.IndexOf($anchor)
Write-Host "Anchor idx: $anchorIdx"
if ($anchorIdx -lt 0) { Write-Error "Anchor not found"; exit 1 }

# Find </article> after that anchor
$closeArticle = '                </article>'
$relClose = $html.IndexOf($closeArticle, $anchorIdx)
Write-Host "Close article at: $relClose  content: [$($html.Substring($relClose, 80))]"

# The insertion goes RIGHT BEFORE that </article> + remaining closing tags
# We want: existing-close-article + book2card inserted BEFORE the next </div></div></section>
# Simple approach: split at $relClose + $closeArticle.Length, insert card in between

$beforeInsert = $html.Substring(0, $relClose + $closeArticle.Length)
$afterInsert  = $html.Substring($relClose + $closeArticle.Length)
Write-Host "afterInsert starts with: [$($afterInsert.Substring(0, 60))]"

$html = $beforeInsert + $book2Card + $afterInsert
Write-Host "After card insertion: $($html.Length) chars"

# 4. Update footer
$old2 = '<a href="./nephilim/">The Cydonian Oaths (Nephilim Chronicles)</a>'
if ($html.IndexOf($old2) -lt 0) {
    # Try with trailing spaces
    $old2 = '<a href="./nephilim/">The Cydonian Oaths (Nephilim Chronicles)</a>  '
}
Write-Host "Footer anchor found at: $($html.IndexOf($old2))"
$new2 = '<a href="./nephilim/">Nephilim Book 1: The Cydonian Oaths</a>' + "`n            " + '<a href="./nephilim/book2/">Nephilim Book 2: The Cauldron of God</a>'
$html = $html.Replace($old2, $new2)
Write-Host "After footer update: $($html.Length) chars"

# 5. Save locally
$localOut = "f:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\WEBSITE\index.html"
[System.IO.File]::WriteAllText($localOut, $html, [System.Text.Encoding]::UTF8)
Write-Host "Saved locally: $((Get-Item $localOut).Length) bytes"

# 6. Push to GitHub
$bytes   = [System.Text.Encoding]::UTF8.GetBytes($html)
$b64     = [Convert]::ToBase64String($bytes)
$apiUri  = "https://api.github.com/repos/reversesingularity/stone-sceptre-website/contents/index.html"
$shaResp = Invoke-RestMethod -Uri $apiUri -Headers $authHdr
$fileSha = $shaResp.sha
Write-Host "Current SHA: $fileSha"
$body = @{ message = "Add Cauldron of God (Book 2) to landing page + update footer"; content = $b64; sha = $fileSha; branch = "main" } | ConvertTo-Json
$pushResp = Invoke-RestMethod -Uri $apiUri -Method Put -Headers $authHdr -Body $body -ContentType "application/json"
Write-Host "Pushed! Commit SHA: $($pushResp.commit.sha)"
