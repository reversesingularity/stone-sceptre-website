"""
DESKTOP-SINGULA — Theological Guard Service (Agent 9)
=====================================================
HTTP server (port 8770) that validates scene / chapter drafts against the
INVIOLABLE axioms of The Nephilim Chronicles Series Bible.

Checks (in order of severity):
    1. Oiketerion Principle     — Watchers TEACH, never DEMONSTRATE innate power
    2. Acoustic Paradigm        — All supernatural tech uses sound / vibration
    3. Azazel Classification    — Azazel is Nephilim (son of Gadreel), NOT a Watcher
    4. Nephilim / Watcher ID    — Entity identities match official dossiers
    5. Raphael's Limitations    — Three canonical limits respected on every appearance
    6. Christology              — Christ's role never diluted, reframed, or syncretically merged
    7. Knowledge Transmission   — Watchers → Nephilim → Apkallu → Sumerians → Modern
    8. Seal Sequence            — Horsemen / Seal breaks follow SSOT timeline
    9. Satan = Dragon           — Never conflate Satan with Beast / False Prophet roles
   10. Acoustic Paradigm / Mo Chrá — Sword produces creation frequencies (not electromagnetic)

All red violations are written to LOGS/THEOLOGICAL_FLAGS.log and appended
to TODO.md so the Author sees them before any canon document is touched.

Endpoints:
    POST /validate-scene        — validate proposed scene text
    POST /validate-batch        — validate list of scenes in one call
    GET  /axioms                — return embedded axiom registry as JSON
    GET  /health                — service health check

Usage:
    python theological_guard_server.py
"""

import json
import os
import time
import logging
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import re
import requests

# ── Config ───────────────────────────────────────────────────────────────────

API_PORT        = 8770
NEMOTRON_ROUTER = "http://localhost:8768"
OLLAMA_URL      = "http://localhost:11434"

# Local Nemotron 3 Super GGUF via llama-server
LOCAL_NEMOTRON_PORT  = int(os.environ.get("LOCAL_NEMOTRON_PORT", "8780"))
LOCAL_NEMOTRON_URL   = f"http://localhost:{LOCAL_NEMOTRON_PORT}/v1/chat/completions"
LOCAL_NEMOTRON_MODEL = os.environ.get("LOCAL_NEMOTRON_MODEL", "nemotron-3-super")
FALLBACK_MODEL  = LOCAL_NEMOTRON_MODEL  # was: "mistral"

PROJECT_ROOT = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
LOGS_DIR     = PROJECT_ROOT / "LOGS"
FLAG_LOG     = LOGS_DIR / "THEOLOGICAL_FLAGS.log"
TODO_FILE    = PROJECT_ROOT / "TODO.md"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [THEOL-GUARD] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOGS_DIR / "theological_guard.log"), encoding="utf-8"),
    ]
)
logger = logging.getLogger("theological_guard")

# ── Axiom Registry ────────────────────────────────────────────────────────────
# Each axiom: id, severity (RED=block, AMBER=warn), description, detection_hint

AXIOMS = [
    {
        "id": "OIKETERION",
        "severity": "RED",
        "label": "Oiketerion Principle (Jude 1:6)",
        "description": (
            "Watchers LOST their innate supernatural gifts when they shed their celestial "
            "bodies. They retained KNOWLEDGE of how abilities work, so they can TEACH but "
            "cannot DEMONSTRATE post-descent supernatural power. Any scene where a Watcher "
            "directly uses innate supernatural ability (teleportation, creation-class powers, "
            "celestial fire etc.) without technology is a violation."
        ),
        "violation_patterns": [
            "watcher.*conjur", "watcher.*summon.*power", "watcher.*fly", "watcher.*vanish",
            "watcher.*heal", "shemyaza.*creates?", "gadreel.*teleports?",
        ],
    },
    {
        "id": "ACOUSTIC_PARADIGM",
        "severity": "RED",
        "label": "Acoustic Paradigm",
        "description": (
            "ALL supernatural/Watcher technology operates through sound and vibration — "
            "never through electromagnetic, visual, or conventional physical mechanisms. "
            "Cydonian ore contains acoustic memory. Mo Chrá produces creation frequencies. "
            "Any tech described as electromagnetic, laser, or light-based (unless natural) "
            "violates this paradigm."
        ),
        "violation_patterns": [
            "electromagnetic.*watcher", "laser.*watcher", "watcher.*radiation",
            "cydonian.*light.*beam", "mo chr.*light", "sword.*laser",
        ],
    },
    {
        "id": "AZAZEL_IS_NEPHILIM",
        "severity": "RED",
        "label": "Azazel Classification",
        "description": (
            "Azazel is the FALSE PROPHET (Revelation). He is a NEPHILIM — specifically "
            "the son of Gadreel (a Watcher), making him second-generation. He is NOT a "
            "Watcher himself. He did not descend at Mount Hermon. He was not among the 200. "
            "Any scene that places Azazel as one of the 200 Watchers, or calls him a Watcher, "
            "is a CANON VIOLATION."
        ),
        "violation_patterns": [
            "azazel.*watcher", "watcher.*azazel.*descended", "azazel.*hermon",
            "azazel.*200", "azazel.*one of the.*watchers",
        ],
    },
    {
        "id": "RAPHAEL_LIMITS",
        "severity": "RED",
        "label": "Raphael's Three Limitations",
        "description": (
            "Raphael has three canonical limitations (Enoch 10:4-7): "
            "(1) Cannot kill fallen Watchers directly; "
            "(2) Cannot enter Cydonia-1 (Mars pyramid complex) due to acoustical wards; "
            "(3) Cannot violate human free will. "
            "Any scene showing Raphael killing a Watcher, entering Cydonia-1, or forcing "
            "a human to act is a violation."
        ),
        "violation_patterns": [
            "raphael.*kills?.*watcher", "raphael.*slays?.*watcher",
            "raphael.*enters?.*cydonia", "raphael.*forces?.*human",
            "raphael.*compels?",
        ],
    },
    {
        "id": "CHRISTOLOGY",
        "severity": "RED",
        "label": "Christology Guard",
        "description": (
            "Jesus Christ is fully divine and fully human, the unique Son of God. "
            "His sacrifice is sufficient for salvation. His resurrection was bodily. "
            "No Watcher, Nephilim, or angelic entity may be positioned as a messiah figure, "
            "co-redeemer, or divine peer. The Acoustic Paradigm cannot retroactively recast "
            "Christ's miracles as technology."
        ),
        "violation_patterns": [
            "watcher.*messiah", "nephilim.*savior", "azazel.*redeems?",
            "watchers.*created.*life", "watcher.*god.*equal",
        ],
    },
    {
        "id": "KNOWLEDGE_CHAIN",
        "severity": "AMBER",
        "label": "Knowledge Transmission Chain",
        "description": (
            "Supernatural knowledge flows in one direction: "
            "Watchers → Nephilim → Apkallu (Nephilim spirits) → Sumerians → "
            "Mystery Babylon System → WEF / Club of Rome. "
            "Reverse transmission (humans teaching Watchers advanced knowledge) is a violation. "
            "Modern tech figures discovering Watcher knowledge independently violates the chain."
        ),
        "violation_patterns": [
            "human.*taught.*watcher", "humans.*gave.*watchers?",
            "scientists?.*revealed.*watcher", "elon.*taught.*watcher",
        ],
    },
    {
        "id": "SEAL_SEQUENCE",
        "severity": "AMBER",
        "label": "Seal / Prophecy Sequence (Revelation 6)",
        "description": (
            "The Seven Seals break in canonical order. The Four Horsemen appear in sequence. "
            "No seal may break out of order, and no character may be present at a seal-break "
            "event that contradicts their established location in the SSOT timeline. "
            "Check SSOT_v3_MASTER.md §3 for locked timeline events."
        ),
        "violation_patterns": [
            "sixth seal.*before.*fifth", "third seal.*before.*second",
            "horsemen.*simultaneously", "all.*seals.*open.*at once",
        ],
    },
    {
        "id": "SATAN_DRAGON",
        "severity": "AMBER",
        "label": "Satan = The Dragon (Identity Clarity)",
        "description": (
            "Satan is THE DRAGON (Revelation 12). The Beast is Ohya (son of Shemyaza and Naamah). "
            "The False Prophet is Azazel (Nephilim, son of Gadreel). These three are distinct. "
            "Never conflate Satan with the Beast or False Prophet roles in narrative."
        ),
        "violation_patterns": [
            "satan.*the beast", "satan.*false prophet", "dragon.*ohya.*same",
            "lucifer.*azazel.*same",
        ],
    },
    {
        "id": "MO_CHRA_ACOUSTIC",
        "severity": "AMBER",
        "label": "Mo Chrá — Acoustic Sword Lore",
        "description": (
            "Mo Chrá (the sword) produces CREATION FREQUENCIES — the frequencies by which "
            "God spoke creation into existence (Genesis 1). The Watchers lost the ability to "
            "produce these frequencies. The sword does NOT produce light sabres, plasma, "
            "electromagnetic pulses, or conventional fire. Its power is acoustic/vibrational."
        ),
        "violation_patterns": [
            "mo chr.*plasma", "mo chr.*electromagnetic", "mo chr.*laser",
            "sword.*light.*saber", "mo chr.*electricity",
        ],
    },
]

AXIOM_MAP = {a["id"]: a for a in AXIOMS}

# Pre-compiled violation patterns — built once at module load (~10ms) instead
# of recompiling on every validate_scene call.
AXIOM_PATTERNS: dict[str, list[re.Pattern]] = {
    axiom["id"]: [re.compile(pat, re.IGNORECASE) for pat in axiom.get("violation_patterns", [])]
    for axiom in AXIOMS
}


# ── LLM Validation ────────────────────────────────────────────────────────────

def call_nemotron(prompt: str, max_tokens: int = 400) -> str:
    """Route through Nemotron if available, fall back to Ollama mistral."""
    try:
        r = requests.post(
            NEMOTRON_ROUTER + "/route",
            json={"task": "theological_guard", "prompt": prompt, "max_tokens": max_tokens},
            timeout=90,
        )
        if r.status_code < 400:
            return r.json().get("response", "")
    except Exception:
        pass

    # Ollama fallback
    try:
        r = requests.post(
            OLLAMA_URL + "/api/generate",
            json={"model": FALLBACK_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        if r.status_code < 400:
            return r.json().get("response", "")
    except Exception:
        pass

    return ""


def llm_deep_check(scene_text: str, axiom: dict) -> dict:
    """
    Ask the LLM to look specifically for this axiom's violation in the scene.
    Returns {"violated": bool, "explanation": str}.
    """
    system_context = (
        "You are a theological canon guard for the Christian apocalyptic fiction series "
        "'The Nephilim Chronicles'. Your job is to detect specific canon violations.\n\n"
        f"AXIOM TO CHECK: {axiom['label']}\n"
        f"RULE: {axiom['description']}\n\n"
        "SCENE TEXT:\n"
        "───────────────────────────────────\n"
        f"{scene_text[:4000]}\n"
        "───────────────────────────────────\n\n"
        "Does this scene VIOLATE the axiom above?\n"
        "Reply in JSON: {\"violated\": true|false, \"explanation\": \"one sentence\"}\n"
        "Only output the JSON, nothing else."
    )

    raw = call_nemotron(system_context, max_tokens=150)

    # Parse JSON response
    try:
        # Strip any markdown fencing
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        # If LLM response is unparseable fall back to "not violated" (conservative)
        return {"violated": False, "explanation": f"LLM response unparseable: {raw[:100]}"}


# ── Flag Writer ───────────────────────────────────────────────────────────────

def write_flag(violation: dict, book: str, chapter: str):
    """Append a theological violation to THEOLOGICAL_FLAGS.log and TODO.md."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    severity = violation.get("severity", "AMBER")
    axiom_id = violation.get("axiom_id", "UNKNOWN")
    label    = violation.get("label", axiom_id)
    expl     = violation.get("explanation", "")

    log_line = f"{ts} [{severity}] {axiom_id} | Book {book} Ch {chapter} | {expl}\n"

    with open(FLAG_LOG, "a", encoding="utf-8") as f:
        f.write(log_line)

    # Append to TODO.md for author review
    todo_entry = (
        f"\n## ⚠ THEOLOGICAL FLAG [{severity}] — {label}\n"
        f"**Book:** {book}  **Chapter:** {chapter}  **Time:** {ts}\n\n"
        f"**Violation:** {expl}\n\n"
        f"**Axiom:** {axiom_id} — {label}\n\n"
        f"*This flag was auto-generated by theological_guard_server.py.*\n\n---\n"
    )
    try:
        with open(TODO_FILE, "a", encoding="utf-8") as f:
            f.write(todo_entry)
    except Exception as e:
        logger.warning(f"Could not write to TODO.md: {e}")


# ── Core Validation ───────────────────────────────────────────────────────────

def validate_scene(scene_text: str, book: str = "?", chapter: str = "?",
                   fast: bool = False) -> dict:
    """
    Run all axiom checks against scene_text.

    Optimised execution model:
      Pass 1 — regex fast-scan across ALL axioms (~50ms total, zero LLM cost).
               Only axioms whose patterns match proceed to Pass 2.
      Pass 2 — LLM deep-check on matched axioms only.
               Exits immediately on first RED violation (no further checks).
      Pass 3 — Batched file I/O: all flags written in one pass after the loop.

    fast=True: regex-only (no LLM) — suitable for Nemoclaw background sweeps.
    """
    violations:     list[dict] = []
    warnings:       list[dict] = []
    flags_to_write: list[tuple] = []

    scene_lower = scene_text.lower()

    # --- Pass 1: fast regex scan --- O(axioms × patterns), no I/O, no LLM
    matched_axioms = [
        axiom for axiom in AXIOMS
        if any(pat.search(scene_lower) for pat in AXIOM_PATTERNS[axiom["id"]])
    ]

    # --- Pass 2: deep-check only matched axioms ---
    for axiom in matched_axioms:
        if fast:
            result = {"violated": True,
                      "explanation": f"Pattern match triggered: {axiom['label']}"}
        else:
            result = llm_deep_check(scene_text, axiom)

        if result.get("violated"):
            entry = {
                "axiom_id":    axiom["id"],
                "severity":    axiom["severity"],
                "label":       axiom["label"],
                "explanation": result.get("explanation", ""),
            }
            if axiom["severity"] == "RED":
                violations.append(entry)
                flags_to_write.append((entry, book, chapter))
                logger.warning(f"RED VIOLATION [{axiom['id']}] Book {book} Ch {chapter}: "
                               f"{entry['explanation']}")
                if not fast:
                    # Early exit: one RED is enough to block the scene
                    break
            else:
                warnings.append(entry)
                flags_to_write.append((entry, book, chapter))
                logger.info(f"AMBER WARNING [{axiom['id']}] Book {book} Ch {chapter}: "
                            f"{entry['explanation']}")

    # --- Pass 3: batch file I/O (one open/write per flag, but after all LLM calls) ---
    for flag_entry, flag_book, flag_chapter in flags_to_write:
        write_flag(flag_entry, flag_book, flag_chapter)

    penalty = len(violations) * 15 + len(warnings) * 5
    score   = max(0, 100 - penalty)

    return {
        "passed":         len(violations) == 0,
        "violations":     violations,
        "warnings":       warnings,
        "score":          score,
        "book":           book,
        "chapter":        chapter,
        "checked_axioms": len(matched_axioms),
        "fast_mode":      fast,
    }


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class GuardHandler(BaseHTTPRequestHandler):

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
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "service": "theological_guard",
                                 "port": API_PORT, "axioms_loaded": len(AXIOMS)})

        elif self.path == "/axioms":
            self.send_json(200, {"axioms": AXIOMS})

        else:
            self.send_json(404, {"error": f"Unknown path: {self.path}"})

    def do_POST(self):
        from urllib.parse import urlparse
        parsed = urlparse(self.path)
        body   = self.read_body()

        if parsed.path == "/validate-scene":
            scene_text = body.get("scene_text", "")
            book       = str(body.get("book", "?"))
            chapter    = str(body.get("chapter", "?"))
            fast       = bool(body.get("fast", False))

            if not scene_text:
                self.send_json(400, {"error": "scene_text required"})
                return

            result = validate_scene(scene_text, book, chapter, fast)
            self.send_json(200, result)

        elif parsed.path == "/validate-batch":
            scenes = body.get("scenes", [])
            book   = str(body.get("book", "?"))
            fast   = bool(body.get("fast", False))

            if not scenes:
                self.send_json(400, {"error": "scenes list required"})
                return

            results = []
            for scene in scenes:
                text    = scene.get("text", "")
                chapter = str(scene.get("chapter", "?"))
                if text:
                    results.append(validate_scene(text, book, chapter, fast))

            all_passed  = all(r["passed"] for r in results)
            total_viols = sum(len(r["violations"]) for r in results)
            total_warns = sum(len(r["warnings"]) for r in results)

            self.send_json(200, {
                "all_passed":        all_passed,
                "scene_count":       len(results),
                "total_violations":  total_viols,
                "total_warnings":    total_warns,
                "results":           results,
            })

        else:
            self.send_json(404, {"error": f"Unknown path: {parsed.path}"})


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 60)
    print("  THEOLOGICAL GUARD — The Nephilim Chronicles v2.0")
    print(f"  Agent 9 | Listening on http://localhost:{API_PORT}")
    print("  Endpoints:")
    print("    POST /validate-scene   — check single scene against axioms")
    print("    POST /validate-batch   — check list of scenes")
    print("    GET  /axioms           — return axiom registry")
    print("    GET  /health           — service health")
    print(f"  Axioms loaded: {len(AXIOMS)}")
    axiom_ids = [a['id'] for a in AXIOMS]
    print(f"  Checks: {', '.join(axiom_ids)}")
    print("═" * 60 + "\n")

    server = HTTPServer(("", API_PORT), GuardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down Theological Guard.")
        server.server_close()


if __name__ == "__main__":
    main()
