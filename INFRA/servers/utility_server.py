"""
DESKTOP-SINGULA — Utility Server (port 8769)
=============================================
HTTP wrapper around three CLI-only scripts so n8n workflows can call them
without needing Python inside the Docker container.

Endpoints:
    POST /crdt-merge          — run crdt_merge.run_merge()
    POST /self-refine         — run self_refine_loop.refine() on a chapter
    POST /cross-book-audit    — run cross_book_audit.run_audit()
    GET  /health              — service health check

Usage:
    python utility_server.py
"""

import json
import sys
import os
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
API_PORT     = 8769

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [UTILITY] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("utility_server")


# ── Response Helpers ────────────────────────────────────────────────────────

def send_json(handler, data: dict, status: int = 200):
    body = json.dumps(data, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_body(handler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


# ── Route Handlers ──────────────────────────────────────────────────────────

def handle_health(handler):
    send_json(handler, {
        "status":    "ok",
        "service":   "utility_server",
        "version":   "2.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/crdt-merge", "/self-refine", "/cross-book-audit"],
    })


def handle_crdt_merge(handler, body: dict):
    """
    POST /crdt-merge
    Body: { "staging_dir": "...", "dry_run": false, "verbose": false }
    """
    import crdt_merge

    staging_dir = body.get("staging_dir", str(PROJECT_ROOT / "STAGING" / "crdt_proposals"))
    dry_run     = bool(body.get("dry_run", False))
    verbose     = bool(body.get("verbose", False))

    logger.info(f"CRDT merge: staging_dir={staging_dir} dry_run={dry_run}")

    try:
        report = crdt_merge.run_merge(staging_dir, dry_run=dry_run, verbose=verbose)
        if report is None:
            report = {"total_proposals": 0, "note": "Nothing to merge"}

        send_json(handler, {
            "status":  "ok",
            "report":  report,
            "dry_run": dry_run,
        })
    except Exception as e:
        logger.error(f"CRDT merge error: {e}")
        send_json(handler, {"status": "error", "error": str(e)}, 500)


def handle_self_refine(handler, body: dict):
    """
    POST /self-refine
    Body: {
        "draft_path": "/data/TNC/MANUSCRIPT/book_3/CH07.md",   // OR
        "draft_text": "Raw prose text...",
        "book": 3, "chapter": 7,
        "author_notes": "...",
        "max_iter": 3, "threshold": 85.0
    }
    """
    import self_refine_loop

    # Resolve draft text
    draft_path = body.get("draft_path")
    draft_text = body.get("draft_text", "")

    if draft_path and not draft_text:
        # n8n sends container path (/data/TNC/...); translate to host path
        p = Path(draft_path.replace("/data/TNC", str(PROJECT_ROOT), 1))
        if p.exists():
            draft_text = p.read_text(encoding="utf-8")
        else:
            send_json(handler, {"status": "error", "error": f"File not found: {p}"}, 400)
            return

    if not draft_text.strip():
        send_json(handler, {"status": "error", "error": "No draft text provided"}, 400)
        return

    book           = int(body.get("book", 1))
    chapter        = int(body.get("chapter", 1))
    author_notes   = body.get("author_notes", "")
    max_iterations = int(body.get("max_iter", 3))
    threshold      = float(body.get("threshold", 85.0))

    logger.info(f"SELF-REFINE: Book {book} Ch {chapter} max_iter={max_iterations} threshold={threshold}")

    try:
        refined_draft, report = self_refine_loop.refine(
            initial_draft  = draft_text,
            book           = book,
            chapter        = chapter,
            author_notes   = author_notes,
            max_iterations = max_iterations,
            pass_threshold = threshold,
        )

        # Optionally write refined draft back to file
        if draft_path and body.get("write_back", False):
            out_path = Path(draft_path.replace("/data/TNC", str(PROJECT_ROOT), 1))
            refined_path = out_path.with_stem(out_path.stem + "_refined")
            refined_path.write_text(refined_draft, encoding="utf-8")
            report["refined_path"] = str(refined_path)

        send_json(handler, {
            "status":        "ok",
            "passed":        report.get("passed", False),
            "final_score":   report.get("final_score", 0),
            "iterations":    report.get("iterations", 0),
            "refined_draft": refined_draft,
            "report":        report,
        })
    except Exception as e:
        logger.error(f"SELF-REFINE error: {e}")
        send_json(handler, {"status": "error", "error": str(e)}, 500)


def handle_cross_book_audit(handler, body: dict):
    """
    POST /cross-book-audit
    Body: {
        "books": [3, 4, 5],        // which books to audit
        "fast": false,
        "single_chapter": null     // or "/data/TNC/MANUSCRIPT/book_3/CH07.md"
    }
    """
    import cross_book_audit

    books  = body.get("books", [3, 4, 5])
    fast   = bool(body.get("fast", False))
    single = body.get("single_chapter")

    if single:
        single = single.replace("/data/TNC", str(PROJECT_ROOT), 1)

    logger.info(f"CROSS-BOOK AUDIT: books={books} fast={fast}")

    try:
        result = cross_book_audit.run_audit(
            books          = [int(b) for b in books],
            fast           = fast,
            single_chapter = single,
        )

        violations = result.get("violations", [])
        critical   = [v for v in violations if v.get("severity") == "CRITICAL"]

        send_json(handler, {
            "status":          "ok",
            "books_audited":   books,
            "violation_count": len(violations),
            "critical_count":  len(critical),
            "summary":         result.get("summary", ""),
            "violations":      violations,
        })
    except Exception as e:
        logger.error(f"Cross-book audit error: {e}")
        send_json(handler, {"status": "error", "error": str(e)}, 500)


# ── Request Handler ─────────────────────────────────────────────────────────

class UtilityHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        logger.info(f"{self.address_string()} {fmt % args}")

    def do_GET(self):
        if self.path in ("/health", "/"):
            handle_health(self)
        else:
            send_json(self, {"error": f"Unknown GET path: {self.path}"}, 404)

    def do_POST(self):
        body = read_body(self)
        path = self.path.split("?")[0]

        if path == "/crdt-merge":
            handle_crdt_merge(self, body)
        elif path == "/self-refine":
            handle_self_refine(self, body)
        elif path == "/cross-book-audit":
            handle_cross_book_audit(self, body)
        else:
            send_json(self, {"error": f"Unknown POST path: {path}"}, 404)


# ── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    logger.info(f"Utility Server starting on port {API_PORT}")
    logger.info(f"Project root: {PROJECT_ROOT}")

    server = HTTPServer(("0.0.0.0", API_PORT), UtilityHandler)
    logger.info(f"Utility Server ready — http://localhost:{API_PORT}/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Utility Server shutting down")
        server.server_close()
