"""
DESKTOP-SINGULA — Agent 6: Image Prompt Designer
=================================================
HTTP server (port 8775) generating visual direction prompts for KDP art.

Reads REFERENCE/VISUAL_DIRECTION.md as the visual bible, then produces
Midjourney / DALL-E / Ideogram prompts for:
  - Book cover concepts
  - Chapter header art (symbolic / narrative)
  - Character concept portraits
  - Establishing shots (locations, architecture)

Two visual languages enforced:
  1. Prequels (586 BCE) — "Sacred Tragedy": diptych stained glass, black ink
  2. Main Series (Modern Day) — "Ancient Future": Vorlon/Stargate organic crystalline

Endpoints:
   POST /generate-chapter-art    — Chapter-specific symbolic art prompt
   POST /generate-cover          — Book cover concept prompt
   POST /generate-character      — Character portrait prompt
   POST /generate-establishing   — Location establishing shot prompt
   POST /batch-book              — Generate prompts for all chapters in a book
   GET  /prompts/<book>          — Read saved prompts for a book
   GET  /visual-bible            — Return the loaded visual direction doc
   GET  /health                  — Health check

Governance: AGENT_6, APPEND-only permissions (see governance.py)

Usage:
    python agent_6_image_prompt_designer.py [--port 8775] [--log-level INFO]
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT   = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
LOG_DIR        = PROJECT_ROOT / "LOGS"
LOG_DIR.mkdir(parents=True, exist_ok=True)

PROMPTS_DIR    = PROJECT_ROOT / "03_IMAGE_PROMPTS"
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

VISUAL_BIBLE   = PROJECT_ROOT / "REFERENCE" / "VISUAL_DIRECTION.md"
MANUSCRIPT_DIR = PROJECT_ROOT / "MANUSCRIPT"

API_PORT          = int(os.environ.get("AGENT_6_PORT", "8775"))
NEMOTRON_ROUTER   = "http://localhost:8768"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AGENT-6] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_DIR / "agent_6.log"), encoding="utf-8"),
    ]
)
logger = logging.getLogger("agent_6")

# ── Visual Bible Loader ──────────────────────────────────────────────────────

_visual_bible_cache: str = ""

def load_visual_bible() -> str:
    global _visual_bible_cache
    if _visual_bible_cache:
        return _visual_bible_cache
    if VISUAL_BIBLE.exists():
        _visual_bible_cache = VISUAL_BIBLE.read_text(encoding="utf-8")
        logger.info(f"Loaded visual bible: {len(_visual_bible_cache)} chars")
    else:
        logger.warning(f"Visual bible not found at {VISUAL_BIBLE}")
        _visual_bible_cache = ""
    return _visual_bible_cache


# ── Nemotron Router Helper ────────────────────────────────────────────────────

def call_nemotron(prompt: str, system: str = "", max_tokens: int = 1024,
                  task_type: str = "image_prompt",
                  json_mode: bool = False) -> str:
    payload = {
        "task_type":  task_type,
        "prompt":     prompt,
        "max_tokens": max_tokens,
        "json_mode":  json_mode,
    }
    if system:
        payload["system"] = system

    try:
        r = requests.post(
            f"{NEMOTRON_ROUTER}/route",
            json=payload,
            timeout=300,
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            logger.warning(f"Router returned error: {data['error']}")
            return ""
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return data.get("response", "")
    except Exception as e:
        logger.error(f"Nemotron router call failed: {e}")
        return ""


def _extract_json(raw: str) -> dict | None:
    if not raw:
        return None
    raw = raw.strip()
    # Direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Markdown code block
    for marker in ("```json", "```"):
        if marker in raw:
            start = raw.index(marker) + len(marker)
            end = raw.index("```", start) if "```" in raw[start:] else len(raw)
            try:
                return json.loads(raw[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                pass
    # Brace counting
    brace = raw.find("{")
    if brace >= 0:
        depth = 0
        for i in range(brace, len(raw)):
            if raw[i] == "{":
                depth += 1
            elif raw[i] == "}":
                depth -= 1
            if depth == 0:
                try:
                    return json.loads(raw[brace:i + 1])
                except json.JSONDecodeError:
                    break
    return None


# ── System Prompts ────────────────────────────────────────────────────────────

SYSTEM_CHAPTER_ART = """You are the Image Prompt Designer for The Nephilim Chronicles, a Christian apocalyptic fiction series.

Your job: generate a single, production-ready AI art prompt (Midjourney format) for a chapter's symbolic header image.

RULES:
- The prompt must capture the chapter's THEMATIC ESSENCE, not illustrate a literal scene.
- Use symbolic, archetypal imagery — not character portraits unless specifically requested.
- Enforce the correct visual language:
  * Pre-modern / flashback scenes → "Sacred Tragedy" aesthetic (stained glass, black ink, crimson/bronze/gold)
  * Modern / Watcher-tech scenes → "Ancient Future" aesthetic (Vorlon crystalline, deep space blacks, celestial golds, ethereal blues)
  * Earth Interlude chapters → Cinematic realism with subtle acoustic/frequency motifs (spectrographs, waveforms, signal decay)
- Include Midjourney parameters: --ar (9:16 for chapter art), --v 6.1, --s 250, --c 15, --no text words letters
- Keep prompts under 200 words.
- Output ONLY valid JSON.

CHARACTER COLOR PALETTES (if characters appear):
- Ohya/Apollyon: golds, blacks, plague-yellow. Apollo corrupted.
- Azazel: ice blues, silvers, cold whites. Cold intelligence.
- Naamah: crimsons, purples, blood-golds. Seductive corruption.
- Cian: bronze sword, weathered Irish warrior, ancient bearing.
- Raphael: obscured by radiance, healing hands, hidden wings.
- Elijah: fire, prophetic fury, consuming flame.
- Enoch: light, scribal precision, celestial records.
- Brennan: engineering instruments, spectrographs, blue-lit server rooms.
- James: military precision, whiteboard, operational stillness.

CONSISTENCY: Technology looks "grown rather than built." Scale for giants (15-30 ft). Enochian glyphs where appropriate."""


SYSTEM_COVER = """You are the Image Prompt Designer for The Nephilim Chronicles, a Christian apocalyptic fiction series.

Your job: generate a production-ready AI art prompt (Midjourney format) for a book cover.

RULES:
- Book covers use --ar 2:3 (portrait, standard book ratio).
- Must leave space for title text at top and author name at bottom.
- Enforce the "Ancient Future" aesthetic for main series (Vorlon crystalline, celestial golds, deep space blacks).
- The cover should convey the book's CORE CONFLICT in a single iconic image.
- Include Midjourney parameters: --ar 2:3, --v 6.1, --s 250, --no text words letters
- Keep prompts under 250 words.
- Output ONLY valid JSON.

CHARACTER COLOR PALETTES:
- Ohya/Apollyon: golds, blacks, plague-yellow. Apollo corrupted.
- Azazel: ice blues, silvers, cold whites. False prophet.
- Naamah: crimsons, purples, blood-golds. The Whore of Babylon.
- Cian: bronze sword, weathered warrior, ancient Irish bearing.
- Raphael: radiance, healing, hidden wings.
- The Beast vessel: corporate suit cannot contain ancient horror."""


SYSTEM_CHARACTER = """You are the Image Prompt Designer for The Nephilim Chronicles, a Christian apocalyptic fiction series.

Your job: generate a production-ready AI art prompt (Midjourney format) for a character portrait.

RULES:
- Character portraits use --ar 2:3.
- Must maintain visual consistency with established character markers.
- Include Midjourney parameters: --ar 2:3, --v 6.1, --s 250, --c 15, --no text words letters
- Keep prompts under 200 words.
- Output ONLY valid JSON.

LOCKED CHARACTER VISUALS:
- Cian mac Morna: Bronze sword (Mo Chrá), weathered features, ancient Irish warrior bearing. 2,636 years old but appears 30s.
- Ohya/Apollyon: Golden eyes, too-perfect Apollo features corrupted by millennia of hatred, plague-yellow accents, terrible beauty.
- Azazel: Darkness clinging to face, ice-blue palette, cold intelligence, false light. NEPHILIM (son of Gadreel), NOT a Watcher.
- Naamah: Shifting beauty, crimson/purple, serpentine grace, many faces across millennia. The Siren who survived the Flood.
- Shemyaza: Tragic, bound, suffering. Chains of divine light. Obsessive love. Hidden in darkness.
- Raphael: Obscured by radiance, healing hands, seven-fold wings suggested in luminosity.
- Elijah: Fire and fury, staff of flame, Hebrew prophet, consuming judgment.
- Enoch: Light, scribal precision, celestial records, the Scribe of Heaven.
- Thanatos: Pale horse, wrong face, clinical inevitability. Beautiful winged youth (Greek classical).
- Hades: Vast shadow, walking (no horse), infinite depth containing souls."""


SYSTEM_ESTABLISHING = """You are the Image Prompt Designer for The Nephilim Chronicles, a Christian apocalyptic fiction series.

Your job: generate a production-ready AI art prompt (Midjourney format) for a location establishing shot.

RULES:
- Establishing shots use --ar 16:9 (cinematic widescreen).
- Must convey SCALE and ATMOSPHERE of the location.
- Enforce visual language: Watcher architecture is "grown rather than built," organic-crystalline, sacred geometry, built for beings 15-30 ft tall.
- Earth locations should feel grounded but carry supernatural undertones.
- Include Midjourney parameters: --ar 16:9, --v 6.1, --s 250, --no text words letters
- Keep prompts under 200 words.
- Output ONLY valid JSON.

KEY LOCATIONS:
- Cydonia-1 (Mars): Ancient alien citadel, obsidian and gold, bioluminescent veins, sacred geometry, Vorlon aesthetic.
- Cydonia-2 / Dudael (Antarctica): Ice-bound fortress, frozen chains, darkness with texture, Azazel's prison.
- Eden: Creation frequency, impossible beauty, the Tree of Life, river of light, timeless sanctuary.
- Mount Hermon: Where the 200 descended. Storm-wreathed peak. Cosmic betrayal site.
- Stewart Island (NZ): Remote safehouse, Southern Ocean, server rooms, spectrographs, isolation.
- Jerusalem: Ancient meets modern, prophetic significance, the Witnesses' stage."""


# ── Prompt Generation Functions ───────────────────────────────────────────────

def _read_chapter_text(book: int, chapter: int) -> str:
    book_dir = MANUSCRIPT_DIR / f"book_{book}" / "CHAPTERS"
    if not book_dir.exists():
        book_dir = MANUSCRIPT_DIR / f"book_{book}"

    # Find the chapter file by number prefix
    pattern = f"CHAPTER_{chapter:02d}"
    for f in sorted(book_dir.iterdir()):
        if f.name.upper().startswith(pattern) and f.suffix == ".md":
            text = f.read_text(encoding="utf-8")
            logger.info(f"Read chapter: {f.name} ({len(text)} chars)")
            return text

    # Try without leading zero
    pattern2 = f"CHAPTER_{chapter}_"
    for f in sorted(book_dir.iterdir()):
        if f.name.upper().startswith(pattern2) and f.suffix == ".md":
            text = f.read_text(encoding="utf-8")
            logger.info(f"Read chapter: {f.name} ({len(text)} chars)")
            return text

    logger.warning(f"Chapter file not found: book {book}, chapter {chapter}")
    return ""


def _get_prompts_file(book: int) -> Path:
    return PROMPTS_DIR / f"BOOK_{book}_PROMPTS.md"


def _append_prompt(book: int, section: str, content: str):
    pfile = _get_prompts_file(book)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not pfile.exists():
        header = f"# Image Prompts — Book {book}\n\n"
        header += f"**Generated by Agent 6 — Image Prompt Designer**\n"
        header += f"**Visual Bible:** REFERENCE/VISUAL_DIRECTION.md\n\n---\n\n"
        pfile.write_text(header, encoding="utf-8")

    with open(pfile, "a", encoding="utf-8") as f:
        f.write(f"\n## {section}\n")
        f.write(f"*Generated: {timestamp}*\n\n")
        f.write(content)
        f.write("\n\n---\n")

    logger.info(f"Appended prompt to {pfile.name}: {section}")


def generate_chapter_art(book: int, chapter: int, chapter_title: str = "",
                         extra_context: str = "") -> dict:
    chapter_text = _read_chapter_text(book, chapter)
    if not chapter_text:
        return {"error": f"Chapter file not found: book {book}, chapter {chapter}"}

    visual_bible = load_visual_bible()

    # Extract first 4000 chars for context (enough for themes without overloading)
    excerpt = chapter_text[:4000]

    prompt = f"""Generate a chapter header art prompt for:
Book: {book}  Chapter: {chapter}  Title: "{chapter_title}"

Chapter excerpt (thematic context):
\"\"\"{excerpt}\"\"\"

{f'Additional context: {extra_context}' if extra_context else ''}

Visual bible reference (key palettes and aesthetics):
\"\"\"{visual_bible[:3000]}\"\"\"

Return JSON:
{{
  "prompt": "The complete Midjourney prompt string including all parameters",
  "aesthetic": "Sacred Tragedy | Ancient Future | Cinematic Realism",
  "aspect_ratio": "9:16",
  "symbolic_elements": ["list", "of", "key", "symbols"],
  "color_palette": "Description of the dominant colors",
  "mood": "One-line mood description"
}}"""

    raw = call_nemotron(prompt, system=SYSTEM_CHAPTER_ART, max_tokens=1024,
                        task_type="image_prompt", json_mode=True)

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}
    else:
        # Save to prompts file
        ch_label = f"Chapter {chapter}: {chapter_title}" if chapter_title else f"Chapter {chapter}"
        content = f"**{ch_label}**\n\n"
        content += f"**Aesthetic:** {result.get('aesthetic', 'N/A')}\n"
        content += f"**Mood:** {result.get('mood', 'N/A')}\n"
        content += f"**Palette:** {result.get('color_palette', 'N/A')}\n"
        content += f"**Symbols:** {', '.join(result.get('symbolic_elements', []))}\n\n"
        content += f"```\n{result.get('prompt', '')}\n```\n"
        _append_prompt(book, f"Chapter {chapter} — {chapter_title or 'Header Art'}", content)

    result["book"] = book
    result["chapter"] = chapter
    result["chapter_title"] = chapter_title
    result["generated_at"] = datetime.now().isoformat()
    return result


def generate_cover(book: int, book_title: str, core_conflict: str,
                   key_characters: list[str] | None = None,
                   extra_context: str = "") -> dict:
    visual_bible = load_visual_bible()

    prompt = f"""Generate a book cover art prompt for:
Book: {book}  Title: "{book_title}"
Core conflict: {core_conflict}
Key characters: {', '.join(key_characters) if key_characters else 'N/A'}

{f'Additional context: {extra_context}' if extra_context else ''}

Visual bible reference:
\"\"\"{visual_bible[:3000]}\"\"\"

Return JSON:
{{
  "prompt": "The complete Midjourney prompt string including all parameters",
  "aesthetic": "Sacred Tragedy | Ancient Future",
  "aspect_ratio": "2:3",
  "focal_element": "The single dominant visual element",
  "color_palette": "Dominant colors",
  "title_placement": "Where title text should overlay (top/center/bottom)",
  "mood": "One-line mood description"
}}"""

    raw = call_nemotron(prompt, system=SYSTEM_COVER, max_tokens=1024,
                        task_type="image_prompt", json_mode=True)

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}
    else:
        content = f"**{book_title}**\n\n"
        content += f"**Focal Element:** {result.get('focal_element', 'N/A')}\n"
        content += f"**Palette:** {result.get('color_palette', 'N/A')}\n"
        content += f"**Mood:** {result.get('mood', 'N/A')}\n"
        content += f"**Title Placement:** {result.get('title_placement', 'N/A')}\n\n"
        content += f"```\n{result.get('prompt', '')}\n```\n"
        _append_prompt(book, f"Book Cover — {book_title}", content)

    result["book"] = book
    result["book_title"] = book_title
    result["generated_at"] = datetime.now().isoformat()
    return result


def generate_character(character_name: str, book: int = 0,
                       description: str = "", scene_context: str = "") -> dict:
    visual_bible = load_visual_bible()

    prompt = f"""Generate a character portrait prompt for:
Character: {character_name}
{f'Book context: Book {book}' if book else ''}
{f'Description: {description}' if description else ''}
{f'Scene context: {scene_context}' if scene_context else ''}

Visual bible reference (character profiles):
\"\"\"{visual_bible[:3000]}\"\"\"

Return JSON:
{{
  "prompt": "The complete Midjourney prompt string including all parameters",
  "aesthetic": "Sacred Tragedy | Ancient Future",
  "aspect_ratio": "2:3",
  "key_markers": ["list", "of", "visual", "markers"],
  "color_palette": "Dominant colors for this character",
  "mood": "One-line mood description"
}}"""

    raw = call_nemotron(prompt, system=SYSTEM_CHARACTER, max_tokens=1024,
                        task_type="image_prompt", json_mode=True)

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}
    else:
        content = f"**{character_name}**\n\n"
        content += f"**Markers:** {', '.join(result.get('key_markers', []))}\n"
        content += f"**Palette:** {result.get('color_palette', 'N/A')}\n"
        content += f"**Mood:** {result.get('mood', 'N/A')}\n\n"
        content += f"```\n{result.get('prompt', '')}\n```\n"
        _append_prompt(book or 0, f"Character — {character_name}", content)

    result["character"] = character_name
    result["generated_at"] = datetime.now().isoformat()
    return result


def generate_establishing(location: str, book: int = 0,
                          description: str = "", scene_context: str = "") -> dict:
    visual_bible = load_visual_bible()

    prompt = f"""Generate an establishing shot prompt for:
Location: {location}
{f'Book context: Book {book}' if book else ''}
{f'Description: {description}' if description else ''}
{f'Scene context: {scene_context}' if scene_context else ''}

Visual bible reference:
\"\"\"{visual_bible[:3000]}\"\"\"

Return JSON:
{{
  "prompt": "The complete Midjourney prompt string including all parameters",
  "aesthetic": "Sacred Tragedy | Ancient Future | Cinematic Realism",
  "aspect_ratio": "16:9",
  "scale_reference": "What conveys the scale (human figure, vehicle, etc.)",
  "color_palette": "Dominant colors",
  "mood": "One-line mood description"
}}"""

    raw = call_nemotron(prompt, system=SYSTEM_ESTABLISHING, max_tokens=1024,
                        task_type="image_prompt", json_mode=True)

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}
    else:
        content = f"**{location}**\n\n"
        content += f"**Scale:** {result.get('scale_reference', 'N/A')}\n"
        content += f"**Palette:** {result.get('color_palette', 'N/A')}\n"
        content += f"**Mood:** {result.get('mood', 'N/A')}\n\n"
        content += f"```\n{result.get('prompt', '')}\n```\n"
        _append_prompt(book or 0, f"Establishing — {location}", content)

    result["location"] = location
    result["generated_at"] = datetime.now().isoformat()
    return result


def batch_book_chapter_art(book: int, chapter_map: dict[int, str] | None = None) -> dict:
    """Generate chapter art prompts for all chapters in a book."""
    book_dir = MANUSCRIPT_DIR / f"book_{book}" / "CHAPTERS"
    if not book_dir.exists():
        book_dir = MANUSCRIPT_DIR / f"book_{book}"

    if not book_dir.exists():
        return {"error": f"Book directory not found: book_{book}"}

    # Discover chapters
    chapters = []
    for f in sorted(book_dir.iterdir()):
        if f.name.upper().startswith("CHAPTER_") and f.suffix == ".md":
            # Extract chapter number
            parts = f.stem.split("_")
            try:
                ch_num = int(parts[1])
                ch_title = " ".join(parts[2:]).replace("_", " ").title() if len(parts) > 2 else ""
                chapters.append((ch_num, ch_title))
            except (ValueError, IndexError):
                continue

    if chapter_map:
        # Use provided map to override titles
        chapters = [(num, chapter_map.get(num, title)) for num, title in chapters]

    results = []
    for ch_num, ch_title in chapters:
        logger.info(f"Generating chapter art: Book {book}, Ch {ch_num} — {ch_title}")
        result = generate_chapter_art(book, ch_num, ch_title)
        results.append(result)

    return {
        "book": book,
        "chapters_processed": len(results),
        "results": results,
        "generated_at": datetime.now().isoformat(),
    }


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class ImagePromptHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        logger.info(fmt % args)

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── GET ───────────────────────────────────────────────────────────────

    def do_GET(self):
        path = self.path.rstrip("/")

        if path == "/health":
            self.send_json({
                "status": "ok",
                "service": "agent_6_image_prompt_designer",
                "port": API_PORT,
                "visual_bible_loaded": bool(_visual_bible_cache),
            })

        elif path == "/visual-bible":
            bible = load_visual_bible()
            self.send_json({
                "content": bible,
                "length": len(bible),
            })

        elif path.startswith("/prompts/"):
            # /prompts/3 → read BOOK_3_PROMPTS.md
            try:
                book = int(path.split("/")[-1])
            except ValueError:
                self.send_json({"error": "Invalid book number"}, 400)
                return
            pfile = _get_prompts_file(book)
            if pfile.exists():
                self.send_json({
                    "book": book,
                    "content": pfile.read_text(encoding="utf-8"),
                })
            else:
                self.send_json({"error": f"No prompts file for book {book}"}, 404)

        else:
            self.send_json({"error": f"Unknown GET path: {path}"}, 404)

    # ── POST ──────────────────────────────────────────────────────────────

    def do_POST(self):
        path = self.path.rstrip("/")

        try:
            body = self.read_json_body()
        except (json.JSONDecodeError, Exception) as e:
            self.send_json({"error": f"Invalid JSON body: {e}"}, 400)
            return

        if path == "/generate-chapter-art":
            book = body.get("book")
            chapter = body.get("chapter")
            if not book or not chapter:
                self.send_json({"error": "Required: book, chapter"}, 400)
                return
            result = generate_chapter_art(
                book=int(book),
                chapter=int(chapter),
                chapter_title=body.get("chapter_title", ""),
                extra_context=body.get("extra_context", ""),
            )
            self.send_json(result)

        elif path == "/generate-cover":
            book = body.get("book")
            book_title = body.get("book_title")
            core_conflict = body.get("core_conflict")
            if not book or not book_title or not core_conflict:
                self.send_json({"error": "Required: book, book_title, core_conflict"}, 400)
                return
            result = generate_cover(
                book=int(book),
                book_title=book_title,
                core_conflict=core_conflict,
                key_characters=body.get("key_characters"),
                extra_context=body.get("extra_context", ""),
            )
            self.send_json(result)

        elif path == "/generate-character":
            character_name = body.get("character_name")
            if not character_name:
                self.send_json({"error": "Required: character_name"}, 400)
                return
            result = generate_character(
                character_name=character_name,
                book=int(body.get("book", 0)),
                description=body.get("description", ""),
                scene_context=body.get("scene_context", ""),
            )
            self.send_json(result)

        elif path == "/generate-establishing":
            location = body.get("location")
            if not location:
                self.send_json({"error": "Required: location"}, 400)
                return
            result = generate_establishing(
                location=location,
                book=int(body.get("book", 0)),
                description=body.get("description", ""),
                scene_context=body.get("scene_context", ""),
            )
            self.send_json(result)

        elif path == "/batch-book":
            book = body.get("book")
            if not book:
                self.send_json({"error": "Required: book"}, 400)
                return
            result = batch_book_chapter_art(
                book=int(book),
                chapter_map=body.get("chapter_map"),
            )
            self.send_json(result)

        else:
            self.send_json({"error": f"Unknown POST path: {path}"}, 404)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agent 6 — Image Prompt Designer")
    parser.add_argument("--port", type=int, default=API_PORT)
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Pre-load visual bible
    load_visual_bible()

    server = HTTPServer(("0.0.0.0", args.port), ImagePromptHandler)
    logger.info(f"Agent 6 — Image Prompt Designer starting on port {args.port}")
    logger.info(f"Visual bible: {'LOADED' if _visual_bible_cache else 'NOT FOUND'}")
    logger.info(f"Prompts output: {PROMPTS_DIR}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Agent 6")
        server.server_close()


if __name__ == "__main__":
    main()
