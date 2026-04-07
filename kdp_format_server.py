"""
kdp_format_server.py
--------------------
HTTP wrapper around build_manuscript.py.
Exposes a POST /kdp-format endpoint on port 8766 so n8n can trigger
KDP DOCX assembly via webhook without a terminal session.

Endpoint:
    POST http://localhost:8766/kdp-format
    Body (JSON, optional):
        {
          "book": 1,                          // 1 or 2 (default 1)
          "manuscript_dir": "path/override",  // optional override
          "output_file": "path/override"      // optional override
        }

    GET  http://localhost:8766/health         // health check

Response (JSON):
    {
      "status": "ok",
      "output_file": "path/to/docx",
      "elapsed_seconds": 12.3,
      "log": "..."
    }

Usage:
    python kdp_format_server.py
"""

import subprocess
import sys
import json
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — must match build_manuscript.py defaults
# ---------------------------------------------------------------------------

SERVER_PORT = 8766

# Book 1 defaults
BOOK1_DIR = Path(r"f:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_1")
BOOK1_OUT = Path(r"f:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\NephilimChronicles_Book1_MANUSCRIPT.docx")

# Book 2 defaults
BOOK2_DIR = Path(r"f:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\MANUSCRIPT\book_2\CHAPTERS")
BOOK2_OUT = Path(r"f:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\NephilimChronicles_Book2_MANUSCRIPT.docx")

# Path to build_manuscript.py
BUILD_SCRIPT = Path(__file__).parent / "build_manuscript.py"

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def run_build(book: int, manuscript_dir: str | None, output_file: str | None) -> dict:
    """
    Run build_manuscript.py as a subprocess with env overrides.
    Returns dict with status, output_file, elapsed_seconds, log.
    """
    if book == 2:
        m_dir = manuscript_dir or str(BOOK2_DIR)
        o_file = output_file or str(BOOK2_OUT)
    else:
        m_dir = manuscript_dir or str(BOOK1_DIR)
        o_file = output_file or str(BOOK1_OUT)

    env = os.environ.copy()
    env["KDP_BOOK"] = str(book)
    env["KDP_MANUSCRIPT_DIR"] = m_dir
    env["KDP_OUTPUT_FILE"] = o_file
    env["PYTHONIOENCODING"] = "utf-8"

    start = time.time()
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        timeout=300
    )
    elapsed = round(time.time() - start, 1)

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    log = stdout + ("\n" + stderr if stderr else "")

    if result.returncode == 0:
        return {
            "status": "ok",
            "output_file": o_file,
            "elapsed_seconds": elapsed,
            "log": log
        }
    else:
        return {
            "status": "error",
            "output_file": None,
            "elapsed_seconds": elapsed,
            "log": log,
            "returncode": result.returncode
        }


# ---------------------------------------------------------------------------
# REQUEST HANDLER
# ---------------------------------------------------------------------------

class KDPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[KDP] {self.address_string()} — {format % args}")

    def send_json(self, code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "service": "kdp-format-server", "port": SERVER_PORT})
        else:
            self.send_json(404, {"error": "Not found", "endpoints": ["POST /kdp-format", "GET /health"]})

    def do_POST(self):
        if self.path != "/kdp-format":
            self.send_json(404, {"error": "Unknown endpoint"})
            return

        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = {}
        if length > 0:
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                body = {}

        book = int(body.get("book", 1))
        manuscript_dir = body.get("manuscript_dir")
        output_file = body.get("output_file")

        print(f"[KDP] Build request: book={book} manuscript_dir={manuscript_dir} output={output_file}")

        try:
            result = run_build(book, manuscript_dir, output_file)
        except subprocess.TimeoutExpired:
            result = {"status": "error", "log": "Timeout (300s exceeded)", "output_file": None}
        except Exception as e:
            result = {"status": "error", "log": str(e), "output_file": None}

        code = 200 if result["status"] == "ok" else 500
        self.send_json(code, result)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", SERVER_PORT), KDPHandler)
    print(f"[KDP] Server listening on port {SERVER_PORT}")
    print(f"[KDP] POST http://localhost:{SERVER_PORT}/kdp-format")
    print(f"[KDP] GET  http://localhost:{SERVER_PORT}/health")
    print(f"[KDP] Build script: {BUILD_SCRIPT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[KDP] Shutting down.")
        server.server_close()
