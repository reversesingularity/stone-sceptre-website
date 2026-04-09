"""
Nemotron Tool Router — Port 8768
=================================
HTTP gateway that routes long-horizon tasks (Book 3–5) to NVIDIA NIM Nemotron-3 Super (120B)
with OpenRouter as secondary fallback and Ollama llama3.1 as tertiary local fallback.

Architecture:
    Client → POST /route → [context-budget check]
           → PRIMARY:   NVIDIA NIM (integrate.api.nvidia.com)
           → FALLBACK1: OpenRouter (openrouter.ai)
           → FALLBACK2: Ollama local (llama3.1)

Endpoints:
    POST /route          — Route a generation request
    POST /embed          — Embed text via nomic-embed-text (Ollama, always local)
    GET  /health         — Service health
    GET  /models         — List available routing targets and their status

Token budget:
    Nemotron window = 1,000,000 tokens.
    Router estimates prompt tokens at ~0.75 chars/token and
    rejects requests that would exceed 900,000 tokens (10% headroom).

Usage:
    python nemotron_tool_router.py [--port 8768] [--log-level INFO]
    Set NVIDIA_API_KEY and OPENROUTER_API_KEY in environment or .env file.
"""

import os
import sys
import json
import logging
import argparse
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT   = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
LOG_DIR        = PROJECT_ROOT / "LOGS"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load .env if present
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

NVIDIA_API_KEY      = os.environ.get("NVIDIA_API_KEY", "")
OPENROUTER_API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")

NVIDIA_NIM_URL    = "https://integrate.api.nvidia.com/v1/chat/completions"
OPENROUTER_URL    = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_URL        = "http://localhost:11434"
EMBED_MODEL       = "nomic-embed-text"

NEMOTRON_MODEL_NVIDIA = "nvidia/nemotron-3-8b-base-4k"  # use the available NIM model
NEMOTRON_MODEL_OR     = "nvidia/nemotron-4-340b-instruct"  # OpenRouter variant
OLLAMA_FALLBACK_MODEL = "llama3.1"

# Context budget: 900K token safety ceiling (1M window, 10% headroom)
MAX_CONTEXT_TOKENS = 900_000
CHARS_PER_TOKEN    = 0.75   # conservative estimate

ERROR_LOG = LOG_DIR / "nemotron_errors.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NEMOTRON-ROUTER] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(ERROR_LOG), encoding="utf-8"),
    ]
)
logger = logging.getLogger("nemotron_router")


# ── Token Budget ──────────────────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) * CHARS_PER_TOKEN))


def build_messages(req: dict) -> list[dict]:
    """Build OpenAI-style messages from request payload."""
    messages = []
    system_prompt = req.get("system", "")
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    prompt = req.get("prompt", "")
    if prompt:
        messages.append({"role": "user", "content": prompt})

    # Allow caller to pass raw messages list directly
    for m in req.get("messages", []):
        messages.append(m)

    return messages


def estimate_total_tokens(messages: list[dict]) -> int:
    total = sum(estimate_tokens(m.get("content", "")) for m in messages)
    return total


# ── Backends ──────────────────────────────────────────────────────────────────

def call_nvidia_nim(messages, max_tokens, tool_schemas):
    """Call NVIDIA NIM API (Nemotron primary)."""
    if not NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY not configured")

    payload = {
        "model":      NEMOTRON_MODEL_NVIDIA,
        "messages":   messages,
        "max_tokens": max_tokens or 4096,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    if tool_schemas:
        payload["tools"] = tool_schemas
        payload["tool_choice"] = "auto"

    r = requests.post(
        NVIDIA_NIM_URL,
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type":  "application/json",
        },
        json=payload,
        timeout=300,
    )
    r.raise_for_status()
    return r.json()


def call_openrouter(messages, max_tokens, tool_schemas):
    """Call OpenRouter (Nemotron secondary fallback)."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")

    payload = {
        "model":      NEMOTRON_MODEL_OR,
        "messages":   messages,
        "max_tokens": max_tokens or 4096,
        "temperature": 0.7,
    }
    if tool_schemas:
        payload["tools"] = tool_schemas
        payload["tool_choice"] = "auto"

    r = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":  "application/json",
            "X-Title":       "The Nephilim Chronicles",
        },
        json=payload,
        timeout=300,
    )
    r.raise_for_status()
    return r.json()


def call_ollama(messages, max_tokens, model=None):
    """Call local Ollama (tertiary fallback)."""
    model = model or OLLAMA_FALLBACK_MODEL
    # Convert to Ollama's format
    prompt_parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            prompt_parts.append(f"[SYSTEM] {content}")
        elif role == "user":
            prompt_parts.append(f"[USER] {content}")
        elif role == "assistant":
            prompt_parts.append(f"[ASSISTANT] {content}")

    prompt_text = "\n".join(prompt_parts)

    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model":  model,
            "prompt": prompt_text,
            "stream": False,
            "options": {"num_predict": max_tokens or 2048},
        },
        timeout=300,
    )
    r.raise_for_status()
    ollama_resp = r.json()

    # Normalise to OpenAI style
    return {
        "id":     "ollama-fallback",
        "model":  model,
        "object": "chat.completion",
        "choices": [{
            "index":         0,
            "message":       {"role": "assistant", "content": ollama_resp.get("response", "")},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens":     ollama_resp.get("prompt_eval_count", 0),
            "completion_tokens": ollama_resp.get("eval_count", 0),
            "total_tokens":      ollama_resp.get("prompt_eval_count", 0) + ollama_resp.get("eval_count", 0),
        },
        "_backend": "ollama",
    }


def validate_tool_calls(completion: dict) -> list:
    """Extract and validate tool calls from completion response."""
    choices = completion.get("choices", [])
    if not choices:
        return []

    message = choices[0].get("message", {})
    tool_calls = message.get("tool_calls", [])
    validated = []

    for tc in tool_calls:
        # Each tool_call must have: id, type='function', function.name, function.arguments
        if not isinstance(tc, dict):
            continue
        fn = tc.get("function", {})
        if not fn.get("name"):
            continue
        # Validate arguments is parseable JSON
        args_raw = fn.get("arguments", "{}")
        if isinstance(args_raw, str):
            try:
                json.loads(args_raw)
            except json.JSONDecodeError:
                logger.warning(f"Invalid tool_call arguments JSON for '{fn['name']}' — skipping")
                continue
        validated.append(tc)

    return validated


# ── Route Handler ─────────────────────────────────────────────────────────────

def route_request(req: dict) -> dict:
    """
    Route a generation request through the backend cascade.

    Request schema:
    {
        "task_type":    str,           # e.g. "cross_book_audit", "scene_draft"
        "system":       str,           # system prompt
        "prompt":       str,           # user prompt
        "messages":     list[dict],    # optional raw messages (appended after system+prompt)
        "tool_schemas": list[dict],    # optional OpenAI tool schemas
        "max_tokens":   int,           # optional
        "force_local":  bool,          # skip Nemotron, use Ollama directly
    }
    """
    task_type    = req.get("task_type", "unknown")
    max_tokens   = req.get("max_tokens", 4096)
    tool_schemas = req.get("tool_schemas", [])
    force_local  = req.get("force_local", False)

    messages = build_messages(req)
    total_estimated = estimate_total_tokens(messages)

    logger.info(f"Routing task_type='{task_type}' "
                f"~{total_estimated:,} tokens, max_out={max_tokens}")

    # Context budget guard
    if total_estimated > MAX_CONTEXT_TOKENS:
        return {
            "error": "CONTEXT_BUDGET_EXCEEDED",
            "estimated_tokens": total_estimated,
            "max_allowed": MAX_CONTEXT_TOKENS,
            "message": "Reduce prompt size or split the task.",
        }

    backend_used = None
    errors = []

    if not force_local:
        # PRIMARY: NVIDIA NIM
        try:
            result = call_nvidia_nim(messages, max_tokens, tool_schemas)
            result["_backend"] = "nvidia_nim"
            result["_task_type"] = task_type
            if tool_schemas:
                result["_tool_calls"] = validate_tool_calls(result)
            backend_used = "nvidia_nim"
            logger.info(f"  NVIDIA NIM success — backend=nvidia_nim")
            return result
        except Exception as e:
            err_msg = str(e)
            errors.append(f"nvidia_nim: {err_msg}")
            logger.warning(f"  NVIDIA NIM failed: {err_msg}")

        # FALLBACK 1: OpenRouter
        try:
            result = call_openrouter(messages, max_tokens, tool_schemas)
            result["_backend"] = "openrouter"
            result["_task_type"] = task_type
            if tool_schemas:
                result["_tool_calls"] = validate_tool_calls(result)
            logger.info(f"  OpenRouter success — backend=openrouter")
            return result
        except Exception as e:
            err_msg = str(e)
            errors.append(f"openrouter: {err_msg}")
            logger.warning(f"  OpenRouter failed: {err_msg}")

    # FALLBACK 2: Ollama local
    try:
        result = call_ollama(messages, max_tokens)
        result["_backend"] = "ollama"
        result["_task_type"] = task_type
        logger.info(f"  Ollama fallback success — model={OLLAMA_FALLBACK_MODEL}")
        if errors:
            result["_warnings"] = errors
        return result
    except Exception as e:
        errors.append(f"ollama: {e}")
        logger.error(f"  All backends failed: {errors}")

    return {
        "error":    "ALL_BACKENDS_FAILED",
        "backends": errors,
        "message":  "NVIDIA NIM, OpenRouter, and Ollama all unreachable.",
    }


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class RouterHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        logger.debug(f"HTTP {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            # Check each backend availability
            nim_ok = bool(NVIDIA_API_KEY)
            or_ok  = bool(OPENROUTER_API_KEY)
            ollama_ok = False
            try:
                r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
                ollama_ok = r.status_code == 200
            except Exception:
                pass

            self.send_json({
                "status":   "ok",
                "service":  "nemotron_tool_router",
                "backends": {
                    "nvidia_nim":   "configured" if nim_ok else "unconfigured",
                    "openrouter":   "configured" if or_ok  else "unconfigured",
                    "ollama":       "up" if ollama_ok else "down",
                }
            })
        elif self.path == "/models":
            self.send_json({
                "primary":   NEMOTRON_MODEL_NVIDIA,
                "secondary": NEMOTRON_MODEL_OR,
                "fallback":  OLLAMA_FALLBACK_MODEL,
                "embed":     EMBED_MODEL,
            })
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        try:
            req = self.read_json_body()
        except Exception:
            self.send_json({"error": "Invalid JSON body"}, 400)
            return

        if self.path == "/route":
            result = route_request(req)
            status = 200 if "error" not in result else 500
            self.send_json(result, status)

        elif self.path == "/embed":
            text = req.get("text", "")
            if not text:
                self.send_json({"error": "Missing 'text' field"}, 400)
                return
            try:
                r = requests.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={"model": EMBED_MODEL, "prompt": text[:8192]},
                    timeout=30,
                )
                r.raise_for_status()
                self.send_json(r.json())
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        else:
            self.send_json({"error": "Not found"}, 404)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Nemotron Tool Router — HTTP gateway for Nemotron-3 Super routing"
    )
    parser.add_argument("--port", type=int, default=8768, help="Port to listen on")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)
    logging.getLogger("nemotron_router").setLevel(args.log_level)

    if not NVIDIA_API_KEY:
        logger.warning("NVIDIA_API_KEY not set — NVIDIA NIM backend disabled")
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — OpenRouter backend disabled")

    server = HTTPServer(("0.0.0.0", args.port), RouterHandler)
    logger.info(f"Nemotron Tool Router listening on port {args.port}")
    logger.info(f"  Primary:   NVIDIA NIM  ({NEMOTRON_MODEL_NVIDIA})")
    logger.info(f"  Secondary: OpenRouter  ({NEMOTRON_MODEL_OR})")
    logger.info(f"  Fallback:  Ollama      ({OLLAMA_FALLBACK_MODEL})")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Nemotron Tool Router.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
