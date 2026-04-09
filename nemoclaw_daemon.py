"""
DESKTOP-SINGULA — Nemoclaw Daemon
===================================
Persistent 24/7 background daemon for The Nephilim Chronicles v2.0 Creative Swarm.
Implements OpenClaw-style heartbeat loop.

Responsibilities:
    1. Watch MANUSCRIPT directories for new/changed chapter files
    2. Auto-vectorize changed chapters into Qdrant tnc_episodes
    3. Queue chapters for Story Prototype extraction (Agent 8)
    4. Collect CRDT proposals and trigger Constitution Updater
    5. Run lightweight drift alerts every 30 minutes
    6. Health-check all 7 services every 5 minutes
    7. Pre-load context for nightly 02:00 cross-book audit

Usage:
    python nemoclaw_daemon.py [--log-level INFO|DEBUG]
    Install as Windows service: see README note below

Windows Service Note:
    To run on startup, create a scheduled task:
    Action: Start a program
    Program: F:\\Projects-cmodi.000\\book_writer_ai_toolkit\\output\\nephilim_chronicles\\.venv\\Scripts\\python.exe
    Arguments: F:\\Projects-cmodi.000\\book_writer_ai_toolkit\\output\\nephilim_chronicles\\nemoclaw_daemon.py
    Trigger: At startup
"""

import os
import sys
import json
import time
import hashlib
import logging
import argparse
import threading
import requests
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue, Empty

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
WATCH_PATHS   = [
    PROJECT_ROOT / "MANUSCRIPT" / "book_3",
    PROJECT_ROOT / "MANUSCRIPT" / "book_4",
    PROJECT_ROOT / "MANUSCRIPT" / "book_5",
]
STAGING_DIR   = PROJECT_ROOT / "STAGING" / "crdt_proposals"
LOG_DIR       = PROJECT_ROOT / "LOGS"
HEALTH_LOG    = LOG_DIR / "DAEMON_HEALTH.log"
ERROR_LOG     = LOG_DIR / "nemoclaw_errors.log"

N8N_BASE           = "http://localhost:5678"
QDRANT_URL         = "http://localhost:6333"
OLLAMA_URL         = "http://localhost:11434"
CANON_SEARCH_URL   = "http://localhost:8765"
KDP_FORMAT_URL     = "http://localhost:8766"
STORY_PROTO_URL    = "http://localhost:8767"
NEMOTRON_ROUTER    = "http://localhost:8768"
EMBED_MODEL        = "nomic-embed-text"
DRIFT_MODEL        = "mistral"

# Heartbeat intervals (seconds)
HEALTH_CHECK_INTERVAL   = 300    # 5 minutes
FILE_WATCH_INTERVAL     = 60     # 1 minute
DRIFT_ALERT_INTERVAL    = 1800   # 30 minutes
CRDT_COLLECT_INTERVAL   = 300    # 5 minutes
NIGHTLY_PREP_HOUR       = 1      # 01:45 → schedule at HH=1, MM=45
NIGHTLY_PREP_MINUTE     = 45

VALID_EXTENSIONS = {".md", ".txt"}
FILE_CHANGE_DEBOUNCE_S  = 5      # wait 5s after last modification before processing

# ── Setup ─────────────────────────────────────────────────────────────────────

LOG_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NEMOCLAW] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(ERROR_LOG), encoding="utf-8"),
    ]
)
logger = logging.getLogger("nemoclaw")

# Global file event queue
file_event_queue = Queue()

# Track last-seen file mtimes to detect changes
_file_mtimes = {}
_nightly_prep_done_date = None


# ── Health Check ──────────────────────────────────────────────────────────────

SERVICES = {
    "n8n":           f"{N8N_BASE}/healthz",
    "qdrant":        f"{QDRANT_URL}/healthz",
    "ollama":        f"{OLLAMA_URL}/api/tags",
    "canon_search":  f"{CANON_SEARCH_URL}/health",
    "kdp_format":    f"{KDP_FORMAT_URL}/health",
    "story_proto":   f"{STORY_PROTO_URL}/health",
    "nemotron_router": f"{NEMOTRON_ROUTER}/health",
}


def check_service(name, url):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code < 400
    except Exception:
        return False


def run_health_check():
    results = {}
    for name, url in SERVICES.items():
        results[name] = check_service(name, url)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok_count   = sum(1 for v in results.values() if v)
    total      = len(results)
    status_sym = "✓" if ok_count == total else "⚠"

    line = (
        f"{ts}  {status_sym} {ok_count}/{total} services UP  "
        + "  ".join(f"{'✓' if v else '✗'} {k}" for k, v in results.items())
    )

    with open(HEALTH_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    if ok_count < total:
        down = [k for k, v in results.items() if not v]
        logger.warning(f"Services DOWN: {down}")
    else:
        logger.debug(f"Health OK — {ok_count}/{total} services up")

    return results


# ── File Watcher ──────────────────────────────────────────────────────────────

def scan_watched_paths():
    """Scan MANUSCRIPT directories for new/changed files and enqueue events."""
    for watch_path in WATCH_PATHS:
        if not watch_path.exists():
            continue
        for root, dirs, files in os.walk(watch_path):
            # Skip hidden and build directories
            dirs[:] = [d for d in dirs if not d.startswith((".", "_", "__"))]
            for fname in files:
                fpath = Path(root) / fname
                if fpath.suffix.lower() not in VALID_EXTENSIONS:
                    continue
                try:
                    mtime = fpath.stat().st_mtime
                except OSError:
                    continue

                key = str(fpath)
                last_mtime = _file_mtimes.get(key, 0)

                if mtime > last_mtime:
                    _file_mtimes[key] = mtime
                    if last_mtime > 0:  # not first-time discovery
                        age_s = time.time() - mtime
                        if age_s > FILE_CHANGE_DEBOUNCE_S:
                            file_event_queue.put({
                                "event_type": "MODIFIED",
                                "path": key,
                                "timestamp": datetime.now().isoformat(),
                            })
                            logger.info(f"File change detected: {fpath.name}")
                    else:
                        logger.debug(f"First-seen file indexed: {fpath.name}")


# ── File Event Processor ──────────────────────────────────────────────────────

def process_file_event(event):
    """Handle a file change event — notify n8n and auto-vectorize."""
    path = event["path"]
    logger.info(f"Processing: {Path(path).name}")

    # 1. Notify n8n
    try:
        r = requests.post(
            f"{N8N_BASE}/webhook/nemoclaw-file-event",
            json=event,
            timeout=10
        )
        if r.status_code < 400:
            logger.info(f"  n8n notified: {r.status_code}")
        else:
            logger.warning(f"  n8n webhook returned {r.status_code}")
    except Exception as e:
        logger.warning(f"  n8n notify failed: {e}")

    # 2. Auto-vectorize chapter into tnc_episodes
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()

        # Simple summary: first 500 chars as excerpt
        excerpt = text[:500].replace("\n", " ").strip()

        # Parse book/chapter from path
        path_obj = Path(path)
        book_num = "?"
        for part in path_obj.parts:
            if part.startswith("book_"):
                book_num = part.replace("book_", "")

        episode_payload = {
            "source_file": path,
            "book":        book_num,
            "chapter":     path_obj.stem,
            "excerpt":     excerpt,
            "char_count":  len(text),
            "timestamp":   datetime.now().isoformat(),
            "category":    "chapter_summary",
            "entity_type": "chapter",
        }

        # Embed and upsert to tnc_episodes
        embed_and_upsert(text[:2000], episode_payload, "tnc_episodes")
        logger.info(f"  Vectorized to tnc_episodes")

    except Exception as e:
        logger.error(f"  Auto-vectorize failed: {e}")

    # 3. Queue Story Prototype extraction
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()

        r = requests.post(
            f"{STORY_PROTO_URL}/extract-triples",
            json={
                "chapter_text": text[:8000],
                "book_num": book_num,
                "chapter_num": Path(path).stem,
            },
            timeout=180
        )
        if r.status_code < 400:
            result = r.json()
            triple_count = len(result.get("role_triples", []))
            event_count  = len(result.get("plot_events", []))
            contra_count = len(result.get("contradictions", []))
            logger.info(f"  Story Prototype: {triple_count} triples, "
                        f"{event_count} events, {contra_count} contradictions")
            if contra_count > 0:
                logger.warning(f"  CONTRADICTIONS DETECTED in {Path(path).name} — check Story Prototype")
    except Exception as e:
        logger.warning(f"  Story Prototype extraction failed: {e}")


def embed_and_upsert(text, payload, collection):
    """Embed text and upsert a single point to Qdrant."""
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text[:4000]},
        timeout=30
    )
    r.raise_for_status()
    vec = r.json()["embedding"]

    point_id = int(hashlib.sha256(
        (payload.get("source_file", "") + payload.get("timestamp", "")).encode()
    ).hexdigest()[:12], 16) % (2**53)

    requests.post(
        f"{QDRANT_URL}/collections/{collection}/points",
        json={"points": [{"id": point_id, "vector": vec, "payload": payload}]},
        timeout=30
    ).raise_for_status()


# ── CRDT Collector ────────────────────────────────────────────────────────────

def run_crdt_collect():
    """Check for pending proposals; trigger n8n Constitution Updater if found."""
    if not STAGING_DIR.exists():
        return

    proposals = list(STAGING_DIR.glob("proposal_*.json"))
    if not proposals:
        logger.debug("CRDT: No pending proposals.")
        return

    logger.info(f"CRDT: {len(proposals)} proposal(s) pending — triggering Constitution Updater")
    try:
        r = requests.post(
            f"{N8N_BASE}/webhook/constitution-update",
            json={"proposals_dir": str(STAGING_DIR), "count": len(proposals)},
            timeout=10
        )
        logger.info(f"  Constitution Updater triggered: {r.status_code}")
    except Exception as e:
        logger.warning(f"  Could not trigger Constitution Updater: {e}")


# ── Drift Alert ───────────────────────────────────────────────────────────────

def run_drift_alert():
    """Run a lightweight drift check on the most recently modified chapter."""
    # Find most recently modified chapter across watch paths
    latest_file = None
    latest_mtime = 0

    for watch_path in WATCH_PATHS:
        if not watch_path.exists():
            continue
        for f in watch_path.rglob("*.md"):
            try:
                mt = f.stat().st_mtime
                if mt > latest_mtime:
                    latest_mtime = mt
                    latest_file = f
            except OSError:
                pass

    if not latest_file:
        logger.debug("Drift Alert: No chapter files found.")
        return

    # Only alert if file is less than 24 hours old
    age_h = (time.time() - latest_mtime) / 3600
    if age_h > 24:
        logger.debug(f"Drift Alert: Latest file {latest_file.name} is {age_h:.1f}h old — skip")
        return

    logger.info(f"Drift Alert: Checking {latest_file.name}")
    try:
        r = requests.post(
            f"{N8N_BASE}/webhook/analyse-chapter",
            json={
                "book": "auto",
                "chapter": str(latest_file),
                "fast_mode": True,
            },
            timeout=10
        )
        logger.info(f"  Drift check triggered: {r.status_code}")
    except Exception as e:
        logger.warning(f"  Drift alert trigger failed: {e}")


# ── Nightly Prep ──────────────────────────────────────────────────────────────

def run_nightly_prep():
    """Pre-load Books 3+4+5 for the 02:00 cross-book audit."""
    global _nightly_prep_done_date
    today = datetime.now().date()

    if _nightly_prep_done_date == today:
        return  # already ran today

    now = datetime.now()
    if not (now.hour == NIGHTLY_PREP_HOUR and now.minute >= NIGHTLY_PREP_MINUTE):
        return

    logger.info("Nightly Prep: triggering cross-book audit pre-load")
    try:
        r = requests.post(
            f"{N8N_BASE}/webhook/nightly-continuity-prep",
            json={"triggered_by": "nemoclaw", "timestamp": now.isoformat()},
            timeout=10
        )
        logger.info(f"  Nightly prep triggered: {r.status_code}")
        _nightly_prep_done_date = today
    except Exception as e:
        logger.warning(f"  Nightly prep trigger failed: {e}")


# ── Persona Arc Tracker ───────────────────────────────────────────────────────

def track_persona_arcs(path, book_num):
    """
    Extract character state updates from chapter and upsert to tnc_personas.
    Lightweight: just embeds the chapter text with character metadata tags.
    Heavy extraction is handled by Agent 8 via the Story Prototype service.
    """
    KEY_CHARACTERS = [
        "CIAN", "MIRIAM", "BRENNAN", "ELIJAH", "ENOCH",
        "RAPHAEL", "LIAIGH", "AZAZEL", "NAAMAH", "OHYA",
        "SHEMYAZA", "JAMES"
    ]

    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()

        text_upper = text.upper()
        present_chars = [c for c in KEY_CHARACTERS if c in text_upper]

        if not present_chars:
            return

        for char in present_chars:
            # Find paragraphs mentioning this character
            paras = [p for p in text.split("\n\n") if char.lower() in p.lower()]
            if not paras:
                continue

            char_excerpt = "\n".join(paras[:3])[:1000]
            payload = {
                "character_id":   char,
                "name":           char.title(),
                "last_seen_chapter": Path(path).stem,
                "last_seen_book": book_num,
                "excerpt":        char_excerpt,
                "timestamp":      datetime.now().isoformat(),
                "entity_type":    "character",
                "category":       "dossier",
            }

            embed_and_upsert(char_excerpt, payload, "tnc_personas")

        logger.debug(f"  Personas updated for: {present_chars}")

    except Exception as e:
        logger.warning(f"Persona arc tracking failed: {e}")


# ── Main Loop ─────────────────────────────────────────────────────────────────

class Timer:
    """Simple interval timer that fires when enough time has passed."""
    def __init__(self, interval_s):
        self.interval = interval_s
        self.last_fired = 0

    def should_fire(self):
        now = time.time()
        if now - self.last_fired >= self.interval:
            self.last_fired = now
            return True
        return False


def main_loop():
    logger.info("═" * 60)
    logger.info("  NEMOCLAW DAEMON — The Nephilim Chronicles v2.0")
    logger.info("  Heartbeat loop running. Press Ctrl+C to stop.")
    logger.info("═" * 60)

    timers = {
        "health":   Timer(HEALTH_CHECK_INTERVAL),
        "filewat":  Timer(FILE_WATCH_INTERVAL),
        "drift":    Timer(DRIFT_ALERT_INTERVAL),
        "crdt":     Timer(CRDT_COLLECT_INTERVAL),
    }

    # Initial health check
    run_health_check()

    while True:
        try:
            # File watch scan
            if timers["filewat"].should_fire():
                scan_watched_paths()

            # Process any queued file events
            processed = 0
            while processed < 5:  # drain up to 5 events per cycle
                try:
                    event = file_event_queue.get_nowait()
                    process_file_event(event)
                    processed += 1
                except Empty:
                    break

            # Health check
            if timers["health"].should_fire():
                run_health_check()

            # CRDT collection
            if timers["crdt"].should_fire():
                run_crdt_collect()

            # Drift alert
            if timers["drift"].should_fire():
                run_drift_alert()

            # Nightly prep (polls every cycle, guard inside function)
            run_nightly_prep()

            time.sleep(10)  # base cycle: 10 seconds

        except KeyboardInterrupt:
            logger.info("Shutdown signal received. Stopping Nemoclaw daemon.")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}", exc_info=True)
            time.sleep(30)  # cool-down before retry


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Nemoclaw Daemon — 24/7 background engine for TNC v2.0 swarm"
    )
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging verbosity")
    args = parser.parse_args()
    logging.getLogger("nemoclaw").setLevel(args.log_level)
    logging.getLogger().setLevel(args.log_level)

    # Outer crash-restart wrapper
    attempt = 0
    while True:
        attempt += 1
        if attempt > 1:
            logger.info(f"Restarting Nemoclaw (attempt {attempt})...")
            time.sleep(10)
        try:
            main_loop()
            break  # clean exit
        except Exception as e:
            logger.critical(f"Fatal error in main_loop: {e}", exc_info=True)
            # Continue outer loop → restart


if __name__ == "__main__":
    main()
