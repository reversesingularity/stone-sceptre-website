"""
ingest_jubilees.py
------------------
Ingests Jubilees annotation data and Strongs concordance into the
existing 'nephilim_chronicles' Qdrant collection.

Sources:
  - jubilees_annotated.html   (16.6 MB — main text with annotations)
  - jubilees_data/*.json      (45+ JSON chapter files)
  - hebrew_strongs.json       (2.6 MB — Hebrew lexicon)
  - greek_strongs.json        (1.5 MB — Greek lexicon)
  - jubilees_kjv_mapping.csv  (9.9 MB — verse mappings)
  - StrongsIndex.csv          (6.1 MB — selective: entries with definitions)
  SKIP: MainIndex.csv (74 MB — bulk data unsuitable for vector search)

Config:
  Set JUBILEES_DIR below, then run:  python ingest_jubilees.py

Requirements: pip install qdrant-client sentence-transformers beautifulsoup4
"""

import json
import csv
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

JUBILEES_DIR = Path(r"F:\Projects-cmodi.000\Project Jubilees Annotation")

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION  = "nephilim_chronicles"

# Embed via Ollama nomic-embed-text (consistent with existing vectors)
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE    = 800   # chars (same as ingest_canon.py)
CHUNK_OVERLAP = 150   # chars

# Starting point ID — above existing 18,021 vectors to avoid collision
#   We use a separate ID namespace starting at 100_000
ID_OFFSET = 100_000

# ---------------------------------------------------------------------------
# TEXT UTILITIES
# ---------------------------------------------------------------------------

def chunk_text(text: str, source: str, category: str, base_id: int) -> list[dict]:
    """
    Split text into overlapping chunks; return list of doc dicts.
    """
    text = text.strip()
    if not text:
        return []

    docs = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    i = 0
    chunk_num = 0
    while i < len(text):
        chunk = text[i : i + CHUNK_SIZE]
        chunk = chunk.strip()
        if len(chunk) > 50:  # skip tiny trailing fragments
            docs.append({
                "id":       base_id + chunk_num,
                "text":     chunk,
                "source":   source,
                "category": category,
            })
            chunk_num += 1
        i += step
    return docs


def clean_html_simple(html_content: str) -> str:
    """Strip HTML tags and decode entities — simple version."""
    # Remove scripts and style blocks
    html_content = re.sub(r"<script[^>]*>.*?</script>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r"<style[^>]*>.*?</style>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
    # Replace block elements with newlines
    html_content = re.sub(r"<(p|br|div|h[1-6]|tr|li)[^>]*>", "\n", html_content, flags=re.IGNORECASE)
    # Strip remaining tags
    html_content = re.sub(r"<[^>]+>", " ", html_content)
    # Decode common entities
    html_content = html_content.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    html_content = html_content.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    # Normalise whitespace
    html_content = re.sub(r"\n{3,}", "\n\n", html_content)
    html_content = re.sub(r"[ \t]+", " ", html_content)
    return html_content.strip()


# ---------------------------------------------------------------------------
# EMBEDDING
# ---------------------------------------------------------------------------

def get_embedding(text: str) -> list[float]:
    """Call Ollama nomic-embed-text for a single text chunk."""
    import urllib.request
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["embedding"]


# ---------------------------------------------------------------------------
# QDRANT
# ---------------------------------------------------------------------------

def get_qdrant_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def upsert_docs(client, docs: list[dict], batch_size: int = 50) -> int:
    """Embed and upsert documents into Qdrant in batches. Returns count inserted."""
    from qdrant_client.models import PointStruct

    total = 0
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        points = []
        for doc in batch:
            try:
                vec = get_embedding(doc["text"])
                points.append(PointStruct(
                    id=doc["id"],
                    vector=vec,
                    payload={
                        "text":     doc["text"],
                        "source":   doc["source"],
                        "category": doc["category"],
                    },
                ))
            except Exception as e:
                print(f"    [WARN] Embedding failed for id={doc['id']}: {e}")
                continue

        if points:
            client.upsert(collection_name=COLLECTION, points=points)
            total += len(points)
            print(f"    Upserted batch of {len(points)} — running total: {total}")

    return total


# ---------------------------------------------------------------------------
# SOURCE PARSERS
# ---------------------------------------------------------------------------

def load_jubilees_html() -> list[dict]:
    """Parse jubilees_annotated.html → text chunks."""
    path = JUBILEES_DIR / "jubilees_annotated.html"
    if not path.exists():
        print(f"  [SKIP] Not found: {path}")
        return []

    print(f"  Reading {path.name} ({path.stat().st_size // 1024} KB)...")
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = clean_html_simple(raw)
    print(f"    → Extracted {len(text):,} chars of text")

    return chunk_text(text, source="jubilees_annotated.html", category="jubilees", base_id=ID_OFFSET)


def load_jubilees_data_folder() -> list[dict]:
    """
    Parse jubilees_data/*.json chapter files.
    Structure: {"1": {"text": "...", "he": "...", "links": [...]}, "2": {...}, ...}
    Keys are verse numbers (strings). Each verse has 'text' (English) and 'he' (Hebrew).
    """
    folder = JUBILEES_DIR / "jubilees_data"
    if not folder.exists():
        print(f"  [SKIP] Not found: {folder}")
        return []

    files = sorted(folder.glob("*.json"))
    print(f"  Found {len(files)} JSON files in jubilees_data/")

    docs = []
    base_id = ID_OFFSET + 50_000

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            print(f"    [WARN] {f.name}: {e}")
            continue

        # Extract chapter number from filename (chapter_1.json → "Chapter 1")
        chapter_label = f.stem.replace("_", " ").title()  # "chapter_1" → "Chapter 1"

        text_parts = []
        if isinstance(data, dict):
            # Check if it's the verse-keyed format: {"1": {"text": ..., "he": ...}, ...}
            for key in sorted(data.keys(), key=lambda k: int(k) if k.isdigit() else 0):
                val = data[key]
                if isinstance(val, dict):
                    en_text = val.get("text", "").strip()
                    he_text = val.get("he", "").strip()
                    verse_text = f"Jubilees {chapter_label}:{key}"
                    if en_text:
                        verse_text += f" — {en_text}"
                    if he_text:
                        verse_text += f" | Hebrew: {he_text}"
                    text_parts.append(verse_text)
                elif isinstance(val, str) and val.strip():
                    text_parts.append(f"Jubilees {chapter_label}:{key} — {val.strip()}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict):
                    en = item.get("text", item.get("content", ""))
                    if en:
                        text_parts.append(en)
        elif isinstance(data, str):
            text_parts = [data]

        combined = "\n".join(part for part in text_parts if part.strip())
        if combined.strip():
            chunks = chunk_text(combined, source=f"jubilees_data/{f.name}", category="jubilees", base_id=base_id)
            docs.extend(chunks)
            base_id += len(chunks) + 10  # leave gap between files

    print(f"    → {len(docs)} chunks from jubilees_data/ ({len(files)} chapters)")
    return docs


def load_external_parallels() -> list[dict]:
    """Parse external_parallels.json — cross-references to other ancient texts."""
    path = JUBILEES_DIR / "external_parallels.json"
    if not path.exists():
        print(f"  [SKIP] Not found: {path}")
        return []

    print(f"  Reading {path.name} ({path.stat().st_size // 1024} KB)...")
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        print(f"    [ERROR] {e}")
        return []

    # Build text blocks from each parallel entry
    docs = []
    base_id = ID_OFFSET + 180_000

    def flatten_entry(entry, depth=0) -> list[str]:
        """Recursively extract text from a parallel entry."""
        parts = []
        if isinstance(entry, str):
            parts.append(entry)
        elif isinstance(entry, dict):
            for k, v in entry.items():
                if isinstance(v, str) and v.strip():
                    parts.append(f"{k}: {v}")
                elif isinstance(v, (dict, list)):
                    parts.extend(flatten_entry(v, depth + 1))
        elif isinstance(entry, list):
            for item in entry:
                parts.extend(flatten_entry(item, depth + 1))
        return parts

    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = list(data.values())
    else:
        entries = [str(data)]

    buffer = []
    i = 0
    for entry in entries:
        lines = flatten_entry(entry)
        text = "\n".join(l for l in lines if l.strip())
        if text.strip():
            buffer.append(text)
        if len(buffer) >= 3:
            docs.append({
                "id":       base_id + i,
                "text":     "\n\n".join(buffer),
                "source":   "external_parallels.json",
                "category": "jubilees_parallels",
            })
            buffer = []
            i += 1

    if buffer:
        docs.append({
            "id":       base_id + i,
            "text":     "\n\n".join(buffer),
            "source":   "external_parallels.json",
            "category": "jubilees_parallels",
        })

    print(f"    → {len(docs)} chunks from external_parallels.json")
    return docs


def load_strongs_json(filename: str, category: str) -> list[dict]:
    """Parse hebrew_strongs.json or greek_strongs.json."""
    path = JUBILEES_DIR / filename
    if not path.exists():
        print(f"  [SKIP] Not found: {path}")
        return []

    print(f"  Reading {path.name} ({path.stat().st_size // 1024} KB)...")
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        print(f"    [ERROR] {e}")
        return []

    # Strongs JSON is typically:
    #   { "H1": {"word": "אָב", "transliteration": "ab", "definition": "father", ...}, ... }
    # OR a list of such objects. Handle both.
    entries = []
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict):
                val["strongs_id"] = key
                entries.append(val)
            elif isinstance(val, str):
                entries.append({"strongs_id": key, "definition": val})
    elif isinstance(data, list):
        entries = data

    # Build text blocks from each entry
    docs = []
    if category == "strongs_hebrew":
        base_id = ID_OFFSET + 200_000
    else:
        base_id = ID_OFFSET + 300_000

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        parts = []
        strongs_id = entry.get("strongs_id", entry.get("id", f"#{i}"))
        word = entry.get("word", entry.get("unicode", ""))
        translit = entry.get("transliteration", entry.get("translit", ""))
        definition = entry.get("definition", entry.get("desc", entry.get("kjv_def", "")))
        usage = entry.get("usage", entry.get("lit", ""))

        parts.append(f"Strongs {strongs_id}: {word} ({translit})")
        if definition:
            parts.append(f"Definition: {definition}")
        if usage:
            parts.append(f"Usage: {usage}")

        text = " | ".join(p for p in parts if p.strip())
        if len(text) > 20:
            docs.append({
                "id":       base_id + i,
                "text":     text,
                "source":   filename,
                "category": category,
            })

    print(f"    → {len(docs)} Strongs entries from {filename}")
    return docs


def load_jubilees_kjv_mapping() -> list[dict]:
    """Parse jubilees_kjv_mapping.csv into verse-pair chunks."""
    path = JUBILEES_DIR / "jubilees_kjv_mapping.csv"
    if not path.exists():
        print(f"  [SKIP] Not found: {path}")
        return []

    print(f"  Reading {path.name} ({path.stat().st_size // 1024} KB)...")
    docs = []
    base_id = ID_OFFSET + 400_000

    # Group every 5 rows into one chunk (verse mappings are short)
    buffer = []
    i = 0
    try:
        with open(path, encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Build readable text from row
                parts = [f"{k}: {v}" for k, v in row.items() if v and v.strip()]
                line = " | ".join(parts)
                if line.strip():
                    buffer.append(line)
                if len(buffer) >= 5:
                    docs.append({
                        "id":       base_id + i,
                        "text":     "\n".join(buffer),
                        "source":   "jubilees_kjv_mapping.csv",
                        "category": "jubilees_kvj_mapping",
                    })
                    buffer = []
                    i += 1
        if buffer:
            docs.append({
                "id":       base_id + i,
                "text":     "\n".join(buffer),
                "source":   "jubilees_kjv_mapping.csv",
                "category": "jubilees_kvj_mapping",
            })
    except Exception as e:
        print(f"    [ERROR] {e}")
        return []

    print(f"    → {len(docs)} chunks from jubilees_kjv_mapping.csv")
    return docs


def load_strongs_index_csv() -> list[dict]:
    """
    Parse StrongsIndex.csv.
    NOTE: If the file only has WordID + StrongsID columns (mapping table only),
    it is automatically skipped as it has no semantic content for vector search.
    Only processes files that have definition/meaning columns.
    """
    path = JUBILEES_DIR / "StrongsIndex.csv"
    if not path.exists():
        print(f"  [SKIP] Not found: {path}")
        return []

    print(f"  Reading {path.name} ({path.stat().st_size // 1024} KB) — checking content...")
    docs = []
    base_id = ID_OFFSET + 500_000

    try:
        with open(path, encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            def_cols = [h for h in headers if any(w in h.lower() for w in ["def", "meaning", "gloss", "desc", "translation", "word", "kjv"])]
            content_cols = [h for h in headers if h.lower() not in ["wordid", "strongsid", "id"]]
            print(f"    Headers: {headers} | Meaningful content cols: {content_cols}")

            if not content_cols:
                print(f"    → SKIPPED — only ID/reference columns detected (no semantic content)")
                return []

            buffer = []
            i = 0
            for row in reader:
                parts = [f"{k}: {v}" for k, v in row.items() if v and v.strip() and len(v) < 500]
                line = " | ".join(parts)
                if line.strip():
                    buffer.append(line)
                if len(buffer) >= 5:
                    docs.append({
                        "id":       base_id + i,
                        "text":     "\n".join(buffer),
                        "source":   "StrongsIndex.csv",
                        "category": "strongs_index",
                    })
                    buffer = []
                    i += 1

            if buffer:
                docs.append({
                    "id":       base_id + i,
                    "text":     "\n".join(buffer),
                    "source":   "StrongsIndex.csv",
                    "category": "strongs_index",
                })
    except Exception as e:
        print(f"    [ERROR] {e}")
        return []

    print(f"    → {len(docs)} filtered chunks from StrongsIndex.csv")
    return docs


def load_jubilees_plaintext() -> list[dict]:
    """
    Load the plain-text Jubilees edition (An Annotated Digital Edition...).
    Useful as clean prose input for semantic search.
    """
    path = JUBILEES_DIR / "An Annotated Digital Edition of the Book of Jubilees.txt"
    if not path.exists():
        print(f"  [SKIP] Not found: {path}")
        return []

    print(f"  Reading {path.name} ({path.stat().st_size // 1024} KB)...")
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    print(f"    → {len(text):,} chars extracted")

    return chunk_text(text, source=path.name, category="jubilees_plaintext", base_id=ID_OFFSET + 550_000)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("JUBILEES & STRONGS QDRANT INGESTION")
    print(f"Target collection: {COLLECTION} @ {QDRANT_HOST}:{QDRANT_PORT}")
    print(f"Source directory:  {JUBILEES_DIR}")
    print("=" * 60)

    # Verify Jubilees directory exists
    if not JUBILEES_DIR.exists():
        print(f"\n[ERROR] JUBILEES_DIR not found: {JUBILEES_DIR}")
        print("Update the JUBILEES_DIR config at the top of this script.")
        sys.exit(1)

    # Verify Qdrant is reachable
    try:
        client = get_qdrant_client()
        info = client.get_collection(COLLECTION)
        existing = info.points_count
        print(f"\nQdrant OK — existing points in '{COLLECTION}': {existing:,}")
    except Exception as e:
        print(f"\n[ERROR] Qdrant not reachable: {e}")
        sys.exit(1)

    # Verify Ollama is reachable
    try:
        import urllib.request
        with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=5) as r:
            models = json.loads(r.read()).get("models", [])
            model_names = [m["name"] for m in models]
            if not any(EMBED_MODEL in n for n in model_names):
                print(f"[WARN] '{EMBED_MODEL}' not found in Ollama models: {model_names}")
                print("       Run: ollama pull nomic-embed-text")
            else:
                print(f"Ollama OK — {EMBED_MODEL} available")
    except Exception as e:
        print(f"[ERROR] Ollama not reachable at {OLLAMA_HOST}: {e}")
        sys.exit(1)

    # ── Load all sources ────────────────────────────────────────────────────
    all_docs = []

    print("\n[1/7] jubilees_annotated.html")
    all_docs.extend(load_jubilees_html())

    print(f"\n[2/7] jubilees_data/ folder (100 chapter JSON files)")
    all_docs.extend(load_jubilees_data_folder())

    print(f"\n[3/7] external_parallels.json")
    all_docs.extend(load_external_parallels())

    print(f"\n[4/7] hebrew_strongs.json")
    all_docs.extend(load_strongs_json("hebrew_strongs.json", "strongs_hebrew"))

    print(f"\n[5/7] greek_strongs.json")
    all_docs.extend(load_strongs_json("greek_strongs.json", "strongs_greek"))

    print(f"\n[6/7] jubilees_kjv_mapping.csv")
    all_docs.extend(load_jubilees_kjv_mapping())

    print(f"\n[7/8] StrongsIndex.csv (selective — auto-skip if mapping-only)")
    all_docs.extend(load_strongs_index_csv())

    print(f"\n[8/8] Plain-text Jubilees edition")
    all_docs.extend(load_jubilees_plaintext())

    print(f"\n{'=' * 60}")
    print(f"TOTAL DOCUMENTS TO INGEST: {len(all_docs):,}")
    print(f"{'=' * 60}")

    if not all_docs:
        print("[ERROR] No documents loaded — check JUBILEES_DIR path and file presence.")
        sys.exit(1)

    # Check for ID collisions
    ids = [d["id"] for d in all_docs]
    if len(ids) != len(set(ids)):
        print("[WARN] Duplicate IDs detected — deduplicating...")
        seen = set()
        deduped = []
        for d in all_docs:
            if d["id"] not in seen:
                seen.add(d["id"])
                deduped.append(d)
        all_docs = deduped
        print(f"       After dedup: {len(all_docs):,}")

    # Show summary by category
    from collections import Counter
    cats = Counter(d["category"] for d in all_docs)
    print("\nBy category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat:<30} {count:>6,}")

    # Confirm before running
    print(f"\nEstimated embedding time: {len(all_docs) * 0.08 / 60:.0f}–{len(all_docs) * 0.15 / 60:.0f} minutes on RTX 3080")
    print("\nStarting ingestion in 5 seconds... (Ctrl+C to abort)")
    import time
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("Aborted.")
        sys.exit(0)

    # ── Ingest ──────────────────────────────────────────────────────────────
    print("\nIngesting...")
    grand_total = upsert_docs(client, all_docs, batch_size=50)

    # ── Final report ────────────────────────────────────────────────────────
    updated_info = client.get_collection(COLLECTION)
    print(f"\n{'=' * 60}")
    print(f"INGESTION COMPLETE")
    print(f"  Documents inserted: {grand_total:,}")
    print(f"  Previous count:     {existing:,}")
    print(f"  New total:          {updated_info.points_count:,}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
