"""
DESKTOP-SINGULA -- Nephilim Chronicles Canon Search API
A local Flask server that provides semantic search over the Chronicles Qdrant collection.
Run: python canon_search_api.py
Then open: http://localhost:8765
"""

import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

OLLAMA_URL      = "http://localhost:11434"
QDRANT_URL      = "http://localhost:6333"
EMBED_MODEL     = "nomic-embed-text"
COLLECTION_NAME = "nephilim_chronicles"
API_PORT        = 8765

CATEGORY_COLOURS = {
    "canon":           "#c084fc",
    "dossier":         "#f472b6",
    "manuscript":      "#34d399",
    "worldbuilding":   "#60a5fa",
    "reference":       "#fbbf24",
    "session_log":     "#a78bfa",
    "production_docx": "#fb923c",
    "other":           "#9ca3af",
}

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Nephilim Chronicles -- Canon Search</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0a0f;
    color: #e2e8f0;
    font-family: 'Georgia', serif;
    min-height: 100vh;
  }
  .header {
    background: linear-gradient(135deg, #1a0a2e 0%, #0f172a 100%);
    border-bottom: 1px solid #7c3aed44;
    padding: 24px 40px;
    display: flex;
    align-items: center;
    gap: 20px;
  }
  .header-icon { font-size: 36px; }
  .header-title { font-size: 22px; font-weight: bold; color: #c084fc; letter-spacing: 1px; }
  .header-sub { font-size: 13px; color: #64748b; margin-top: 4px; font-family: monospace; }
  .stats-bar {
    background: #0f172a;
    border-bottom: 1px solid #1e293b;
    padding: 10px 40px;
    display: flex;
    gap: 32px;
    font-family: monospace;
    font-size: 12px;
    color: #64748b;
  }
  .stats-bar span { color: #94a3b8; }
  .main { max-width: 960px; margin: 40px auto; padding: 0 24px; }
  .search-box {
    background: #0f172a;
    border: 1px solid #7c3aed66;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
  }
  .search-row { display: flex; gap: 12px; }
  input[type=text] {
    flex: 1;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 16px;
    color: #f1f5f9;
    font-family: Georgia, serif;
    outline: none;
    transition: border-color 0.2s;
  }
  input[type=text]:focus { border-color: #7c3aed; }
  .btn-search {
    background: #7c3aed;
    border: none;
    border-radius: 8px;
    padding: 14px 28px;
    color: white;
    font-size: 15px;
    cursor: pointer;
    font-family: Georgia, serif;
    transition: background 0.2s;
    white-space: nowrap;
  }
  .btn-search:hover { background: #6d28d9; }
  .filters { margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
  .filter-label { font-size: 12px; color: #64748b; font-family: monospace; }
  select {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    color: #94a3b8;
    font-size: 13px;
    font-family: monospace;
    cursor: pointer;
  }
  .presets { margin-top: 14px; }
  .preset-label { font-size: 11px; color: #475569; font-family: monospace; margin-bottom: 8px; }
  .preset-btns { display: flex; flex-wrap: wrap; gap: 8px; }
  .preset-btn {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px;
    color: #94a3b8;
    cursor: pointer;
    font-family: monospace;
    transition: all 0.15s;
  }
  .preset-btn:hover { border-color: #7c3aed; color: #c084fc; background: #1a0a2e; }
  .results-header {
    font-size: 12px;
    color: #64748b;
    font-family: monospace;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
  }
  .result-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
  }
  .result-card:hover { border-color: #334155; }
  .result-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
  .result-source { font-family: monospace; font-size: 12px; color: #64748b; }
  .result-meta { display: flex; gap: 8px; align-items: center; }
  .score-badge {
    background: #1e293b;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-family: monospace;
    color: #94a3b8;
  }
  .score-high { color: #34d399; }
  .score-med  { color: #fbbf24; }
  .score-low  { color: #f87171; }
  .cat-badge {
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-family: monospace;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .result-text {
    font-size: 15px;
    line-height: 1.7;
    color: #cbd5e1;
    border-left: 3px solid #1e293b;
    padding-left: 14px;
    margin-top: 8px;
  }
  .result-chunk { font-size: 11px; color: #475569; font-family: monospace; margin-top: 8px; }
  .loading { text-align: center; padding: 60px; color: #7c3aed; font-size: 20px; }
  .empty { text-align: center; padding: 60px; color: #334155; }
  .empty-icon { font-size: 48px; margin-bottom: 16px; }
  .error-msg { background: #1a0a0a; border: 1px solid #7f1d1d; border-radius: 8px; padding: 16px; color: #f87171; font-family: monospace; font-size: 13px; }
</style>
</head>
<body>

<div class="header">
  <div class="header-icon">📜</div>
  <div>
    <div class="header-title">THE NEPHILIM CHRONICLES &mdash; CANON SEARCH</div>
    <div class="header-sub">DESKTOP-SINGULA &nbsp;|&nbsp; RTX 3080 &nbsp;|&nbsp; Qdrant + nomic-embed-text &nbsp;|&nbsp; 10,254 vectors</div>
  </div>
</div>

<div class="stats-bar">
  <div>Collection: <span>nephilim_chronicles</span></div>
  <div>Files: <span>73</span></div>
  <div>Chunks: <span>10,254</span></div>
  <div>Model: <span>nomic-embed-text</span></div>
  <div>Status: <span style="color:#34d399">LIVE</span></div>
</div>

<div class="main">
  <div class="search-box">
    <div class="search-row">
      <input type="text" id="query" placeholder="Ask anything about the Chronicles... e.g. 'What are Raphael's limitations?'" autofocus>
      <button class="btn-search" onclick="search()">Search Canon</button>
    </div>
    <div class="filters">
      <span class="filter-label">Filter category:</span>
      <select id="cat-filter">
        <option value="">All categories</option>
        <option value="canon">Canon</option>
        <option value="dossier">Dossiers</option>
        <option value="manuscript">Manuscript</option>
        <option value="worldbuilding">Worldbuilding</option>
        <option value="production_docx">Production Docx</option>
        <option value="reference">Reference</option>
        <option value="session_log">Session Logs</option>
      </select>
      <select id="top-k">
        <option value="5">Top 5</option>
        <option value="10" selected>Top 10</option>
        <option value="20">Top 20</option>
      </select>
    </div>
    <div class="presets">
      <div class="preset-label">Quick queries:</div>
      <div class="preset-btns">
        <button class="preset-btn" onclick="setQuery('Who is Cian mac Morna and what is his backstory?')">Cian mac Morna</button>
        <button class="preset-btn" onclick="setQuery('What are Raphael the guardian angel limitations and the Ban?')">Raphael / The Ban</button>
        <button class="preset-btn" onclick="setQuery('Who are the Two Witnesses of Revelation 11?')">Two Witnesses</button>
        <button class="preset-btn" onclick="setQuery('What is Methuselah Sword Mo Chra and how does it work?')">Mo Chra Sword</button>
        <button class="preset-btn" onclick="setQuery('Who is Shemyaza and what is his role as the Beast?')">Shemyaza / Beast</button>
        <button class="preset-btn" onclick="setQuery('Who is Azazel and what is the prison at Dudael Antarctica?')">Azazel / Dudael</button>
        <button class="preset-btn" onclick="setQuery('Who is Miriam Ashford and what is her background?')">Miriam Ashford</button>
        <button class="preset-btn" onclick="setQuery('What is the acoustic paradigm and Watcher technology?')">Acoustic Paradigm</button>
        <button class="preset-btn" onclick="setQuery('What happens in Book 5 the final battle?')">Book 5 Endgame</button>
        <button class="preset-btn" onclick="setQuery('What is the Synagogue of Satan thirteen houses?')">Synagogue of Satan</button>
        <button class="preset-btn" onclick="setQuery('What happened to Cian previous wives?')">Cian Wives</button>
        <button class="preset-btn" onclick="setQuery('What is the Cydonia revelation and Mars connection?')">Cydonia / Mars</button>
      </div>
    </div>
  </div>

  <div id="results"></div>
</div>

<script>
const CAT_COLOURS = {
  "canon":           "#c084fc",
  "dossier":         "#f472b6",
  "manuscript":      "#34d399",
  "worldbuilding":   "#60a5fa",
  "reference":       "#fbbf24",
  "session_log":     "#a78bfa",
  "production_docx": "#fb923c",
  "other":           "#9ca3af",
};

function setQuery(q) {
  document.getElementById('query').value = q;
  search();
}

document.getElementById('query').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') search();
});

async function search() {
  const query = document.getElementById('query').value.trim();
  if (!query) return;
  const cat   = document.getElementById('cat-filter').value;
  const topk  = document.getElementById('top-k').value;
  const div   = document.getElementById('results');
  div.innerHTML = '<div class="loading">&#9670; Searching canon...</div>';

  try {
    const resp = await fetch(`/search?q=${encodeURIComponent(query)}&cat=${cat}&k=${topk}`);
    const data = await resp.json();
    if (data.error) {
      div.innerHTML = `<div class="error-msg">ERROR: ${data.error}</div>`;
      return;
    }
    renderResults(data.results, query, data.elapsed_ms);
  } catch(e) {
    div.innerHTML = `<div class="error-msg">Connection error: ${e.message}</div>`;
  }
}

function renderResults(results, query, elapsed) {
  const div = document.getElementById('results');
  if (!results || results.length === 0) {
    div.innerHTML = '<div class="empty"><div class="empty-icon">&#9670;</div>No results found.</div>';
    return;
  }
  let html = `<div class="results-header"><span>${results.length} results for "${query}"</span><span>${elapsed}ms</span></div>`;
  for (const r of results) {
    const cat    = r.category || "other";
    const colour = CAT_COLOURS[cat] || "#9ca3af";
    const score  = r.score;
    const scoreClass = score >= 0.65 ? "score-high" : score >= 0.55 ? "score-med" : "score-low";
    const text   = r.text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    html += `
      <div class="result-card">
        <div class="result-top">
          <div class="result-source">${r.source_file}</div>
          <div class="result-meta">
            <span class="cat-badge" style="background:${colour}22;color:${colour}">${cat}</span>
            <span class="score-badge ${scoreClass}">${score.toFixed(3)}</span>
          </div>
        </div>
        <div class="result-text">${text}</div>
        <div class="result-chunk">chunk ${r.chunk_index + 1} of ${r.total_chunks} &nbsp;|&nbsp; ${r.source_root}</div>
      </div>`;
  }
  div.innerHTML = html;
}
</script>
</body>
</html>
"""

class CanonSearchHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Suppress default access logs

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif parsed.path == "/search":
            params = parse_qs(parsed.query)
            query  = params.get("q", [""])[0]
            cat    = params.get("cat", [""])[0]
            k      = int(params.get("k", ["10"])[0])

            import time
            t0 = time.time()
            result = self.do_search(query, cat, k)
            elapsed = int((time.time() - t0) * 1000)
            result["elapsed_ms"] = elapsed

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_search(self, query, category_filter, top_k):
        try:
            # Get embedding
            r = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": query},
                timeout=30
            )
            r.raise_for_status()
            vector = r.json()["embedding"]

            # Build Qdrant query
            payload = {"vector": vector, "limit": top_k, "with_payload": True}
            if category_filter:
                payload["filter"] = {
                    "must": [{"key": "category", "match": {"value": category_filter}}]
                }

            r2 = requests.post(
                f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search",
                json=payload,
                timeout=30
            )
            r2.raise_for_status()
            hits = r2.json().get("result", [])

            results = []
            for hit in hits:
                p = hit["payload"]
                results.append({
                    "score":       round(hit["score"], 4),
                    "source_file": p.get("source_file", ""),
                    "source_root": p.get("source_root", ""),
                    "category":    p.get("category", "other"),
                    "chunk_index": p.get("chunk_index", 0),
                    "total_chunks":p.get("total_chunks", 1),
                    "text":        p.get("text", ""),
                    "filename":    p.get("filename", ""),
                })
            return {"results": results}

        except Exception as e:
            return {"error": str(e), "results": []}


def main():
    print()
    print("=" * 56)
    print("  NEPHILIM CHRONICLES -- CANON SEARCH")
    print("  DESKTOP-SINGULA | Qdrant + nomic-embed-text")
    print("=" * 56)
    print()
    print(f"  Starting server on http://localhost:{API_PORT}")
    print(f"  Press Ctrl+C to stop.")
    print()

    server = HTTPServer(("localhost", API_PORT), CanonSearchHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")


if __name__ == "__main__":
    main()
