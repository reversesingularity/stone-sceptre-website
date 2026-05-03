"""
Swarm Health Monitor — Port 8774
One-glance dashboard for the entire Nephilim Chronicles Creative Swarm.

Pages:
  /        → Overview (service health, Qdrant, CRDT, last audit, last marketing gen)
  /logs    → Live tail of DAEMON_HEALTH.log and marketing_log.json
  /freeze  → Toggle Author Freeze Mode
"""

import json
import logging
from pathlib import Path
from datetime import datetime

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_PORT = 8774
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "LOGS"
FREEZE_LOCK = PROJECT_ROOT / "FREEZE_MODE.lock"
DAEMON_HEALTH_LOG = LOG_DIR / "DAEMON_HEALTH.log"
MARKETING_LOG = LOG_DIR / "marketing_log.json"

N8N_WEBHOOK_NIGHTLY = "http://localhost:5678/webhook/nightly-continuity-prep"

# Services to monitor (name, url, port)
SERVICES = [
    ("n8n", "http://localhost:5678", 5678),
    ("Qdrant", "http://localhost:6333", 6333),
    ("Ollama", "http://localhost:11434/api/tags", 11434),
    ("Canon Search API", "http://localhost:8765/health", 8765),
    ("KDP Format", "http://localhost:8766/health", 8766),
    ("Story Prototype", "http://localhost:8767/health", 8767),
    ("Nemotron Router", "http://localhost:8768/health", 8768),
    ("Theological Guard", "http://localhost:8770/health", 8770),
    ("Conductor", "http://localhost:8771/health", 8771),
    ("Agent 9 Content", "http://localhost:8772/health", 8772),
    ("Marketing Agent", "http://localhost:8773/health", 8773),
    ("Image Prompt Designer", "http://localhost:8775/health", 8775),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Dashboard] %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "monitoring_dashboard.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("dashboard")

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(title="Swarm Health Monitor", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------------------------------------------------------------------------
# Shared HTML shell
# ---------------------------------------------------------------------------
_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TNC Swarm Monitor</title>
<script src="https://unpkg.com/htmx.org@1.9.12"></script>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
body{background:#0f172a;color:#e2e8f0;font-family:ui-monospace,monospace}
.pill-up{background:#059669;color:#fff;padding:2px 10px;border-radius:9999px;font-size:.75rem}
.pill-down{background:#dc2626;color:#fff;padding:2px 10px;border-radius:9999px;font-size:.75rem}
.pill-freeze{background:#f59e0b;color:#000;padding:2px 10px;border-radius:9999px;font-size:.75rem}
.card{background:#1e293b;border-radius:.75rem;padding:1.25rem;margin-bottom:1rem;border:1px solid #334155}
pre{white-space:pre-wrap;word-break:break-all;max-height:70vh;overflow-y:auto;background:#0f172a;padding:1rem;border-radius:.5rem;font-size:.8rem}
a.nav{color:#38bdf8;text-decoration:none;margin-right:1.5rem;font-weight:600}
a.nav:hover{text-decoration:underline}
</style>
</head>
<body class="p-6 max-w-6xl mx-auto">
<header class="mb-8">
<h1 class="text-2xl font-bold text-cyan-400 mb-2">&#9670; TNC Swarm Health Monitor</h1>
<nav>
<a class="nav" href="/">Overview</a>
<a class="nav" href="/logs">Logs</a>
<a class="nav" href="/freeze">Freeze Mode</a>
</nav>
</header>
"""
_FOOT = "</body></html>"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _check_service(name: str, url: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=12) as c:
            r = await c.get(url)
            return {"name": name, "status": "up" if r.status_code < 500 else "down", "code": r.status_code}
    except Exception:
        return {"name": name, "status": "down", "code": 0}


def _read_tail(path: Path, lines: int = 80) -> str:
    if not path.exists():
        return f"(file not found: {path.name})"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return "\n".join(text.splitlines()[-lines:])
    except Exception as exc:
        return f"(read error: {exc})"


def _last_marketing_gen() -> str:
    if not MARKETING_LOG.exists():
        return "No generations yet"
    try:
        entries = json.loads(MARKETING_LOG.read_text(encoding="utf-8"))
        if entries:
            last = entries[-1]
            return f"{last.get('timestamp', '?')} — {last.get('content_type', '?')} (Book {last.get('book')}, Ch{last.get('chapter')})"
    except Exception:
        pass
    return "No generations yet"


def _qdrant_stats() -> dict:
    try:
        import requests as req
        r = req.get("http://localhost:6333/collections", timeout=4)
        r.raise_for_status()
        cols = r.json().get("result", {}).get("collections", [])
        return {"count": len(cols), "names": [c["name"] for c in cols]}
    except Exception:
        return {"count": "?", "names": []}


def _crdt_pending() -> int:
    crdt_dir = PROJECT_ROOT / "STAGING" / "crdt_proposals"
    if not crdt_dir.exists():
        return 0
    return len(list(crdt_dir.glob("*.json")))


def _last_audit() -> str:
    audit_dir = PROJECT_ROOT / "02_ANALYSIS"
    if not audit_dir.exists():
        return "No audits found"
    audits = sorted(audit_dir.glob("NIGHTLY_AUDIT_*.md"), reverse=True)
    if audits:
        return audits[0].name
    return "No audits found"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def overview():
    import asyncio
    checks = await asyncio.gather(*[_check_service(name, url) for name, url, _ in SERVICES])

    freeze_active = FREEZE_LOCK.exists()
    qdrant = _qdrant_stats()
    crdt = _crdt_pending()
    last_audit = _last_audit()
    last_mkt = _last_marketing_gen()

    rows = ""
    for svc in checks:
        pill = "pill-up" if svc["status"] == "up" else "pill-down"
        rows += f'<tr><td class="py-1 pr-4">{svc["name"]}</td><td><span class="{pill}">{svc["status"]}</span></td><td class="text-gray-500 text-sm pl-4">{svc["code"]}</td></tr>'

    html = _HEAD + f"""
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card">
        <h2 class="text-lg font-semibold text-cyan-300 mb-3">Service Health</h2>
        <table class="w-full"><tbody>{rows}</tbody></table>
      </div>
      <div class="card">
        <h2 class="text-lg font-semibold text-cyan-300 mb-3">System Status</h2>
        <div class="space-y-2 text-sm">
          <p><strong>Freeze Mode:</strong>
            <span class="{'pill-freeze' if freeze_active else 'pill-up'}">
              {'ACTIVE — dispatches halted' if freeze_active else 'OFF — normal operations'}
            </span>
          </p>
          <p><strong>Qdrant Collections:</strong> {qdrant['count']} ({', '.join(qdrant['names'][:5])})</p>
          <p><strong>Pending CRDT Proposals:</strong> {crdt}</p>
          <p><strong>Last Nightly Audit:</strong> {last_audit}</p>
          <p><strong>Last Marketing Gen:</strong> {last_mkt}</p>
        </div>
      </div>
    </div>
    <div class="card mt-4">
      <h2 class="text-lg font-semibold text-cyan-300 mb-3">Quick Actions</h2>
      <div class="flex gap-4">
        <button hx-post="/api/force-audit" hx-swap="innerHTML" hx-target="#audit-result"
                class="bg-cyan-700 hover:bg-cyan-600 text-white px-4 py-2 rounded font-semibold text-sm">
          Force Nightly Audit
        </button>
        <span id="audit-result" class="text-sm text-gray-400 self-center"></span>
      </div>
    </div>
    """ + _FOOT
    return HTMLResponse(html)


@app.get("/logs", response_class=HTMLResponse)
async def logs_page():
    health_tail = _read_tail(DAEMON_HEALTH_LOG, 60)
    mkt_tail = _read_tail(MARKETING_LOG, 40)

    html = _HEAD + f"""
    <div class="card">
      <h2 class="text-lg font-semibold text-cyan-300 mb-2">DAEMON_HEALTH.log (last 60 lines)</h2>
      <pre>{health_tail}</pre>
    </div>
    <div class="card">
      <h2 class="text-lg font-semibold text-cyan-300 mb-2">marketing_log.json (last 40 lines)</h2>
      <pre>{mkt_tail}</pre>
    </div>
    <p class="text-gray-500 text-sm mt-2">Refresh page to update. Auto-refresh:
      <button onclick="location.reload()" class="text-cyan-400 underline ml-1">Now</button>
    </p>
    """ + _FOOT
    return HTMLResponse(html)


@app.get("/freeze", response_class=HTMLResponse)
async def freeze_page():
    active = FREEZE_LOCK.exists()
    status_text = "ACTIVE — all Nemoclaw auto-dispatches are halted" if active else "OFF — normal operations"
    btn_label = "Deactivate Freeze" if active else "Activate Freeze"
    btn_color = "bg-green-700 hover:bg-green-600" if active else "bg-red-700 hover:bg-red-600"

    html = _HEAD + f"""
    <div class="card">
      <h2 class="text-lg font-semibold text-cyan-300 mb-3">Author Freeze Mode</h2>
      <p class="mb-4">
        <strong>Current Status:</strong>
        <span class="{'pill-freeze' if active else 'pill-up'}">{status_text}</span>
      </p>
      <p class="text-sm text-gray-400 mb-4">
        When active, Nemoclaw will not process file-change events, fire drift alerts,
        or trigger n8n webhooks. Health checks continue. Toggle safely at any time.
      </p>
      <button hx-post="/api/toggle-freeze" hx-swap="innerHTML" hx-target="body"
              class="{btn_color} text-white px-6 py-3 rounded font-semibold">
        {btn_label}
      </button>
    </div>
    """ + _FOOT
    return HTMLResponse(html)


# ---------------------------------------------------------------------------
# API endpoints (HTMX targets)
# ---------------------------------------------------------------------------
@app.post("/api/toggle-freeze", response_class=HTMLResponse)
async def toggle_freeze():
    if FREEZE_LOCK.exists():
        FREEZE_LOCK.unlink()
        log.info("Freeze Mode DEACTIVATED by dashboard")
    else:
        FREEZE_LOCK.write_text(
            f"Freeze activated via dashboard at {datetime.utcnow().isoformat()}Z\n",
            encoding="utf-8",
        )
        log.info("Freeze Mode ACTIVATED by dashboard")
    # Re-render the freeze page inline
    return await freeze_page()


@app.post("/api/force-audit")
async def force_audit():
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(N8N_WEBHOOK_NIGHTLY)
            if r.status_code < 400:
                log.info("Forced nightly audit via n8n webhook")
                return HTMLResponse('<span class="text-green-400">Audit triggered ✓</span>')
            return HTMLResponse(f'<span class="text-red-400">n8n returned {r.status_code}</span>')
    except Exception as exc:
        return HTMLResponse(f'<span class="text-red-400">Failed: {exc}</span>')


@app.get("/api/health")
async def api_health():
    return {"service": "swarm_health_monitor", "port": API_PORT, "status": "ok", "freeze_active": FREEZE_LOCK.exists()}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    log.info("Starting Swarm Health Monitor on port %d", API_PORT)
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
