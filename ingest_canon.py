"""
DESKTOP-SINGULA -- Nephilim Chronicles Canon Ingestion Pipeline v2
Embeds all Chronicles canon files into Qdrant for semantic search.

Sources:
  1. F:\\Projects-cmodi.000\\book_writer_ai_toolkit\\output\\nephilim_chronicles
     (markdown canon, manuscripts, worldbuilding, session logs)
  2. C:\\Users\\cmodi.000\\OneDrive\\Desktop\\TNC
     (final production docx files -- authoritative published text)

Uses:
  - Ollama nomic-embed-text (local GPU) for embeddings
  - Qdrant (local Docker) for vector storage

Run: python ingest_canon.py
"""

import os
import sys
import json
import time
import hashlib
import requests

# ── Configuration ─────────────────────────────────────────────────────────────

CHRONICLES_ROOT = r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles"
TNC_DESKTOP     = r"C:\Users\cmodi.000\OneDrive\Desktop\TNC"

OLLAMA_URL      = "http://localhost:11434"
QDRANT_URL      = "http://localhost:6333"
EMBED_MODEL     = "nomic-embed-text"
COLLECTION_NAME = "nephilim_chronicles"
CHUNK_SIZE      = 800
CHUNK_OVERLAP   = 150

# Directories to ingest from CHRONICLES_ROOT (relative paths)
INGEST_DIRS = [
    "CANON",
    os.path.join("MANUSCRIPT", "book_1"),
    "WORLDBUILDING",
    "REFERENCE",
    os.path.join("ARCHIVE", "session_logs"),
]

# Files to ingest directly from TNC_DESKTOP (docx only, top level)
TNC_DOCX_FILES = [
    "Prologue.docx",
    "Body.docx",
    "Appendices.docx",
    "Dedication.docx",
    "Epigraph.docx",
    "Epilogue.docx",
    "Foreword.docx",
    "Title.docx",
    "Title_Copyright.docx",
    "TOC_Page.docx",
    "NephilimChronicles_Book1_MANUSCRIPT.docx",
    "Paperback KDP Ready.docx",
    "template.docx",
]

VALID_MD_EXTENSIONS  = {".md", ".txt"}
SKIP_PATTERNS        = {".git", ".venv", "__pycache__", "superseded"}


# ── Text Extraction ────────────────────────────────────────────────────────────

def extract_docx_text(filepath):
    """Extract plain text from a .docx file using python-docx."""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        print(f"\n  WARNING: Could not read docx {os.path.basename(filepath)}: {e}")
        return ""


def extract_text(filepath):
    """Extract text from a file based on its extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".docx":
        return extract_docx_text(filepath)
    else:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"\n  WARNING: Could not read {os.path.basename(filepath)}: {e}")
            return ""


# ── Helpers ────────────────────────────────────────────────────────────────────

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += size - overlap
    return chunks


def get_embedding(text):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["embedding"]


def qdrant_request(method, path, data=None):
    url = f"{QDRANT_URL}{path}"
    if   method == "GET":    r = requests.get(url, timeout=30)
    elif method == "PUT":    r = requests.put(url, json=data, timeout=30)
    elif method == "POST":   r = requests.post(url, json=data, timeout=60)
    elif method == "DELETE": r = requests.delete(url, timeout=30)
    r.raise_for_status()
    return r.json()


def create_collection(vector_size=768):
    try:
        qdrant_request("GET", f"/collections/{COLLECTION_NAME}")
        print(f"  Collection '{COLLECTION_NAME}' already exists.")
        choice = input("  Re-ingest everything? Deletes existing data. (y/n): ").strip().lower()
        if choice == 'y':
            qdrant_request("DELETE", f"/collections/{COLLECTION_NAME}")
            print("  Deleted existing collection.")
        else:
            print("  Keeping existing data. Adding new documents.")
            return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code != 404:
            raise

    qdrant_request("PUT", f"/collections/{COLLECTION_NAME}", {
        "vectors": {"size": vector_size, "distance": "Cosine"}
    })
    print(f"  Created collection '{COLLECTION_NAME}' ({vector_size}d Cosine)")
    return True


def get_category_chronicles(filepath):
    rel = os.path.relpath(filepath, CHRONICLES_ROOT).replace("\\", "/")
    if rel.startswith("CANON/dossiers"):      return "dossier"
    elif rel.startswith("CANON"):             return "canon"
    elif rel.startswith("MANUSCRIPT"):        return "manuscript"
    elif rel.startswith("WORLDBUILDING"):     return "worldbuilding"
    elif rel.startswith("REFERENCE"):         return "reference"
    elif rel.startswith("ARCHIVE/session"):   return "session_log"
    else:                                     return "other"


def collect_chronicles_files():
    files = []
    for rel_dir in INGEST_DIRS:
        abs_dir = os.path.join(CHRONICLES_ROOT, rel_dir)
        if not os.path.exists(abs_dir):
            print(f"  WARNING: Not found, skipping: {abs_dir}")
            continue
        for root, dirs, filenames in os.walk(abs_dir):
            dirs[:] = [d for d in dirs if not any(s in d for s in SKIP_PATTERNS)]
            for fname in filenames:
                if os.path.splitext(fname)[1].lower() in VALID_MD_EXTENSIONS:
                    files.append((os.path.join(root, fname), get_category_chronicles))
    return files


def collect_tnc_files():
    files = []
    for fname in TNC_DOCX_FILES:
        fpath = os.path.join(TNC_DESKTOP, fname)
        if os.path.exists(fpath):
            files.append((fpath, lambda fp: "production_docx"))
        else:
            print(f"  WARNING: TNC file not found: {fname}")
    return files


# ── Main Ingestion ─────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 64)
    print("  NEPHILIM CHRONICLES -- CANON INGESTION PIPELINE v2")
    print("  Sources: Chronicles Root + TNC Desktop (production docx)")
    print("  Engine:  Qdrant + Ollama nomic-embed-text | RTX 3080")
    print("=" * 64)
    print()

    # 1. Check dependencies
    print("[1/6] Checking dependencies...")
    try:
        from docx import Document
        print("  python-docx: READY")
    except ImportError:
        print("  Installing python-docx...")
        os.system("pip install python-docx --quiet")
        from docx import Document
        print("  python-docx: INSTALLED")

    # 2. Check services
    print()
    print("[2/6] Checking services...")
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        if not any("nomic-embed-text" in m for m in models):
            print("  ERROR: nomic-embed-text not found. Run PULL-MODELS.ps1 first.")
            sys.exit(1)
        print("  Ollama: ONLINE  |  nomic-embed-text: READY")
    except Exception as e:
        print(f"  ERROR: Cannot reach Ollama: {e}")
        sys.exit(1)

    try:
        qdrant_request("GET", "/")
        print("  Qdrant: ONLINE")
    except Exception as e:
        print(f"  ERROR: Cannot reach Qdrant: {e}")
        sys.exit(1)

    # 3. Probe embedding dimensions
    print()
    print("[3/6] Probing embedding dimensions...")
    test_embed = get_embedding("The Nephilim Chronicles")
    vector_size = len(test_embed)
    print(f"  Vector size: {vector_size} dimensions")

    # 4. Create collection
    print()
    print("[4/6] Setting up Qdrant collection...")
    create_collection(vector_size)

    # 5. Collect all files
    print()
    print("[5/6] Scanning all source files...")

    chronicles_files = collect_chronicles_files()
    tnc_files        = collect_tnc_files()
    all_files        = chronicles_files + tnc_files

    print(f"  Chronicles root files : {len(chronicles_files)}")
    print(f"  TNC Desktop docx files: {len(tnc_files)}")
    print(f"  Total files           : {len(all_files)}")
    print()

    from collections import Counter
    all_cats = []
    for fp, cat_fn in all_files:
        all_cats.append(cat_fn(fp))
    for cat, count in sorted(Counter(all_cats).items()):
        print(f"    {cat:25s}: {count} files")
    print()

    # 6. Ingest
    print("[6/6] Embedding and loading into Qdrant...")
    print()

    total_chunks = 0
    total_files  = 0
    errors       = []
    point_id     = 1

    for i, (filepath, cat_fn) in enumerate(all_files):
        filename = os.path.basename(filepath)
        category = cat_fn(filepath)

        # Determine relative path for payload
        if filepath.startswith(CHRONICLES_ROOT):
            rel_path = os.path.relpath(filepath, CHRONICLES_ROOT).replace("\\", "/")
            source   = "chronicles_root"
        else:
            rel_path = os.path.relpath(filepath, TNC_DESKTOP).replace("\\", "/")
            source   = "tnc_desktop"

        try:
            text = extract_text(filepath)
            if not text.strip():
                continue

            chunks = chunk_text(text)
            points = []

            for j, chunk in enumerate(chunks):
                embedding = get_embedding(chunk)
                points.append({
                    "id":     point_id,
                    "vector": embedding,
                    "payload": {
                        "source_file":  rel_path,
                        "source_root":  source,
                        "filename":     filename,
                        "category":     category,
                        "chunk_index":  j,
                        "total_chunks": len(chunks),
                        "text":         chunk,
                        "file_hash":    hashlib.md5(text.encode()).hexdigest()[:8]
                    }
                })
                point_id    += 1
                total_chunks += 1

            # Batch upsert to Qdrant
            qdrant_request("PUT", f"/collections/{COLLECTION_NAME}/points", {"points": points})

            total_files += 1
            pct = int(30 * (i+1) / len(all_files))
            bar = "#" * pct
            print(f"\r  [{bar:<30}] {i+1}/{len(all_files)} | {filename[:38]:<38} | {len(chunks):3d} chunks", end="", flush=True)

        except Exception as e:
            errors.append((filename, str(e)))
            print(f"\n  ERROR: {filename}: {e}")

    print()
    print()
    print("=" * 64)
    print("  INGESTION COMPLETE")
    print("=" * 64)
    print()
    print(f"  Files processed : {total_files}")
    print(f"  Total chunks    : {total_chunks}")
    print(f"  Vectors stored  : {total_chunks}")
    print(f"  Collection      : {COLLECTION_NAME}")
    print(f"  Errors          : {len(errors)}")

    if errors:
        print()
        print("  Failed files:")
        for fname, err in errors:
            print(f"    {fname}: {err}")

    # Test queries
    print()
    print("  Running test queries...")
    test_queries = [
        "Who is Cian mac Morna?",
        "What is Methuselah's Sword?",
        "Who are the Two Witnesses of Revelation 11?"
    ]

    for query in test_queries:
        print()
        print(f"  QUERY: '{query}'")
        vec = get_embedding(query)
        result = qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points/search", {
            "vector": vec, "limit": 2, "with_payload": True
        })
        for r in result.get("result", []):
            score = r["score"]
            src   = r["payload"]["source_file"]
            text  = r["payload"]["text"][:100].replace("\n", " ")
            print(f"    [{score:.3f}] {src}")
            print(f"           {text}...")

    print()
    print("  Canon search is LIVE. DESKTOP-SINGULA knows the Chronicles.")
    print()


if __name__ == "__main__":
    main()
