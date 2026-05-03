"""
DESKTOP-SINGULA — Swarm Conductor (Agent 0)
============================================
HTTP server (port 8771) that acts as the master orchestrator for the
HAWK 12-agent creative swarm for The Nephilim Chronicles v2.0.

Powered by Nemotron 3 Super (120B MoE) via nemotron_tool_router.py (:8768).

Responsibilities:
    1. Receive user intent (POST /conduct)
    2. Decompose intent into an ordered task graph via Nemotron
    3. Dispatch sub-tasks to n8n /webhook/swarm-dispatch
    4. Track completion state per task
    5. Return task_id for async polling (GET /task-status/{id})

Architecture guarantees:
    - Agents NEVER call each other directly — only via this Conductor or n8n bus
    - All dispatches go through /webhook/swarm-dispatch (WF1)
    - Task state stored in-process (ephemeral); survives only as long as server runs
    - Tier 1 (working memory) loaded from Qdrant tnc_episodes per chapter before dispatch

Endpoints:
    POST /conduct              — accept user intent, return task plan
    GET  /task-status/{id}     — poll task completion
    GET  /tasks                — list all active tasks
    POST /task-complete        — n8n callbacks mark sub-task complete
    GET  /health               — service health

Usage:
    python conductor_server.py
"""

import json
import uuid
import time
import logging
import sys
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
import requests

# ── Config ───────────────────────────────────────────────────────────────────

API_PORT        = 8771
N8N_BASE        = "http://localhost:5678"
NEMOTRON_ROUTER = "http://localhost:8768"
QDRANT_URL      = "http://localhost:6333"
THEOL_GUARD_URL = "http://localhost:8770"
STORY_PROTO_URL = "http://localhost:8767"

PROJECT_ROOT = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
LOGS_DIR     = PROJECT_ROOT / "LOGS"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CONDUCTOR] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOGS_DIR / "conductor.log"), encoding="utf-8"),
    ]
)
logger = logging.getLogger("conductor")

# ── Task Registry (in-process) ────────────────────────────────────────────────

_tasks: dict = {}          # task_id → TaskRecord
_tasks_lock = threading.Lock()


def new_task(user_intent: str, book: str, chapter: str) -> dict:
    task_id = str(uuid.uuid4())[:8]
    record = {
        "task_id":     task_id,
        "intent":      user_intent,
        "book":        book,
        "chapter":     chapter,
        "plan":        [],           # list of SubTask dicts
        "status":      "pending",    # pending → planning → dispatched → complete → failed
        "created_at":  datetime.now().isoformat(),
        "updated_at":  datetime.now().isoformat(),
        "dispatched":  [],           # list of dispatched webhook task_types
        "completed":   [],           # list of completed task_types
        "errors":      [],
    }
    with _tasks_lock:
        _tasks[task_id] = record
    return record


def update_task(task_id: str, **kwargs):
    with _tasks_lock:
        if task_id in _tasks:
            _tasks[task_id].update(kwargs)
            _tasks[task_id]["updated_at"] = datetime.now().isoformat()


def get_task(task_id: str) -> dict | None:
    with _tasks_lock:
        return _tasks.get(task_id)


# ── Qdrant Tier 1 — Working Memory Loader ────────────────────────────────────

def load_working_memory(book: str, chapter: str) -> str:
    """
    Query tnc_episodes for the current chapter + neighbours to provide
    context for Nemotron's task-decomposition prompt.
    Returns a condensed text summary.
    """
    try:
        # Scroll for recent episodes matching book
        r = requests.post(
            f"{QDRANT_URL}/collections/tnc_episodes/points/scroll",
            json={
                "filter": {
                    "must": [{"key": "book", "match": {"value": str(book)}}]
                },
                "limit": 5,
                "with_payload": True,
                "with_vector": False,
            },
            timeout=10,
        )
        r.raise_for_status()
        points = r.json().get("result", {}).get("points", [])
        if not points:
            return "(no prior chapter context found in tnc_episodes)"

        excerpts = []
        for pt in points:
            p = pt.get("payload", {})
            excerpts.append(
                f"Book {p.get('book','?')} Ch {p.get('chapter','?')}: "
                f"{p.get('excerpt','')[:200]}"
            )
        return "\n".join(excerpts)
    except Exception as e:
        logger.debug(f"Working memory load failed: {e}")
        return "(working memory unavailable)"


# ── Nemotron Intent Decomposition ─────────────────────────────────────────────

# Available agent task types that WF1 SWARM_DISPATCH can route
AGENT_TASK_TYPES = {
    "analyse_chapter":      "Run full chapter analysis (Agents 2,4,5,8,9) via n8n",
    "validate_theology":    "Request theological guard check (Agent 9)",
    "extract_story_proto":  "Extract Role/Plot graph triples (Agent 8)",
    "refine_scene":         "Run self-refine loop on draft (Agent 11)",
    "kdp_assemble":         "Assemble KDP manuscript DOCX (Agent 7)",
    "constitution_update":  "Merge CRDT proposals into canon docs (Agent 3)",
    "cross_book_audit":     "Full cross-book continuity audit (Agent 10)",
    "image_prompt":         "Generate KDP image prompts (Agent 6)",
    "content_strategy":     "Generate social/SEO/serialization content (Agent 9 — Content Strategist)",
    "nz_grants":            "Scrape NZ literary grants and update opportunities log (Agent 9 — NZ Monitor)",
    "youtube_anchor":       "Generate YouTube anchor content brief (Agent 9 — Content Strategist)",
    "audiobook_assemble":   "Run full audiobook pre-production pipeline: sanitize → machine-ear → production manifest → hybrid diarization (port 8776)",
}


def decompose_intent(user_intent: str, book: str, chapter: str,
                     working_memory: str) -> list:
    """
    Ask Nemotron to decompose user_intent into an ordered task graph.
    Returns list of SubTask dicts: [{task_type, payload, depends_on, reason}].
    """
    available_types = "\n".join(
        f"  {k}: {v}" for k, v in AGENT_TASK_TYPES.items()
    )

    prompt = (
        "You are the Swarm Conductor for The Nephilim Chronicles creative AI system.\n"
        "Your job: decompose the user's intent into an ordered list of sub-tasks.\n\n"
        f"USER INTENT: {user_intent}\n"
        f"BOOK: {book}   CHAPTER: {chapter}\n\n"
        f"RECENT CHAPTER CONTEXT:\n{working_memory}\n\n"
        f"AVAILABLE TASK TYPES:\n{available_types}\n\n"
        "Rules:\n"
        "1. Only use task types from the list above.\n"
        "2. Order tasks so dependencies are respected (e.g., validate_theology before refine).\n"
        "3. Keep the plan minimal — only tasks that serve the intent.\n"
        "4. theological validation MUST precede any refine or assembly task.\n\n"
        "Output JSON array of tasks:\n"
        '[{"task_type":"...", "reason":"...", "payload":{}, "depends_on":null|"task_type"}]\n'
        "Only output the JSON, nothing else."
    )

    raw = ""
    try:
        r = requests.post(
            NEMOTRON_ROUTER + "/route",
            json={"task": "conduct_decompose", "prompt": prompt, "max_tokens": 600},
            timeout=120,
        )
        if r.status_code < 400:
            raw = r.json().get("response", "")
    except Exception as e:
        logger.warning(f"Nemotron decompose failed: {e}")

    # Parse
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        plan  = json.loads(clean)
        if isinstance(plan, list):
            # Validate each entry has required keys
            validated = []
            for item in plan:
                if isinstance(item, dict) and "task_type" in item:
                    if item["task_type"] in AGENT_TASK_TYPES:
                        validated.append(item)
            return validated
    except (json.JSONDecodeError, ValueError):
        logger.warning(f"Could not parse Nemotron plan: {raw[:200]}")

    # Fallback: minimal sensible plan for common intents
    lower = user_intent.lower()
    fallback = []
    if any(w in lower for w in ["draft", "write", "chapter"]):
        fallback = [
            {"task_type": "validate_theology", "reason": "Always validate before drafting",
             "payload": {}, "depends_on": None},
            {"task_type": "extract_story_proto", "reason": "Update role/plot graph",
             "payload": {}, "depends_on": "validate_theology"},
            {"task_type": "refine_scene", "reason": "Self-refine drafted content",
             "payload": {}, "depends_on": "extract_story_proto"},
        ]
    elif "audit" in lower:
        fallback = [
            {"task_type": "cross_book_audit", "reason": "User requested audit",
             "payload": {}, "depends_on": None},
        ]
    elif any(w in lower for w in ["kdp", "publish", "assemble", "docx"]):
        fallback = [
            {"task_type": "kdp_assemble", "reason": "User requested KDP assembly",
             "payload": {}, "depends_on": None},
        ]
    elif any(w in lower for w in ["audiobook", "audio", "diarize", "tts", "narrate"]):
        fallback = [
            {"task_type": "audiobook_assemble", "reason": "User requested audiobook pre-production",
             "payload": {}, "depends_on": None},
        ]
    else:
        fallback = [
            {"task_type": "analyse_chapter", "reason": "Default: full analysis",
             "payload": {}, "depends_on": None},
        ]

    logger.info(f"Using fallback plan: {[t['task_type'] for t in fallback]}")
    return fallback


# ── Dispatcher ────────────────────────────────────────────────────────────────

def dispatch_task(sub_task: dict, task_id: str, book: str, chapter: str) -> bool:
    """Post a sub-task to n8n WF1 SWARM_DISPATCH webhook."""
    payload = {
        "task_type":    sub_task["task_type"],
        "conductor_id": task_id,
        "book":         book,
        "chapter":      chapter,
        "payload":      sub_task.get("payload", {}),
        "reason":       sub_task.get("reason", ""),
    }
    try:
        r = requests.post(
            f"{N8N_BASE}/webhook/swarm-dispatch",
            json=payload,
            timeout=15,
        )
        if r.status_code < 400:
            logger.info(f"  Dispatched [{sub_task['task_type']}] → n8n [{r.status_code}]")
            return True
        else:
            logger.warning(f"  Dispatch failed [{sub_task['task_type']}]: HTTP {r.status_code}")
            return False
    except Exception as e:
        logger.warning(f"  Dispatch error [{sub_task['task_type']}]: {e}")
        return False


def run_conduct(task_id: str):
    """Background thread: decompose intent and dispatch tasks."""
    record = get_task(task_id)
    if not record:
        return

    update_task(task_id, status="planning")
    logger.info(f"[{task_id}] Planning intent: '{record['intent'][:80]}'")

    # Load Tier 1 working memory
    wm = load_working_memory(record["book"], record["chapter"])

    # Decompose
    plan = decompose_intent(
        record["intent"], record["book"], record["chapter"], wm
    )
    update_task(task_id, plan=plan, status="dispatching")

    logger.info(f"[{task_id}] Plan: {[t['task_type'] for t in plan]}")

    dispatched = []
    errors     = []

    for sub_task in plan:
        ok = dispatch_task(sub_task, task_id, record["book"], record["chapter"])
        if ok:
            dispatched.append(sub_task["task_type"])
        else:
            errors.append({"task_type": sub_task["task_type"], "error": "dispatch_failed"})

    final_status = "dispatched" if not errors else "partial"
    if len(errors) == len(plan):
        final_status = "failed"

    update_task(task_id,
                status=final_status,
                dispatched=dispatched,
                errors=errors)

    logger.info(f"[{task_id}] Conduct complete: status={final_status}, "
                f"dispatched={len(dispatched)}, errors={len(errors)}")


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class ConductorHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        logger.debug(fmt % args)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        data = self.rfile.read(length)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}

    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self.send_json(200, {
                "status":         "ok",
                "service":        "conductor",
                "port":           API_PORT,
                "active_tasks":   len(_tasks),
                "agent_task_types": list(AGENT_TASK_TYPES.keys()),
            })

        elif parsed.path == "/tasks":
            with _tasks_lock:
                summary = [
                    {k: v for k, v in t.items() if k != "plan"}
                    for t in _tasks.values()
                ]
            self.send_json(200, {"tasks": summary, "count": len(summary)})

        elif parsed.path.startswith("/task-status/"):
            task_id = parsed.path.split("/task-status/")[-1].strip("/")
            record  = get_task(task_id)
            if not record:
                self.send_json(404, {"error": f"Task {task_id!r} not found"})
            else:
                self.send_json(200, record)

        else:
            self.send_json(404, {"error": f"Unknown path: {self.path}"})

    def do_POST(self):
        parsed = urlparse(self.path)
        body   = self.read_body()

        if parsed.path == "/conduct":
            intent  = body.get("user_intent", "").strip()
            book    = str(body.get("book", "3"))
            chapter = str(body.get("chapter", "1"))
            context = body.get("context", "")

            if not intent:
                self.send_json(400, {"error": "user_intent required"})
                return

            record = new_task(intent, book, chapter)
            task_id = record["task_id"]

            # Run in background thread so we can return immediately
            t = threading.Thread(
                target=run_conduct, args=(task_id,), daemon=True
            )
            t.start()

            logger.info(f"Conduct task created: {task_id} | intent: '{intent[:60]}'")
            self.send_json(202, {
                "task_id":    task_id,
                "status":     "planning",
                "message":    "Task accepted — poll /task-status/{task_id} for completion",
            })

        elif parsed.path == "/task-complete":
            # Called by n8n agents to mark a sub-task done
            task_id   = body.get("conductor_id", "")
            task_type = body.get("task_type", "")

            if not task_id or not task_type:
                self.send_json(400, {"error": "conductor_id and task_type required"})
                return

            record = get_task(task_id)
            if not record:
                self.send_json(404, {"error": f"Task {task_id!r} not found"})
                return

            completed = record.get("completed", []) + [task_type]
            dispatched = record.get("dispatched", [])
            new_status = (
                "complete" if set(completed) >= set(dispatched) else "in_progress"
            )
            update_task(task_id, completed=completed, status=new_status)
            logger.info(f"[{task_id}] Sub-task complete: {task_type} | "
                        f"progress {len(completed)}/{len(dispatched)}")
            self.send_json(200, {"task_id": task_id, "status": new_status})

        else:
            self.send_json(404, {"error": f"Unknown path: {parsed.path}"})


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 60)
    print("  SWARM CONDUCTOR (Agent 0) — The Nephilim Chronicles v2.0")
    print(f"  Listening on http://localhost:{API_PORT}")
    print("  Endpoints:")
    print("    POST /conduct              — accept user intent")
    print("    GET  /task-status/{id}     — poll task state")
    print("    GET  /tasks                — list all active tasks")
    print("    POST /task-complete        — agent callback (sub-task done)")
    print("    GET  /health               — service health")
    print(f"  Agent task types: {', '.join(AGENT_TASK_TYPES.keys())}")
    print("═" * 60 + "\n")

    server = HTTPServer(("", API_PORT), ConductorHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down Swarm Conductor.")
        server.server_close()


if __name__ == "__main__":
    main()
