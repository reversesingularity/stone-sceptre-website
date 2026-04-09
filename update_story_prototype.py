"""
DESKTOP-SINGULA — Story Prototype Service
==========================================
HTTP server (port 8767) that manages the Dual-Knowledge Graph for
The Nephilim Chronicles v2.0 Creative Swarm.

Two graphs are maintained in Qdrant:
    tnc_role_graph  — entity-relation-entity semantic triples
                      (who is who, what capabilities they have, what relationships)
    tnc_plot_graph  — causal event chains
                      (what happened, what caused it, what it leads to)

Endpoints:
    POST /extract-triples      — extract triples from chapter text via Nemotron/Ollama
    POST /upsert-triples       — embed + store triples in Qdrant
    POST /upsert-events        — embed + store plot events in Qdrant
    GET  /foreshadow-brief     — get unplanted narrative seeds for a chapter range
    GET  /check-contradictions — check proposed triples against LOCKED canon
    GET  /health               — health check

Usage:
    python update_story_prototype.py
"""

import json
import re
import hashlib
import time
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

# ── Config ─────────────────────────────────────────────────────────────────

QDRANT_URL      = "http://localhost:6333"
OLLAMA_URL      = "http://localhost:11434"
NEMOTRON_ROUTER = "http://localhost:8768"   # nemotron_tool_router.py
EMBED_MODEL     = "nomic-embed-text"
EXTRACT_MODEL   = "llama3.1"               # fallback if Nemotron unavailable
API_PORT        = 8767

ROLE_GRAPH_COLL = "tnc_role_graph"
PLOT_GRAPH_COLL = "tnc_plot_graph"

PROJECT_ROOT = r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles"

# ── Confidence Tiers ────────────────────────────────────────────────────────

CONFIDENCE_LOCKED    = "LOCKED"     # Published canon — immutable
CONFIDENCE_CONFIRMED = "CONFIRMED"  # Author-approved
CONFIDENCE_PROPOSED  = "PROPOSED"   # Agent suggestion — pending author decision
CONFIDENCE_INFERRED  = "INFERRED"   # Derived from context — flag for review

# ── Helpers ──────────────────────────────────────────────────────────────────

def qdrant_post(path, body):
    r = requests.post(f"{QDRANT_URL}{path}", json=body, timeout=60)
    r.raise_for_status()
    return r.json()


def embed(text):
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["embedding"]


def stable_id(text):
    """Generate a stable integer ID from text content."""
    h = hashlib.sha256(text.encode()).hexdigest()
    return int(h[:12], 16) % (2**53)  # safe int range for Qdrant


def call_ollama(prompt, model=EXTRACT_MODEL, system=""):
    """Call Ollama for LLM inference."""
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt}
        ],
        "stream": False,
        "format": "json",
    }
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]


def call_nemotron(payload):
    """Route heavy inference through Nemotron tool router (falls back to Ollama)."""
    try:
        r = requests.post(f"{NEMOTRON_ROUTER}/route", json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("result", "")
    except Exception:
        # Fallback: use Ollama llama3.1
        return call_ollama(payload.get("prompt", ""), model="llama3.1",
                           system=payload.get("system", ""))


def read_json_safely(text):
    """Extract the first JSON object or array from a possibly noisy response."""
    text = text.strip()
    # Find first { or [
    start = -1
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start == -1:
        return None
    # Find matching close bracket
    depth = 0
    open_ch  = text[start]
    close_ch = "}" if open_ch == "{" else "]"
    for i in range(start, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    return None
    return None


# ── Triple Extraction ─────────────────────────────────────────────────────────

TRIPLE_SYSTEM = """You are a semantic triple extractor for The Nephilim Chronicles.
Extract entity-relation-entity triples from the given chapter text.
Use ALL_CAPS_SNAKE_CASE for entity and relation names.
Output ONLY a JSON object with this exact structure:
{
  "role_triples": [
    {"subject": "ENTITY_A", "predicate": "RELATION", "object": "ENTITY_B"}
  ],
  "plot_events": [
    {
      "event_id": "B{book}_EVT_{seq:03d}",
      "description": "one-line description",
      "causes": ["event_id_1", "event_id_2"],
      "effects": ["description_of_effect_1"],
      "book": "{book}",
      "chapter_est": "{chapter}"
    }
  ]
}
Only extract triples that are explicit in the text. Do not infer."""

def extract_triples_from_chapter(chapter_text, book_num, chapter_num):
    """Ask LLM to extract role triples and plot events from chapter text."""
    system = TRIPLE_SYSTEM.format(book=book_num, chapter=chapter_num)
    prompt = (
        f"Book {book_num}, Chapter {chapter_num}:\n\n"
        f"{chapter_text[:8000]}"  # safety cap for Ollama context
    )

    # Try Nemotron first for accuracy; fall back to Ollama
    try:
        payload = {
            "task_type": "triple_extraction",
            "system": system,
            "prompt": prompt,
            "max_tokens": 2000,
        }
        raw = call_nemotron(payload)
    except Exception:
        raw = call_ollama(prompt, system=system)

    parsed = read_json_safely(raw)
    if not parsed:
        return {"role_triples": [], "plot_events": [], "parse_error": raw[:200]}

    return {
        "role_triples": parsed.get("role_triples", []),
        "plot_events":  parsed.get("plot_events", []),
    }


# ── Contradiction Check ───────────────────────────────────────────────────────

def check_contradictions(new_triples):
    """
    Check new triples against LOCKED canon in tnc_role_graph.
    Returns list of contradiction dicts.
    """
    contradictions = []

    for triple in new_triples:
        subject   = triple.get("subject", "")
        predicate = triple.get("predicate", "")
        obj       = triple.get("object", "")
        triple_text = f"{subject} {predicate} {obj}"

        # Semantic search for similar triples
        try:
            vec = embed(triple_text)
            result = qdrant_post(
                f"/collections/{ROLE_GRAPH_COLL}/points/search",
                {
                    "vector": vec,
                    "limit": 5,
                    "with_payload": True,
                    "filter": {
                        "must": [
                            {"key": "confidence", "match": {"value": CONFIDENCE_LOCKED}},
                            {"key": "subject",    "match": {"value": subject}},
                        ]
                    }
                }
            )
        except Exception:
            continue

        for hit in result.get("result", []):
            existing = hit["payload"]
            # Same subject + predicate but different object = potential contradiction
            if (existing.get("subject") == subject and
                existing.get("predicate") == predicate and
                existing.get("object") != obj and
                hit["score"] > 0.85):
                contradictions.append({
                    "proposed":       triple,
                    "existing_locked": existing,
                    "similarity":      round(hit["score"], 3),
                    "rule":           f"LOCKED triple exists: {existing['triple_text']}"
                })

    return contradictions


# ── Upsert Triples ────────────────────────────────────────────────────────────

def upsert_triples(triples, confidence=CONFIDENCE_PROPOSED, author_approved=False,
                   book_scope=None, added_by="story_prototype_service"):
    """Embed and upsert role triples into tnc_role_graph."""
    if author_approved:
        confidence = CONFIDENCE_CONFIRMED

    upserted, skipped, errors = 0, 0, []
    for triple in triples:
        subject   = triple.get("subject", "")
        predicate = triple.get("predicate", "")
        obj       = triple.get("object", "")

        if not (subject and predicate and obj):
            errors.append(f"Incomplete triple: {triple}")
            continue

        triple_text = f"{subject} {predicate} {obj}"
        point_id = stable_id(triple_text)

        # Check not already LOCKED before overwriting
        try:
            existing = qdrant_post(
                f"/collections/{ROLE_GRAPH_COLL}/points",
                {"ids": [point_id], "with_payload": True}
            )
            pts = existing.get("result", [])
            if pts and pts[0].get("payload", {}).get("confidence") == CONFIDENCE_LOCKED:
                skipped += 1
                continue
        except Exception:
            pass

        try:
            vec = embed(triple_text)
            point = {
                "id": point_id,
                "vector": vec,
                "payload": {
                    "subject":     subject,
                    "predicate":   predicate,
                    "object":      obj,
                    "triple_text": triple_text,
                    "confidence":  confidence,
                    "book_scope":  book_scope or ["3", "4", "5"],
                    "added_by":    added_by,
                    "timestamp":   datetime.now().isoformat(),
                    "entity_type": "triple",
                    "category":    "canon_fact",
                }
            }
            qdrant_post(f"/collections/{ROLE_GRAPH_COLL}/points",
                        {"points": [point]})
            upserted += 1
        except Exception as e:
            errors.append(f"{triple_text}: {e}")

    return {"upserted": upserted, "skipped_locked": skipped, "errors": errors}


def upsert_plot_events(events, author_approved=False, added_by="story_prototype_service"):
    """Embed and upsert plot events into tnc_plot_graph."""
    lock_status = "AUTHOR_APPROVED" if author_approved else "PROPOSED"
    upserted, errors = 0, []

    for event in events:
        desc       = event.get("description", "")
        event_id   = event.get("event_id", f"EVT_{stable_id(desc)}")
        book       = event.get("book", "?")
        chapter_est = event.get("chapter_est", "?")

        if not desc:
            errors.append(f"Empty event description: {event}")
            continue

        try:
            vec = embed(desc)
            point = {
                "id": stable_id(event_id + desc),
                "vector": vec,
                "payload": {
                    "event_id":    event_id,
                    "description": desc,
                    "causes":      event.get("causes", []),
                    "effects":     event.get("effects", []),
                    "book":        book,
                    "chapter_est": chapter_est,
                    "status":      "PLANNED",
                    "lock_status": lock_status,
                    "added_by":    added_by,
                    "timestamp":   datetime.now().isoformat(),
                    "entity_type": "event",
                    "category":    "plot_event",
                }
            }
            qdrant_post(f"/collections/{PLOT_GRAPH_COLL}/points",
                        {"points": [point]})
            upserted += 1
        except Exception as e:
            errors.append(f"{event_id}: {e}")

    return {"upserted": upserted, "errors": errors}


# ── Foreshadow Brief ──────────────────────────────────────────────────────────

def generate_foreshadow_brief(book, chapter):
    """
    Query the Plot Graph for effects that should be seeded by this chapter.
    Returns a list of narrative seeds for Agent 1.
    """
    # Search for events in earlier chapters whose effects should manifest ~now
    try:
        # Free-text search across plot graph
        query_text = f"Book {book} Chapter {chapter} effects consequences seeds"
        vec = embed(query_text)
        result = qdrant_post(
            f"/collections/{PLOT_GRAPH_COLL}/points/search",
            {
                "vector": vec,
                "limit": 20,
                "with_payload": True,
                "filter": {
                    "must": [
                        {"key": "book", "match": {"value": str(book)}}
                    ]
                }
            }
        )
    except Exception as e:
        return {"seeds": [], "error": str(e)}

    seeds = []
    for hit in result.get("result", []):
        payload = hit["payload"]
        effects = payload.get("effects", [])
        if effects:
            seeds.append({
                "source_event": payload.get("event_id"),
                "description": payload.get("description"),
                "effects_to_plant": effects,
                "relevance_score": round(hit["score"], 3),
            })

    return {
        "book": book,
        "chapter": chapter,
        "seeds": seeds[:10],  # top 10 most relevant
        "instruction": (
            "Weave these narrative seeds into the chapter. "
            "Do not resolve them — only plant the atmosphere or foreshadowing."
        )
    }


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class StoryPrototypeHandler(BaseHTTPRequestHandler):
    """Minimal HTTP server — same pattern as canon_search_api.py."""

    def log_message(self, format, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] {self.path} — {format % args}")

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    # ── GET ──────────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/health":
            self.send_json(200, {
                "status": "ok",
                "service": "update_story_prototype",
                "version": "2.0",
                "timestamp": datetime.now().isoformat(),
            })

        elif parsed.path == "/foreshadow-brief":
            book    = qs.get("book", ["3"])[0]
            chapter = qs.get("chapter", ["1"])[0]
            result  = generate_foreshadow_brief(book, chapter)
            self.send_json(200, result)

        elif parsed.path == "/check-contradictions":
            body = self.read_body()
            triples = body.get("triples", [])
            contradictions = check_contradictions(triples)
            self.send_json(200, {
                "contradiction_count": len(contradictions),
                "contradictions": contradictions,
            })

        else:
            self.send_json(404, {"error": f"Unknown path: {parsed.path}"})

    # ── POST ─────────────────────────────────────────────────────────────────

    def do_POST(self):
        parsed = urlparse(self.path)
        body   = self.read_body()

        if parsed.path == "/extract-triples":
            chapter_text = body.get("chapter_text", "")
            book_num     = body.get("book_num", 3)
            chapter_num  = body.get("chapter_num", 1)

            if not chapter_text:
                self.send_json(400, {"error": "chapter_text required"})
                return

            extracted = extract_triples_from_chapter(chapter_text, book_num, chapter_num)
            contradictions = check_contradictions(extracted.get("role_triples", []))

            # Generate foreshadow brief
            foreshadow = generate_foreshadow_brief(book_num, chapter_num)

            self.send_json(200, {
                "role_triples":    extracted.get("role_triples", []),
                "plot_events":     extracted.get("plot_events", []),
                "contradictions":  contradictions,
                "foreshadow_brief": foreshadow,
                "parse_error":     extracted.get("parse_error"),
            })

        elif parsed.path == "/upsert-triples":
            triples        = body.get("triples", [])
            confidence     = body.get("confidence", CONFIDENCE_PROPOSED)
            author_approved = body.get("author_approved", False)
            collection     = body.get("collection_name", ROLE_GRAPH_COLL)

            result = upsert_triples(triples, confidence, author_approved)
            self.send_json(200, result)

        elif parsed.path == "/upsert-events":
            events          = body.get("events", [])
            author_approved = body.get("author_approved", False)

            result = upsert_plot_events(events, author_approved)
            self.send_json(200, result)

        elif parsed.path == "/persona-arc-delta":
            # Called by Nemoclaw after chapter save to track character state deltas
            # and upsert updated persona data to tnc_personas
            chapter_text = body.get("chapter_text", "")
            book_num     = body.get("book_num", "?")
            chapter_id   = body.get("chapter_id", "unknown")

            if not chapter_text:
                self.send_json(400, {"error": "chapter_text required"})
                return

            KEY_CHARACTERS = [
                "Cian", "Miriam", "Brennan", "Elijah", "Enoch",
                "Raphael", "Liaigh", "Azazel", "Naamah", "Ohya",
                "Shemyaza", "James",
            ]

            updated = []
            for char in KEY_CHARACTERS:
                if char.lower() not in chapter_text.lower():
                    continue

                paras = [p for p in chapter_text.split("\n\n")
                         if char.lower() in p.lower()]
                if not paras:
                    continue

                excerpt = "\n".join(paras[:3])[:1000]

                # Extract the arc delta via Nemotron (with Ollama fallback)
                delta_prompt = (
                    f"In this chapter excerpt, identify what CHANGED for {char}. "
                    f"List concrete state changes: location, relationships, abilities, "
                    f"knowledge gained, wounds, emotional state. Be brief.\n\n{excerpt}"
                )
                try:
                    r = requests.post(
                        NEMOTRON_ROUTER + "/route",
                        json={"task": "persona_delta", "prompt": delta_prompt,
                              "max_tokens": 200},
                        timeout=60
                    )
                    delta_text = r.json().get("response", excerpt) if r.status_code < 400 else excerpt
                except Exception:
                    delta_text = excerpt

                payload = {
                    "character_id":        char.upper(),
                    "name":                char,
                    "last_seen_chapter":   chapter_id,
                    "last_seen_book":      str(book_num),
                    "arc_delta":           delta_text[:500],
                    "excerpt":             excerpt,
                    "timestamp":           datetime.now().isoformat(),
                    "entity_type":         "character",
                    "category":            "dossier",
                }

                try:
                    vec = embed(excerpt)
                    point_id = stable_id(char.upper() + str(book_num) + chapter_id)
                    qdrant_post(
                        f"/collections/tnc_personas/points",
                        {"points": [{"id": point_id, "vector": vec, "payload": payload}]}
                    )
                    updated.append(char)
                except Exception as e:
                    pass  # non-fatal; continue with other characters

            self.send_json(200, {"updated_personas": updated, "chapter": chapter_id})

        else:
            self.send_json(404, {"error": f"Unknown path: {parsed.path}"})


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 60)
    print("  STORY PROTOTYPE SERVICE — The Nephilim Chronicles v2.0")
    print(f"  Listening on http://localhost:{API_PORT}")
    print("  Endpoints:")
    print("    POST /extract-triples      — extract from chapter text")
    print("    POST /upsert-triples       — store role triples")
    print("    POST /upsert-events        — store plot events")
    print("    GET  /foreshadow-brief     — get narrative seeds")
    print("    GET  /check-contradictions — validate against canon")
    print("    POST /persona-arc-delta    — track character state deltas")
    print("    GET  /health               — service health")
    print("═" * 60 + "\n")

    server = HTTPServer(("", API_PORT), StoryPrototypeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down Story Prototype Service.")
        server.server_close()


if __name__ == "__main__":
    main()
