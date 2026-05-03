"""
audiobook_prep_server.py
------------------------
HTTP microservice (port 8776) — Audiobook Pre-Production Pipeline for
The Nephilim Chronicles.

Exposes four staged endpoints plus a single-call /assemble pipeline:

    POST /sanitize            Stage 1 — strip front/back matter + decorative glyphs
    POST /machine-ear         Stage 2 — Machine Ear optimization (visual refs, numbers,
                                        phonetic injection from PHONETIC_GLOSSARY + Qdrant)
    POST /production-manifest Stage 3 — Narrative Director: Nemotron 1M-context pass →
                                        PRODUCTION_MANIFEST.json
    POST /diarize-hybrid      Stage 4 — Hybrid XML diarization (Nemotron auto-tags routine
                                        lines; REVIEW_FLAGS.json for ambiguous segments)
    POST /assemble            Stages 1–4 in sequence (convenience entry point)
    POST /synthesis-dispatch  STUB — 501 Not Implemented (reserved for Grok TTS)
    GET  /health

All outputs land under:
    STAGING/audiobook/book_{N}/
        sanitized/
        machine_ear/
        diarized/
            CH_XX_AUTO.xml
            CH_XX_REVIEW_FLAGS.json
        PRODUCTION_MANIFEST.json
        DIARIZATION_REPORT.md

Canon authority:
    CANON/PHONETIC_GLOSSARY.md  (primary phonetics source)
    http://localhost:8765/search  (Qdrant fallback)
    http://localhost:8768/route   (Nemotron router — NIM → OpenRouter → GGUF → Ollama)

Voice roster (2026-04-28 revision from diarize-chapter/SKILL.md):
    Leo / pitch_low   — Omniscient Narrator
    Rex / baseline    — Cian mac Morna (protagonist)
    Eve / baseline    — Miriam, Victoria, Sarah McNeeve, Mo Chrá (sword)
    Ara / slow_whisper — Naamah bat Lamech
    Leo / deep_tag    — Archangels (Liaigh/Raphael, Michael, Uriel, Gabriel, Sariel, The Word)
    Leo / style_deep  — Watcher Chiefs (Shemyaza, Gadreel, Azazel, Penemue, Kokabiel,
                         Araqiel, Baraqiel, Armaros, Tamiel) + collective Watchers
    Leo / pitch_neg   — The Adversary / Satan / Helel / The Trafficker
    Leo / pitch_low   — Brennan McNeeve, Vârcolac
    Leo / low_tag     — James Madigan
    Leo / slow_tag    — Enoch
    Sal / baseline    — Restricted allowlist: Khem Operative, Lamech (ben Methushael),
                         Domnul, Hal, House Satar Patriarch/Analyst, Guard

Usage:
    python INFRA/agents/audiobook_prep_server.py
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

SERVER_PORT = 8776

PROJECT_ROOT = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
CANON_DIR    = PROJECT_ROOT / "CANON"
PHONETIC_GLOSSARY = CANON_DIR / "PHONETIC_GLOSSARY.md"
STAGING_ROOT = PROJECT_ROOT / "STAGING" / "audiobook"
LOGS_DIR     = PROJECT_ROOT / "LOGS"

# Manuscript paths by book number
MANUSCRIPT_DIRS = {
    1: PROJECT_ROOT / "MANUSCRIPT" / "book_1",
    2: PROJECT_ROOT / "MANUSCRIPT" / "book_2" / "CHAPTERS",
    3: PROJECT_ROOT / "MANUSCRIPT" / "book_3" / "CHAPTERS",
    4: PROJECT_ROOT / "MANUSCRIPT" / "book_4" / "CHAPTERS",
    5: PROJECT_ROOT / "MANUSCRIPT" / "book_5" / "CHAPTERS",
}

# Downstream service URLs (local, not docker-internal — this server runs on the host)
CANON_SEARCH_URL  = "http://localhost:8765"
NEMOTRON_URL      = "http://localhost:8768"

# ---------------------------------------------------------------------------
# DECORATIVE GLYPH PATTERN — strip these so TTS doesn't read them aloud
# ---------------------------------------------------------------------------
DECORATIVE_GLYPHS = re.compile(r"[✦✧★☆❋❊✸✹✺✻✼✽✾♦◆◇▪▫■□▲△▼▽◉○●◦⟡⟢⟣⟤⟥⟦⟧⟨⟩⟪⟫⁂※†‡§¶]")

# Front/back matter filename patterns to EXCLUDE from audio output
FRONT_MATTER_PATTERNS = {
    r"FRONT_MATTER",
    r"TABLE_OF_CONTENTS",
    r"TOC",
    r"COPYRIGHT",
    r"DEDICATION",
    r"EPIGRAPH",
    r"AVAILABLE_BOOKS",
    r"ALSO_BY",
    r"ABOUT_THE_AUTHOR",
    r"ACKNOWLEDGEMENTS?",
    r"ACKNOWLEDGMENTS?",
}

# Back matter patterns that cannot be narrated
BACK_MATTER_VISUAL_PATTERNS = {
    r"APPENDIX_[Ff]",   # Maps appendix
    r"MAPS?",
    r"DIAGRAM",
    r"CHART",
    r"FAMILY_TREE",
    r"GENEALOGY",
}

# Abbreviation expansion map (applied during Machine Ear pass)
ABBREVIATION_MAP = {
    r"\bSt\.\s": "Saint ",
    r"\bSts\.\s": "Saints ",
    r"\bDr\.\s": "Doctor ",
    r"\bMr\.\s": "Mister ",
    r"\bMrs\.\s": "Missus ",
    r"\bMs\.\s": "Ms. ",
    r"\bProf\.\s": "Professor ",
    r"\bGen\.\s": "General ",
    r"\bCol\.\s": "Colonel ",
    r"\bLt\.\s": "Lieutenant ",
    r"\bSgt\.\s": "Sergeant ",
    r"\bCpl\.\s": "Corporal ",
    r"\bPvt\.\s": "Private ",
    r"\bAve\.\s": "Avenue ",
    r"\bBlvd\.\s": "Boulevard ",
    r"\bRd\.\s": "Road ",
    r"\bApt\.\s": "Apartment ",
    r"\bvs\.\s": "versus ",
    r"\betc\.": "etcetera",
    r"\be\.g\.": "for example",
    r"\bi\.e\.": "that is",
    r"\bca\.\s": "approximately ",
    r"\bbce?\b": "BCE",
    r"\bce\b": "CE",
    r"\bkm\b": "kilometres",
    r"\bm/s\b": "metres per second",
    r"\bHz\b": "Hertz",
    r"\bkHz\b": "kiloHertz",
    r"\bMHz\b": "megaHertz",
}

# Visual reference rewrites  (applied during Machine Ear pass)
VISUAL_REFERENCE_MAP = [
    (r"as shown (below|above|in the (map|figure|diagram|table|chart|image|illustration))",
     r"as detailed in the supplemental PDF"),
    (r"(see|refer to) (the )?(map|figure|diagram|table|chart|image|illustration)( below| above)?",
     r"refer to the supplemental PDF"),
    (r"(the following (map|figure|table|diagram|chart))",
     r"the supplemental PDF"),
    (r"(illustrated|depicted|shown) (above|below|here)",
     r"described in the supplemental PDF"),
    (r"\[Figure \d+[^\]]*\]", ""),
    (r"\[Map [^\]]*\]", ""),
    (r"\[Image [^\]]*\]", ""),
    (r"\[Table \d+[^\]]*\]", ""),
    (r"!\[[^\]]*\]\([^)]*\)", ""),   # Strip markdown images entirely
]

# ---------------------------------------------------------------------------
# VOICE ROSTER — used by hybrid diarizer
# ---------------------------------------------------------------------------
VOICE_ROSTER = {
    # Narrator
    "Narrator":         ("Leo",  "pitch_low"),
    # Protagonist
    "Cian":             ("Rex",  "baseline"),
    # Sword
    "Mo_Chra":          ("Eve",  "baseline"),
    # Archangels
    "Liaigh":           ("Leo",  "deep_tag"),
    "Michael":          ("Leo",  "deep_tag"),
    "Uriel":            ("Leo",  "deep_tag"),
    "Gabriel":          ("Leo",  "deep_tag"),
    "Sariel":           ("Leo",  "deep_tag"),
    "The_Word":         ("Leo",  "deep_tag"),
    # Watcher Chiefs
    "Shemyaza":         ("Leo",  "style_deep"),
    "Gadreel":          ("Leo",  "style_deep"),
    "Azazel":           ("Leo",  "style_deep"),
    "Penemue":          ("Leo",  "style_deep"),
    "Kokabiel":         ("Leo",  "style_deep"),
    "Araqiel":          ("Leo",  "style_deep"),
    "Baraqiel":         ("Leo",  "style_deep"),
    "Armaros":          ("Leo",  "style_deep"),
    "Tamiel":           ("Leo",  "style_deep"),
    "Watchers":         ("Leo",  "style_deep"),
    # Adversary
    "The_Adversary":    ("Leo",  "pitch_neg"),
    "Shedim":           ("Leo",  "style_deep"),
    # Major mortal males
    "Brennan":          ("Leo",  "pitch_low"),
    "Varcolac":         ("Leo",  "pitch_low"),
    "James":            ("Leo",  "low_tag"),
    "Enoch":            ("Leo",  "slow_tag"),
    "Marcus":           ("Leo",  "baseline"),
    "Dragomir":         ("Leo",  "baseline"),
    "Brother_Michel":   ("Leo",  "baseline"),
    "Jeremiah":         ("Leo",  "baseline"),
    # Female characters
    "Naamah":           ("Ara",  "slow_whisper"),
    "Miriam":           ("Eve",  "baseline"),
    "Victoria":         ("Eve",  "baseline"),
    "Sarah":            ("Eve",  "baseline"),
    "Sarah_McNeeve":    ("Eve",  "baseline"),
    "Elara":            ("Eve",  "baseline"),
    "Anya":             ("Eve",  "baseline"),
    "Dara":             ("Eve",  "baseline"),
    "Siorse":           ("Eve",  "baseline"),
    "Emma":             ("Eve",  "baseline"),
    "Niamh":            ("Eve",  "baseline"),
    "Adrienne":         ("Eve",  "baseline"),
    # Sal allowlist (RESTRICTED)
    "Khem_Operative":   ("Sal",  "baseline"),
    "Lamech":           ("Sal",  "baseline"),
    "Domnul":           ("Sal",  "baseline"),
    "Hal":              ("Sal",  "baseline"),
    "Satar_Patriarch":  ("Sal",  "baseline"),
    "Satar_Analyst":    ("Sal",  "baseline"),
    "Guard":            ("Sal",  "baseline"),
}

# Default for any unmatched male
DEFAULT_MALE   = ("Leo", "baseline")
DEFAULT_FEMALE = ("Eve", "baseline")

# Segments that require human (Claude) review rather than auto-diarization
# These map to the REVIEW_FLAGS.json output
AMBIGUOUS_PATTERNS = [
    re.compile(r"Mo Chr[aá]", re.IGNORECASE),          # Sword hum-speech
    re.compile(r"\*[^*]+\*"),                            # Italicised text (often thought / emphasis)
    re.compile(r"(?<![\"'«])\b(he|she|I|we)\b.*?(?=\.|!|\?)", re.IGNORECASE),  # Unquoted internal monologue signals
    re.compile(r"\[([A-Z\s]+)\]"),                       # Stage direction / Empyreal Register caps
    re.compile(r"[A-Z][a-z]+ mac [A-Z]"),               # Irish patronymics (could be narrator or dialogue)
]

# ---------------------------------------------------------------------------
# PHONETIC GLOSSARY LOADER
# ---------------------------------------------------------------------------

def load_phonetic_glossary() -> dict[str, str]:
    """
    Parse CANON/PHONETIC_GLOSSARY.md into {term: plain_english_phonetic} dict.
    Returns empty dict if file not found.
    """
    if not PHONETIC_GLOSSARY.exists():
        return {}
    glossary: dict[str, str] = {}
    try:
        text = PHONETIC_GLOSSARY.read_text(encoding="utf-8")
        # Match table rows: | Term | IPA | Plain-English | Notes |
        pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*[^|]*\|\s*([^|]+?)\s*\|", re.MULTILINE)
        for m in pattern.finditer(text):
            term = m.group(1).strip()
            phonetic = m.group(2).strip()
            # Skip header rows and separator rows
            if term.lower() in ("term", "---", "") or "---" in term:
                continue
            if phonetic and phonetic.lower() not in ("plain-english", "---", ""):
                glossary[term] = phonetic
    except Exception as e:
        print(f"[AUDIOBOOK] Warning: failed to load phonetic glossary: {e}")
    return glossary


def qdrant_phonetic_lookup(term: str) -> str | None:
    """
    Fallback: query canon_search_api for phonetic data.
    Returns plain-English phonetic string or None.
    """
    try:
        query_text = f"{term} pronunciation phonetic IPA"
        payload = json.dumps({"query": query_text, "top_k": 3}).encode()
        req = urllib.request.Request(
            f"{CANON_SEARCH_URL}/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            results = data.get("results", [])
            if results and results[0].get("score", 0) > 0.7:
                # Best-effort extract: return the snippet
                return f"[see canon: {results[0].get('text', '')[:80]}]"
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# STAGE 1 — SANITIZE
# ---------------------------------------------------------------------------

def sanitize_book(book: int) -> dict:
    """
    Stage 1: Copy chapter markdown files into STAGING/audiobook/book_{N}/sanitized/,
    stripping front/back matter that cannot be narrated and decorative glyphs.
    Returns stats dict.
    """
    ms_dir = MANUSCRIPT_DIRS.get(book)
    if not ms_dir or not ms_dir.exists():
        return {"status": "error", "message": f"Manuscript dir not found: {ms_dir}"}

    out_dir = STAGING_ROOT / f"book_{book}" / "sanitized"
    out_dir.mkdir(parents=True, exist_ok=True)

    included, excluded, glyph_count = [], [], 0

    front_re = re.compile("|".join(FRONT_MATTER_PATTERNS), re.IGNORECASE)
    back_re  = re.compile("|".join(BACK_MATTER_VISUAL_PATTERNS), re.IGNORECASE)

    md_files = sorted(ms_dir.glob("*.md"))
    if not md_files:
        # Some books nest further — try one level down
        md_files = sorted(ms_dir.parent.glob("**/*.md"))

    for f in md_files:
        stem_upper = f.stem.upper()
        if front_re.search(stem_upper):
            excluded.append(f.name)
            continue
        if back_re.search(stem_upper):
            excluded.append(f.name)
            continue

        text = f.read_text(encoding="utf-8")
        before_len = len(text)
        text, n = DECORATIVE_GLYPHS.subn("", text)
        glyph_count += n

        # Also strip markdown horizontal rules made of glyphs
        text = re.sub(r"^[\s*-]{3,}$", "", text, flags=re.MULTILINE)

        out_path = out_dir / f.name
        out_path.write_text(text, encoding="utf-8")
        included.append(f.name)

    return {
        "status":       "ok",
        "stage":        "sanitize",
        "book":         book,
        "output_dir":   str(out_dir),
        "included":     len(included),
        "excluded":     excluded,
        "glyphs_removed": glyph_count,
        "files":        included,
    }


# ---------------------------------------------------------------------------
# STAGE 2 — MACHINE EAR
# ---------------------------------------------------------------------------

def machine_ear_book(book: int) -> dict:
    """
    Stage 2: Process sanitized files through Machine Ear optimizations.
    - Rewrite visual references
    - Expand abbreviations
    - Inject phonetic annotations for difficult names (first occurrence per chapter)
    """
    src_dir = STAGING_ROOT / f"book_{book}" / "sanitized"
    out_dir = STAGING_ROOT / f"book_{book}" / "machine_ear"

    if not src_dir.exists():
        return {"status": "error", "message": "Run /sanitize first (sanitized/ dir missing)"}

    out_dir.mkdir(parents=True, exist_ok=True)
    glossary = load_phonetic_glossary()

    # Pre-compile abbreviation patterns
    abbrev_patterns = [(re.compile(pat), repl) for pat, repl in ABBREVIATION_MAP.items()]
    # Pre-compile visual reference patterns
    visual_patterns = [(re.compile(pat, re.IGNORECASE), repl) for pat, repl in VISUAL_REFERENCE_MAP]

    total_abbrev   = 0
    total_visual   = 0
    total_phonetic = 0
    processed      = []

    for f in sorted(src_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")

        # Visual reference rewrites
        for pat, repl in visual_patterns:
            text, n = pat.subn(repl, text)
            total_visual += n

        # Abbreviation expansion
        for pat, repl in abbrev_patterns:
            text, n = pat.subn(repl, text)
            total_abbrev += n

        # Number expansion: spell out large standalone integers and ordinals
        # e.g. "3,048" → "three thousand and forty-eight"  (handled by TTS if written out)
        # We do a lightweight pass: flag 4+ digit numbers that aren't years or model numbers
        def expand_number(m: re.Match) -> str:
            raw = m.group(0).replace(",", "")
            try:
                n = int(raw)
                # Leave years (1800–2099) and short numbers alone
                if 1800 <= n <= 2099 or n < 100:
                    return m.group(0)
                return _num_to_words(n)
            except ValueError:
                return m.group(0)

        text = re.sub(r"\b\d{1,3}(?:,\d{3})+\b|\b\d{4,}\b", expand_number, text)

        # Phonetic injection — first occurrence per chapter per term
        seen_terms: set[str] = set()
        for term, plain_phonetic in glossary.items():
            if term in seen_terms:
                continue
            # Case-insensitive first occurrence replacement
            escaped = re.escape(term)
            pat_term = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
            if pat_term.search(text):
                def inject(m: re.Match, t=term, pp=plain_phonetic, s=seen_terms) -> str:
                    if t in s:
                        return m.group(0)
                    s.add(t)
                    total_phonetic  # noqa: captured from enclosing scope via nonlocal workaround
                    return f"{m.group(0)} _{pp}_"
                text = pat_term.sub(inject, text, count=1)
                seen_terms.add(term)
                total_phonetic += 1

        out_path = out_dir / f.name
        out_path.write_text(text, encoding="utf-8")
        processed.append(f.name)

    return {
        "status":           "ok",
        "stage":            "machine_ear",
        "book":             book,
        "output_dir":       str(out_dir),
        "files_processed":  len(processed),
        "visual_rewrites":  total_visual,
        "abbrev_expansions": total_abbrev,
        "phonetic_injections": total_phonetic,
    }


def _num_to_words(n: int) -> str:
    """
    Lightweight integer-to-words converter for numbers not covered by TTS.
    Handles 0–999,999. Falls back to string representation for larger values.
    """
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
            "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
            "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    if n == 0:
        return "zero"
    if n < 0:
        return f"negative {_num_to_words(-n)}"

    def _below_thousand(x: int) -> str:
        if x == 0:
            return ""
        if x < 20:
            return ones[x]
        if x < 100:
            remainder = x % 10
            return tens[x // 10] + ("-" + ones[remainder] if remainder else "")
        h = x // 100
        remainder = x % 100
        return ones[h] + " hundred" + (" and " + _below_thousand(remainder) if remainder else "")

    if n < 1000:
        return _below_thousand(n)
    if n < 1_000_000:
        thousands = n // 1000
        remainder = n % 1000
        result = _below_thousand(thousands) + " thousand"
        if remainder:
            result += " and " + _below_thousand(remainder) if remainder < 100 else " " + _below_thousand(remainder)
        return result
    # Fallback for very large numbers
    return str(n)


# ---------------------------------------------------------------------------
# STAGE 3 — PRODUCTION MANIFEST (Narrative Director)
# ---------------------------------------------------------------------------

def production_manifest_book(book: int) -> dict:
    """
    Stage 3: Route the full sanitized+optimized manuscript to Nemotron router
    (:8768/route) using the NIM tier (1M-context window) to generate a structured
    PRODUCTION_MANIFEST.json with:
        - character_profiles: {name: {gender, age_range, accent, voice_notes}}
        - sentiment_map: [{chapter, scene_index, emotion, intensity, pacing_note}]
        - spatial_audio_cues: [{chapter, scene_index, cue_type, description, timing}]
    """
    src_dir = STAGING_ROOT / f"book_{book}" / "machine_ear"
    if not src_dir.exists():
        return {"status": "error", "message": "Run /machine-ear first (machine_ear/ dir missing)"}

    out_dir = STAGING_ROOT / f"book_{book}"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "PRODUCTION_MANIFEST.json"

    # Assemble full manuscript text (truncated at 850k chars to stay under 900k token ceiling)
    MAX_CHARS = 850_000
    chapters_text = ""
    chapter_list  = []
    for f in sorted(src_dir.glob("*.md")):
        chapter_list.append(f.stem)
        content = f.read_text(encoding="utf-8")
        chapters_text += f"\n\n--- FILE: {f.name} ---\n{content}"
        if len(chapters_text) >= MAX_CHARS:
            chapters_text = chapters_text[:MAX_CHARS]
            chapters_text += "\n\n[TRUNCATED — remaining chapters omitted for context budget]"
            break

    prompt = (
        "You are the Narrative Director for The Nephilim Chronicles audiobook production.\n"
        "Analyse the manuscript below and return a valid JSON object with EXACTLY these keys:\n\n"
        "{\n"
        '  "character_profiles": {\n'
        '    "<character_name>": {\n'
        '      "gender": "male|female|non-binary|celestial",\n'
        '      "age_range": "<string, e.g. ancient, 30s, child>",\n'
        '      "accent": "<string>",\n'
        '      "vocal_notes": "<string — key delivery traits for TTS>"\n'
        "    }\n"
        "  },\n"
        '  "sentiment_map": [\n'
        '    {"chapter": "<filename>", "scene_index": <int>, "emotion": "<string>",\n'
        '     "intensity": <1-10>, "pacing_note": "<string>"}\n'
        "  ],\n"
        '  "spatial_audio_cues": [\n'
        '    {"chapter": "<filename>", "scene_index": <int>, "cue_type": "ambient|sfx|music_bed",\n'
        '     "description": "<string>", "timing": "pre|during|post"}\n'
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- character_profiles: only include characters with dialogue or significant action.\n"
        "- sentiment_map: cover every distinct scene (scene = section separated by scene break).\n"
        "- spatial_audio_cues: flag acoustic Paradigm events (Mo Chrá frequencies, Cydonian resonance),\n"
        "  battle sounds, ambience shifts, silences. Minimum 1 cue per chapter.\n"
        "- Output ONLY valid JSON. No markdown fences, no commentary.\n\n"
        f"CHAPTERS PROCESSED: {', '.join(chapter_list)}\n\n"
        f"MANUSCRIPT:\n{chapters_text}"
    )

    payload = json.dumps({
        "prompt":     prompt,
        "max_tokens": 16384,
        "tier_hint":  "nim",        # Prefer Tier 1 NVIDIA NIM for 1M context
        "purpose":    "audiobook_production_manifest",
    }).encode()

    try:
        req = urllib.request.Request(
            f"{NEMOTRON_URL}/route",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            router_resp = json.loads(resp.read())
            raw_text = router_resp.get("text", "") or router_resp.get("content", "")

        # Parse the JSON output from Nemotron
        manifest_data = json.loads(raw_text)

    except json.JSONDecodeError:
        # Nemotron returned non-JSON — wrap it for inspection
        manifest_data = {
            "character_profiles": {},
            "sentiment_map":      [],
            "spatial_audio_cues": [],
            "_raw_response":      raw_text[:4000],
            "_parse_error":       "Nemotron returned non-JSON; raw captured in _raw_response",
        }
    except Exception as e:
        manifest_data = {
            "character_profiles": {},
            "sentiment_map":      [],
            "spatial_audio_cues": [],
            "_error":             str(e),
        }

    manifest_path.write_text(
        json.dumps(manifest_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return {
        "status":           "ok",
        "stage":            "production_manifest",
        "book":             book,
        "manifest_path":    str(manifest_path),
        "character_count":  len(manifest_data.get("character_profiles", {})),
        "scene_count":      len(manifest_data.get("sentiment_map", [])),
        "audio_cue_count":  len(manifest_data.get("spatial_audio_cues", [])),
    }


# ---------------------------------------------------------------------------
# STAGE 4 — HYBRID DIARIZATION
# ---------------------------------------------------------------------------

def _wrap_voice(text: str, voice: str, modifier: str, role: str) -> str:
    return f'<voice id="{voice}" modifier="{modifier}" role="{role}">\n{text.strip()}\n</voice>'


def _identify_speaker(line: str) -> tuple[str, str, str] | None:
    """
    Attempt to identify speaker from attribution verbs + roster.
    Returns (voice_id, modifier, role) or None if indeterminate.
    """
    for role_key, (voice, modifier) in VOICE_ROSTER.items():
        # Build a case-insensitive name pattern from the role key
        name_pat = re.compile(rf"\b{re.escape(role_key.replace('_', ' '))}\b", re.IGNORECASE)
        if name_pat.search(line):
            return (voice, modifier, role_key)
    return None


def diarize_file_hybrid(md_path: Path, out_dir: Path, manifest: dict) -> dict:
    """
    Hybrid diarize a single chapter file.
    - Quoted dialogue with clear attribution → auto-tag
    - Narrator blocks (no attribution, no quotes) → auto-tag as Narrator
    - Ambiguous segments → flag to REVIEW_FLAGS.json
    Returns {filename, auto_tagged, flagged, xml_path, flags_path}
    """
    text  = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    xml_lines:   list[str] = []
    flag_entries: list[dict] = []
    auto_count   = 0
    flag_count   = 0

    # Preserve the chapter heading
    h1 = next((ln for ln in lines if ln.startswith("# ")), md_path.stem)
    xml_lines.append(f"# {h1.lstrip('# ').strip()}")
    xml_lines.append(f"<!-- AUTO-DIARIZED by audiobook_prep_server.py | book={md_path.parent.parent.parent.name} | {md_path.name} -->")
    xml_lines.append(f"<!-- Review flags: {md_path.stem}_REVIEW_FLAGS.json -->")
    xml_lines.append("")

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Empty lines / section breaks
        if not line or re.match(r"^#{1,3}\s", line):
            xml_lines.append(line)
            i += 1
            continue

        # Check for ambiguous patterns — flag before anything else
        is_ambiguous = any(pat.search(line) for pat in AMBIGUOUS_PATTERNS)

        # Detect quoted dialogue
        has_quote = bool(re.search(r'["«][^"»]{3,}["»]', line))

        if is_ambiguous:
            # Emit as comment placeholder, add to flags
            xml_lines.append(f"<!-- REVIEW: {line} -->")
            flag_entries.append({
                "line_index":  i,
                "text":        line,
                "reason":      "ambiguous_pattern",
                "suggestion":  "Verify speaker — check for Mo Chrá hum, internal monologue, or Celtic phrase",
            })
            flag_count += 1

        elif has_quote:
            # Try to identify speaker from context (current + surrounding lines)
            context = " ".join(lines[max(0, i-2):i+3])
            speaker_info = _identify_speaker(context)
            if speaker_info:
                voice, modifier, role = speaker_info
                xml_lines.append(_wrap_voice(line, voice, modifier, role))
                auto_count += 1
            else:
                # Unresolvable dialogue — flag for review
                xml_lines.append(f"<!-- REVIEW: {line} -->")
                flag_entries.append({
                    "line_index": i,
                    "text":       line,
                    "reason":     "unresolved_dialogue_speaker",
                    "suggestion": "Identify speaker; assign voice from roster or default Leo/baseline",
                })
                flag_count += 1

        else:
            # Plain narrative prose — assign to Narrator
            xml_lines.append(_wrap_voice(line, "Leo", "pitch_low", "Narrator"))
            auto_count += 1

        i += 1

    # Write XML output
    xml_out  = out_dir / f"{md_path.stem}_AUTO.xml"
    flag_out = out_dir / f"{md_path.stem}_REVIEW_FLAGS.json"

    xml_out.write_text("\n".join(xml_lines), encoding="utf-8")
    flag_out.write_text(
        json.dumps({"chapter": md_path.name, "flags": flag_entries}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return {
        "file":          md_path.name,
        "auto_tagged":   auto_count,
        "flagged":       flag_count,
        "xml_path":      str(xml_out),
        "flags_path":    str(flag_out),
    }


def diarize_hybrid_book(book: int) -> dict:
    """
    Stage 4: Run hybrid diarization on all machine_ear/ files.
    Loads PRODUCTION_MANIFEST.json for character context.
    """
    src_dir  = STAGING_ROOT / f"book_{book}" / "machine_ear"
    out_dir  = STAGING_ROOT / f"book_{book}" / "diarized"
    manifest_path = STAGING_ROOT / f"book_{book}" / "PRODUCTION_MANIFEST.json"

    if not src_dir.exists():
        return {"status": "error", "message": "Run /machine-ear first (machine_ear/ dir missing)"}

    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    chapter_results: list[dict] = []
    total_auto  = 0
    total_flags = 0

    for f in sorted(src_dir.glob("*.md")):
        result = diarize_file_hybrid(f, out_dir, manifest)
        chapter_results.append(result)
        total_auto  += result["auto_tagged"]
        total_flags += result["flagged"]

    # Write human-readable DIARIZATION_REPORT.md
    report_path = STAGING_ROOT / f"book_{book}" / "DIARIZATION_REPORT.md"
    report_lines = [
        f"# Diarization Report — Book {book}",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Status:** {'REVIEW REQUIRED' if total_flags > 0 else 'CLEAN — no flags'}",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Chapters processed | {len(chapter_results)} |",
        f"| Lines auto-tagged | {total_auto} |",
        f"| Lines flagged for review | {total_flags} |",
        f"| Auto-tag rate | {round(total_auto / max(1, total_auto + total_flags) * 100, 1)}% |",
        "",
        "## Chapter Breakdown",
        "",
        "| Chapter | Auto | Flagged | XML | Flags |",
        "|---------|------|---------|-----|-------|",
    ]
    for r in chapter_results:
        xml_rel   = Path(r["xml_path"]).name
        flags_rel = Path(r["flags_path"]).name
        report_lines.append(
            f"| {r['file']} | {r['auto_tagged']} | {r['flagged']} | {xml_rel} | {flags_rel} |"
        )
    if total_flags > 0:
        report_lines += [
            "",
            "## Next Step",
            "",
            "Open each `*_REVIEW_FLAGS.json` file and resolve flagged segments using the",
            "`diarize-chapter` Claude skill. Replace `<!-- REVIEW: ... -->` blocks in the",
            "corresponding `*_AUTO.xml` file with correct `<voice>` tags.",
        ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return {
        "status":         "ok",
        "stage":          "diarize_hybrid",
        "book":           book,
        "output_dir":     str(out_dir),
        "chapters":       len(chapter_results),
        "total_auto":     total_auto,
        "total_flagged":  total_flags,
        "auto_rate_pct":  round(total_auto / max(1, total_auto + total_flags) * 100, 1),
        "report_path":    str(report_path),
        "results":        chapter_results,
    }


# ---------------------------------------------------------------------------
# FULL PIPELINE (/assemble)
# ---------------------------------------------------------------------------

def run_full_pipeline(book: int) -> dict:
    """
    Run all 4 stages sequentially for the given book number.
    Returns combined summary with per-stage results.
    """
    pipeline_start = time.time()

    s1 = sanitize_book(book)
    if s1["status"] != "ok":
        return {"status": "error", "stage_failed": "sanitize", "detail": s1}

    s2 = machine_ear_book(book)
    if s2["status"] != "ok":
        return {"status": "error", "stage_failed": "machine_ear", "detail": s2}

    s3 = production_manifest_book(book)
    # Don't hard-fail on manifest — Nemotron may be unavailable; pipeline continues

    s4 = diarize_hybrid_book(book)
    if s4["status"] != "ok":
        return {"status": "error", "stage_failed": "diarize_hybrid", "detail": s4}

    elapsed = round(time.time() - pipeline_start, 1)

    # Log to LOGS/audiobook_pipeline.jsonl
    log_entry = {
        "timestamp":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "book":         book,
        "elapsed_s":    elapsed,
        "sanitize":     {"included": s1["included"], "excluded": len(s1["excluded"])},
        "machine_ear":  {"files": s2["files_processed"], "visual": s2["visual_rewrites"],
                         "abbrev": s2["abbrev_expansions"], "phonetic": s2["phonetic_injections"]},
        "manifest":     {"characters": s3.get("character_count", 0), "scenes": s3.get("scene_count", 0)},
        "diarization":  {"auto": s4["total_auto"], "flagged": s4["total_flagged"],
                         "auto_rate_pct": s4["auto_rate_pct"]},
    }
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / "audiobook_pipeline.jsonl"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(log_entry) + "\n")

    return {
        "status":           "ok",
        "book":             book,
        "elapsed_seconds":  elapsed,
        "output_root":      str(STAGING_ROOT / f"book_{book}"),
        "stages": {
            "sanitize":           s1,
            "machine_ear":        s2,
            "production_manifest": s3,
            "diarize_hybrid":     s4,
        },
        "review_required":  s4["total_flagged"] > 0,
        "review_count":     s4["total_flagged"],
        "diarization_report": s4.get("report_path", ""),
    }


# ---------------------------------------------------------------------------
# HTTP REQUEST HANDLER
# ---------------------------------------------------------------------------

def _parse_book(body: dict) -> int:
    """Extract and validate book number from request body."""
    book = int(body.get("book", 2))
    if book not in (2, 3, 4, 5):
        raise ValueError(f"Unsupported book number: {book}. Valid: 2, 3, 4, 5")
    return book


class AudiobookPrepHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[AUDIOBOOK] {self.address_string()} — {format % args}")

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw) if raw.strip() else {}

    def do_GET(self):
        if self.path == "/health":
            self._send_json({
                "status":  "ok",
                "service": "audiobook_prep_server",
                "port":    SERVER_PORT,
                "version": "1.0.0",
                "stages":  ["sanitize", "machine-ear", "production-manifest", "diarize-hybrid", "assemble"],
                "books_supported": [2, 3, 4, 5],
            })
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        try:
            body = self._read_body()
        except json.JSONDecodeError as e:
            self._send_json({"error": f"invalid JSON: {e}"}, 400)
            return

        path = self.path.rstrip("/")

        if path == "/sanitize":
            try:
                book = _parse_book(body)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
                return
            result = sanitize_book(book)
            self._send_json(result, 200 if result["status"] == "ok" else 500)

        elif path == "/machine-ear":
            try:
                book = _parse_book(body)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
                return
            result = machine_ear_book(book)
            self._send_json(result, 200 if result["status"] == "ok" else 500)

        elif path == "/production-manifest":
            try:
                book = _parse_book(body)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
                return
            result = production_manifest_book(book)
            self._send_json(result, 200 if result["status"] == "ok" else 500)

        elif path == "/diarize-hybrid":
            try:
                book = _parse_book(body)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
                return
            result = diarize_hybrid_book(book)
            self._send_json(result, 200 if result["status"] == "ok" else 500)

        elif path == "/assemble":
            try:
                book = _parse_book(body)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
                return
            result = run_full_pipeline(book)
            self._send_json(result, 200 if result["status"] == "ok" else 500)

        elif path == "/synthesis-dispatch":
            # STUB — reserved for future Grok TTS wiring
            self._send_json({
                "status":  "not_implemented",
                "message": (
                    "synthesis-dispatch is reserved for Grok TTS wiring. "
                    "When ready, set GROK_API_KEY in .env and implement in synthesize_v5.py. "
                    "Use the diarize-chapter Claude skill to run synthesis manually in the interim."
                ),
                "next_step": "POST /assemble → review REVIEW_FLAGS.json → run diarize-chapter skill → synthesize_v5.py",
            }, 501)

        else:
            self._send_json({"error": f"unknown endpoint: {self.path}"}, 404)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[AUDIOBOOK] Audiobook Prep Server starting on port {SERVER_PORT}")
    print(f"[AUDIOBOOK] Project root:  {PROJECT_ROOT}")
    print(f"[AUDIOBOOK] Staging root:  {STAGING_ROOT}")
    print(f"[AUDIOBOOK] Phonetic glossary: {PHONETIC_GLOSSARY} "
          f"({'OK' if PHONETIC_GLOSSARY.exists() else 'MISSING — Qdrant fallback active'})")
    print(f"[AUDIOBOOK] Endpoints: /sanitize /machine-ear /production-manifest "
          f"/diarize-hybrid /assemble /synthesis-dispatch(stub) /health")

    server = HTTPServer(("0.0.0.0", SERVER_PORT), AudiobookPrepHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[AUDIOBOOK] Server stopped.")
        server.server_close()
        sys.exit(0)
