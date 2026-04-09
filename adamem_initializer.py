"""
DESKTOP-SINGULA — AdaMem Initializer
=====================================
Decomposes the flat 'nephilim_chronicles' Qdrant collection into the four-tier
AdaMem architecture required for the v2.0 Creative Swarm (Books 3–5).

Tier Map:
    tnc_episodes  — Episodic Memory: chapter summaries, scene records
    tnc_personas  — Persona Memory: character dossiers, trait states
    tnc_role_graph — Graph Memory (Role): entity-relation-entity triples
    tnc_plot_graph — Graph Memory (Plot): causal event chains

The original 'nephilim_chronicles' collection is NOT deleted.
Run with --dry-run first to preview classification results.

Usage:
    python adamem_initializer.py [--dry-run] [--verbose]
"""

import sys
import json
import time
import argparse
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

QDRANT_URL      = "http://localhost:6333"
OLLAMA_URL      = "http://localhost:11434"
EMBED_MODEL     = "nomic-embed-text"
SOURCE_COLL     = "nephilim_chronicles"
VECTOR_SIZE     = 768   # nomic-embed-text output dimension

TIER_COLLECTIONS = {
    "tnc_episodes":   "Episodic Memory — chapter summaries & scene records",
    "tnc_personas":   "Persona Memory  — character dossiers & arc states",
    "tnc_role_graph": "Graph Memory    — entity-relation-entity triples",
    "tnc_plot_graph": "Graph Memory    — causal event chains",
}

# Classification rules — checked in order; first match wins
# Each rule: (tier, condition_fn)
CLASSIFICATION_RULES = [
    # ── Episodic ──────────────────────────────────────────────
    ("tnc_episodes", lambda p: p.get("category") in ("chapter_summary", "manuscript")),
    ("tnc_episodes", lambda p: p.get("entity_type") in ("chapter", "scene", "episode")),
    ("tnc_episodes", lambda p: "chapter" in str(p.get("source_file", "")).lower()
                               and p.get("category") not in ("canon", "dossier")),

    # ── Personas ──────────────────────────────────────────────
    ("tnc_personas", lambda p: p.get("category") in ("dossier", "character_dossier")),
    ("tnc_personas", lambda p: p.get("entity_type") in
                               ("character", "watcher", "nephilim", "archangel", "human")),
    ("tnc_personas", lambda p: any(k in str(p.get("source_file", "")).upper()
                                   for k in ("DOSSIER", "PROTAGONIST", "ANTAGONIST",
                                             "WATCHER_D", "NEPHILIM_D"))),

    # ── Role Graph ────────────────────────────────────────────
    ("tnc_role_graph", lambda p: p.get("category") == "canon_fact"),
    ("tnc_role_graph", lambda p: p.get("entity_type") in ("triple", "relation", "canon_triple")),
    ("tnc_role_graph", lambda p: all(k in p for k in ("subject", "predicate", "object"))),

    # ── Plot Graph ────────────────────────────────────────────
    ("tnc_plot_graph", lambda p: p.get("category") == "plot_event"),
    ("tnc_plot_graph", lambda p: p.get("entity_type") in ("event", "plot_node", "causal_event")),
]

BATCH_SIZE = 100   # Qdrant scroll batch size


# ── Qdrant Helpers ────────────────────────────────────────────────────────────

def qdrant_get(path):
    r = requests.get(f"{QDRANT_URL}{path}", timeout=30)
    r.raise_for_status()
    return r.json()


def qdrant_post(path, body):
    r = requests.post(f"{QDRANT_URL}{path}", json=body, timeout=60)
    r.raise_for_status()
    return r.json()


def qdrant_put(path, body):
    r = requests.put(f"{QDRANT_URL}{path}", json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def collection_exists(name):
    try:
        qdrant_get(f"/collections/{name}")
        return True
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return False
        raise


def create_collection(name):
    body = {
        "vectors": {
            "size": VECTOR_SIZE,
            "distance": "Cosine"
        },
        "optimizers_config": {
            "memmap_threshold": 20000
        },
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100
        }
    }
    qdrant_put(f"/collections/{name}", body)
    print(f"  ✓ Created collection: {name}")


def scroll_all_points(collection):
    """Generator: yields all points from a collection via scroll pagination."""
    offset = None
    while True:
        body = {
            "limit": BATCH_SIZE,
            "with_payload": True,
            "with_vectors": True,
        }
        if offset is not None:
            body["offset"] = offset

        result = qdrant_post(f"/collections/{collection}/points/scroll", body)
        points = result.get("result", {}).get("points", [])
        if not points:
            break

        yield from points

        next_offset = result.get("result", {}).get("next_page_offset")
        if next_offset is None:
            break
        offset = next_offset


def upsert_points(collection, points):
    """Upsert a batch of points into a collection."""
    body = {
        "points": [
            {
                "id": p["id"],
                "vector": p["vector"],
                "payload": p.get("payload", {})
            }
            for p in points
            if p.get("vector") is not None
        ]
    }
    if not body["points"]:
        return  # nothing to upsert
    qdrant_put(f"/collections/{collection}/points", body)


# ── Classification ─────────────────────────────────────────────────────────────

def classify_point(point):
    """
    Returns the target tier collection for a point, or None (keep in source).
    """
    payload = point.get("payload", {})
    for tier, condition in CLASSIFICATION_RULES:
        try:
            if condition(payload):
                return tier
        except Exception:
            continue
    return None  # remains in nephilim_chronicles (raw text fallback)


# ── Main Migration ─────────────────────────────────────────────────────────────

def run_migration(dry_run=False, verbose=False):
    print("\n" + "═" * 64)
    print("  ADAMEM INITIALIZER — The Nephilim Chronicles v2.0")
    print(f"  Mode: {'DRY RUN — no writes' if dry_run else 'LIVE MIGRATION'}")
    print(f"  Source collection: {SOURCE_COLL}")
    print("═" * 64)

    # 1. Verify source collection exists
    try:
        info = qdrant_get(f"/collections/{SOURCE_COLL}")
        total_points = info["result"]["points_count"]
        print(f"\n  Source: {SOURCE_COLL} — {total_points:,} points")
    except Exception as e:
        print(f"\n  ERROR: Could not reach Qdrant or collection '{SOURCE_COLL}': {e}")
        sys.exit(1)

    # 2. Create tier collections (skip if exist)
    print("\n  ── Tier Collections ──────────────────────────────────────")
    if not dry_run:
        for name, desc in TIER_COLLECTIONS.items():
            if collection_exists(name):
                print(f"  · {name} already exists — skipping create")
            else:
                create_collection(name)

    # 3. Scroll and classify all points
    print(f"\n  ── Classifying {total_points:,} points ──────────────────────")
    counts = {name: 0 for name in TIER_COLLECTIONS}
    counts["unclassified"] = 0

    tier_buffers = {name: [] for name in TIER_COLLECTIONS}
    processed = 0

    for point in scroll_all_points(SOURCE_COLL):
        processed += 1
        tier = classify_point(point)

        if tier:
            counts[tier] += 1
            if verbose:
                src = point.get("payload", {}).get("source_file", "?")
                print(f"    [{tier:20s}] {src}")
            if not dry_run:
                tier_buffers[tier].append(point)
                if len(tier_buffers[tier]) >= BATCH_SIZE:
                    upsert_points(tier, tier_buffers[tier])
                    tier_buffers[tier] = []
        else:
            counts["unclassified"] += 1
            if verbose:
                src = point.get("payload", {}).get("source_file", "?")
                print(f"    [{'unclassified':20s}] {src}")

        if processed % 500 == 0:
            print(f"    … {processed:,} / {total_points:,} processed")

    # 4. Flush remaining buffers
    if not dry_run:
        for tier, buf in tier_buffers.items():
            if buf:
                upsert_points(tier, buf)

    # 5. Report
    print("\n  ── Migration Report ──────────────────────────────────────")
    for name, count in counts.items():
        bar = "█" * min(40, count // max(1, total_points // 40))
        print(f"  {name:20s}  {count:6,}  {bar}")

    migrated_total = sum(v for k, v in counts.items() if k != "unclassified")
    pct_migrated = (migrated_total / total_points * 100) if total_points else 0
    print(f"\n  Total points processed : {processed:,}")
    print(f"  Migrated to tiers      : {migrated_total:,}  ({pct_migrated:.1f}%)")
    print(f"  Remaining in source    : {counts['unclassified']:,}")

    if dry_run:
        print("\n  DRY RUN COMPLETE — Re-run without --dry-run to apply.")
    else:
        print("\n  MIGRATION COMPLETE.")
        print(f"  Original '{SOURCE_COLL}' collection preserved (raw text fallback).")
        print("  Author confirmation required before deleting source collection.")

    # 6. Write report to file
    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": "dry_run" if dry_run else "live",
        "source_collection": SOURCE_COLL,
        "total_source_points": total_points,
        "processed": processed,
        "tier_counts": counts,
        "migrated_total": migrated_total,
        "migration_pct": round(pct_migrated, 2),
    }
    report_path = "adamem_migration_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved: {report_path}")
    print("═" * 64 + "\n")


# ── Seed Role Graph with Locked Canon Triples ─────────────────────────────────

LOCKED_TRIPLES = [
    # ── Core Identity ─────────────────────────────────────────
    ("CIAN_MAC_MORNA",   "IS_WIELDER_OF",          "MO_CHRA"),
    ("CIAN_MAC_MORNA",   "IS",                     "GUARDIAN"),
    ("CIAN_MAC_MORNA",   "GUARDIAN_OF",            "ENOCH"),
    ("CIAN_MAC_MORNA",   "GUARDIAN_OF",            "ELIJAH"),
    ("CIAN_MAC_MORNA",   "COMMISSIONED_IN",        "586_BCE"),
    ("MO_CHRA",          "MADE_BY",                "ENOCH"),
    ("MO_CHRA",          "INTERFACES_WITH",        "EMPYREAL_REGISTER"),
    ("MO_CHRA",          "PRODUCES",               "CREATION_FREQUENCIES"),
    # ── Watcher/Nephilim Ontology ──────────────────────────────
    ("RAPHAEL",          "ALIAS_IS",               "LIAIGH"),     # LOCKED — Book 5 reveal
    ("RAPHAEL",          "CANNOT_KILL",            "FALLEN_WATCHERS"),
    ("RAPHAEL",          "CANNOT_ENTER",           "CYDONIA_1"),
    ("RAPHAEL",          "CANNOT_VIOLATE",         "HUMAN_FREE_WILL"),
    ("SHEMYAZA",         "LED",                     "200_WATCHERS"),
    ("SHEMYAZA",         "DESCENDED_AT",           "MOUNT_HERMON"),
    ("WATCHERS",         "LOST",                   "INNATE_SUPERNATURAL_GIFTS"),
    ("WATCHERS",         "RETAINED",               "KNOWLEDGE_OF_ABILITIES"),
    ("AZAZEL",           "IS",                     "NEPHILIM"),        # NOT a Watcher
    ("AZAZEL",           "IS_SON_OF",              "GADREEL"),
    ("AZAZEL",           "IS",                     "FALSE_PROPHET"),
    ("AZAZEL",           "IMPRISONED_IN",          "DUDAEL"),
    ("OHYA",             "IS",                     "THE_BEAST"),
    ("OHYA",             "IS_SON_OF",              "SHEMYAZA"),
    ("OHYA",             "IS_SON_OF",              "NAAMAH"),
    ("NAAMAH",           "IS",                     "WHORE_OF_BABYLON"),
    ("NAAMAH",           "SURVIVED_FLOOD_AS",      "SIREN"),
    # ── Witnesses ─────────────────────────────────────────────
    ("ENOCH",            "IS",                     "FIRST_WITNESS"),
    ("ENOCH",            "IS",                     "HEAVENS_RECORD_KEEPER"),
    ("ELIJAH",           "IS",                     "SECOND_WITNESS"),
    ("ENOCH",            "PROPHESIES_FOR",         "1260_DAYS"),
    ("ELIJAH",           "PROPHESIES_FOR",         "1260_DAYS"),
    # ── Knowledge Transmission Chain ──────────────────────────
    ("WATCHERS",         "TAUGHT",                 "NEPHILIM"),
    ("NEPHILIM",         "BECAME",                 "APKALLU"),
    ("APKALLU",          "TAUGHT",                 "SUMERIANS"),
    ("SUMERIANS",        "TRANSMITTED_VIA",        "MYSTERY_BABYLON"),
    ("MYSTERY_BABYLON",  "MANIFESTS_AS",           "WEF_CLUB_OF_ROME"),
    # ── Acoustic Paradigm ─────────────────────────────────────
    ("SUPERNATURAL_TECHNOLOGY", "OPERATES_THROUGH", "SOUND_VIBRATION"),
    ("CYDONIAN_ORE",     "CONTAINS",               "ACOUSTIC_MEMORY"),
    # ── Theological Constants ─────────────────────────────────
    ("JESUS_CHRIST",     "IS",                     "SON_OF_GOD"),
    ("JESUS_CHRIST",     "IS",                     "FULLY_DIVINE"),
    ("JESUS_CHRIST",     "IS",                     "FULLY_HUMAN"),
    ("SALVATION",        "IS_THROUGH",             "CHRIST_ALONE"),
    ("SATAN",            "IS",                     "THE_DRAGON"),
    ("SATAN",            "IS",                     "DEFEATED_AT_CALVARY"),
]


def embed_text(text):
    """Embed a text string using Ollama nomic-embed-text."""
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["embedding"]


def seed_role_graph(dry_run=False):
    """Seed tnc_role_graph with locked canon triples."""
    print("\n  ── Seeding Role Graph (Locked Canon Triples) ────────────")
    print(f"  Triples to seed: {len(LOCKED_TRIPLES)}")

    if dry_run:
        for s, p, o in LOCKED_TRIPLES:
            print(f"    ({s}, {p}, {o})")
        print("  DRY RUN — no embeddings generated.")
        return

    batch = []
    for i, (subject, predicate, obj) in enumerate(LOCKED_TRIPLES):
        triple_text = f"{subject} {predicate} {obj}"
        print(f"  [{i+1:2d}/{len(LOCKED_TRIPLES)}] Embedding: {triple_text}")
        vec = embed_text(triple_text)

        # Use deterministic ID: hash of subject+predicate+object
        import hashlib
        triple_hash = hashlib.sha256(triple_text.encode()).hexdigest()
        # Qdrant requires integer or UUID IDs; use first 8 hex chars as unsigned int
        point_id_int = int(triple_hash[:8], 16)

        batch.append({
            "id": point_id_int,
            "vector": vec,
            "payload": {
                "subject":     subject,
                "predicate":   predicate,
                "object":      obj,
                "triple_text": triple_text,
                "confidence":  "LOCKED",
                "source":      "CANON/SERIES_BIBLE.md",
                "book_scope":  ["1", "2", "3", "4", "5"],
                "added_by":    "adamem_initializer",
                "timestamp":   datetime.now().isoformat(),
                "entity_type": "triple",
                "category":    "canon_fact",
            }
        })

        # Upsert in batches of 10 (embeddings are slow)
        if len(batch) >= 10:
            upsert_points("tnc_role_graph", batch)
            batch = []
        time.sleep(0.1)  # be gentle on Ollama

    if batch:
        upsert_points("tnc_role_graph", batch)

    print(f"  ✓ {len(LOCKED_TRIPLES)} locked canon triples seeded into tnc_role_graph")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AdaMem Initializer — decomposes Qdrant flat collection into 4-tier AdaMem"
    )
    parser.add_argument("--dry-run",  action="store_true",
                        help="Preview classification without writing to Qdrant")
    parser.add_argument("--verbose",  action="store_true",
                        help="Print per-point classification decisions")
    parser.add_argument("--seed-only", action="store_true",
                        help="Skip migration; only seed Role Graph with locked triples")
    parser.add_argument("--migrate-only", action="store_true",
                        help="Skip seeding; only migrate existing collection")
    args = parser.parse_args()

    if not args.seed_only:
        run_migration(dry_run=args.dry_run, verbose=args.verbose)

    if not args.migrate_only:
        seed_role_graph(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
