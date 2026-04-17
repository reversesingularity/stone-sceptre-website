"""
Targeted ingestion: Miriam_Ashford_Character_Canon_02Mar2026.docx
Tags all vectors with source: character_dossier, character: miriam_ashford
Upserts into existing nephilim_chronicles Qdrant collection.
"""

import hashlib
import requests
from docx import Document

DOCX_PATH       = r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\CANON\dossiers\Miriam_Ashford_Character_Canon_02Mar2026.docx"
OLLAMA_URL      = "http://localhost:11434"
QDRANT_URL      = "http://localhost:6333"
EMBED_MODEL     = "nomic-embed-text"
COLLECTION_NAME = "nephilim_chronicles"
CHUNK_SIZE      = 800
CHUNK_OVERLAP   = 150


def extract_docx_text(path):
    doc = Document(path)
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + size]
        if chunk.strip():
            chunks.append(chunk)
        start += size - overlap
    return chunks


def get_embedding(text):
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def qdrant_post(path, data):
    r = requests.post(f"{QDRANT_URL}{path}", json=data, timeout=60)
    r.raise_for_status()
    return r.json()


def qdrant_put(path, data):
    r = requests.put(f"{QDRANT_URL}{path}", json=data, timeout=120)
    r.raise_for_status()
    return r.json()


def get_next_point_id():
    """Fetch current point count to use as starting ID offset."""
    r = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}", timeout=10)
    r.raise_for_status()
    return r.json()["result"]["points_count"] + 1


def main():
    print()
    print("=" * 60)
    print("  MIRIAM ASHFORD DOSSIER — TARGETED QDRANT INGESTION")
    print("=" * 60)
    print()

    print(f"  Source : {DOCX_PATH}")
    print(f"  Tags   : source=character_dossier, character=miriam_ashford")
    print()

    text = extract_docx_text(DOCX_PATH)
    if not text.strip():
        print("  ERROR: No text extracted from DOCX. Aborting.")
        return

    print(f"  Extracted: {len(text):,} characters")

    chunks = chunk_text(text)
    print(f"  Chunks   : {len(chunks)}")
    print()

    file_hash  = hashlib.md5(text.encode()).hexdigest()[:8]
    start_id   = get_next_point_id()
    points     = []

    for j, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        points.append({
            "id":     start_id + j,
            "vector": embedding,
            "payload": {
                "source_file":  "CANON/dossiers/Miriam_Ashford_Character_Canon_02Mar2026.docx",
                "source_root":  "chronicles_root",
                "filename":     "Miriam_Ashford_Character_Canon_02Mar2026.docx",
                "category":     "dossier",
                "source":       "character_dossier",
                "character":    "miriam_ashford",
                "chunk_index":  j,
                "total_chunks": len(chunks),
                "text":         chunk,
                "file_hash":    file_hash,
            },
        })
        print(f"\r  Embedding chunk {j+1}/{len(chunks)}...", end="", flush=True)

    print()
    print("  Upserting to Qdrant...")
    qdrant_put(f"/collections/{COLLECTION_NAME}/points?wait=true", {"points": points})

    print()
    print(f"  ✓ {len(points)} vectors upserted (IDs {start_id}–{start_id + len(points) - 1})")
    print()

    # Spot-check query
    print("  Spot-check: 'Miriam Ashford denial architecture'")
    vec = get_embedding("Miriam Ashford denial architecture feelings for Cian")
    result = qdrant_post(
        f"/collections/{COLLECTION_NAME}/points/search",
        {"vector": vec, "limit": 3, "with_payload": True,
         "filter": {"must": [{"key": "character", "match": {"value": "miriam_ashford"}}]}},
    )
    for hit in result.get("result", []):
        score = hit["score"]
        text_preview = hit["payload"]["text"][:120].replace("\n", " ")
        print(f"    [{score:.3f}] {text_preview}...")

    print()
    print("  DONE — Miriam Ashford dossier is live in Qdrant.")
    print()


if __name__ == "__main__":
    main()
