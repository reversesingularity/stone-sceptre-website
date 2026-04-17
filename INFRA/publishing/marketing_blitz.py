"""
MARKETING BLITZ — Kerman Gild Publishing
=========================================
Fires Agent 9 (port 8772) against all published books to generate
a complete marketing asset library:

  1. SEO metadata  — Amazon KDP keywords, BISAC, A/B titles, HTML descriptions
  2. Social packs  — TikTok scripts, LinkedIn posts, Twitter threads, YouTube community
  3. YouTube briefs — Long-form anchor video scripts per chapter
  4. Serialization  — DTC exclusivity schedules & revenue projections
  5. NZ Grants      — Trigger the grant scrape cycle

Assets saved to MARKETING/<book_slug>/<asset_type>/*.json

Usage:
    python marketing_blitz.py                     # full blitz — all books, all assets
    python marketing_blitz.py --books 1           # Book 1 only
    python marketing_blitz.py --books 1 2         # Books 1 and 2
    python marketing_blitz.py --assets seo social # SEO + social only
    python marketing_blitz.py --dry-run           # show plan without calling Agent 9
    python marketing_blitz.py --grants-only       # just NZ grant scrape
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles")
MANUSCRIPT   = PROJECT_ROOT / "MANUSCRIPT"
MARKETING    = PROJECT_ROOT / "MARKETING"
AGENT_9_URL  = "http://localhost:8772"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BLITZ] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("marketing_blitz")

# ── Book Catalog ──────────────────────────────────────────────────────────────

BOOK_CATALOG = {
    # ── Nephilim Chronicles ──
    "nc_book_1": {
        "title":       "The Cydonian Oaths",
        "series":      "The Nephilim Chronicles",
        "series_tag":  "nephilim_chronicles",
        "book_num":    1,
        "slug":        "nc_book_1_cydonian_oaths",
        "word_count":  165000,
        "description": (
            "After twenty-six centuries of silence, an immortal Celtic guardian's "
            "ancient sword finally speaks as the Two Witnesses of Revelation return. "
            "Cian mac Morna — warrior, outcast, last of the Fianna — is drawn into a "
            "war that spans from the Antarctic ice to a Martian pyramid, where the "
            "fallen Watchers of Genesis 6 planted the seeds of humanity's extinction. "
            "Tom Clancy meets Frank Peretti in this apocalyptic thriller grounded in "
            "the Book of Enoch, Celtic legend, and Revelation prophecy."
        ),
        "chapter_dir": MANUSCRIPT / "book_1",
        "chapter_glob": "CHAPTER_*.md",
        "extra_files": ["BOOK_1_PROLOGUE.md", "EPILOGUE_THE_DIGGING_BEGINS.md"],
    },
    "nc_book_2": {
        "title":       "The Cauldron of God",
        "series":      "The Nephilim Chronicles",
        "series_tag":  "nephilim_chronicles",
        "book_num":    2,
        "slug":        "nc_book_2_cauldron_of_god",
        "word_count":  130000,
        "description": (
            "Cian mac Morna descends into a two-kilometre-deep Antarctic prison to "
            "stop the release of the antediluvian weapon-smith Azazel — son of the "
            "fallen Watcher Gadreel. As the Titan fleet reaches Mars and Cydonia-1 "
            "awakens, the twenty names spoken at Mount Hermon echo again. The Cauldron "
            "of God is the vessel of judgment, and its hour has come. Book Two of "
            "The Nephilim Chronicles — where military thriller meets cosmic horror."
        ),
        "chapter_dir": MANUSCRIPT / "book_2" / "CHAPTERS",
        "chapter_glob": "CHAPTER_*.md",
        "extra_files": [
            "PROLOGUE_SCENE1_TheFountainsOfTheDeep.md",
            "PROLOGUE_SCENE2_TheTowerAndTheThrone.md",
            "EPILOGUE_TheWitnessesInEden.md",
        ],
    },
    # ── Stone & Sceptre Chronicles ──
    "ss_book_1": {
        "title":       "The Stone and the Sceptre",
        "series":      "The Stone & Sceptre Chronicles",
        "series_tag":  "stone_sceptre",
        "book_num":    1,
        "slug":        "ss_book_1_stone_sceptre",
        "word_count":  150000,
        "description": (
            "The prophet Jeremiah flees a burning Jerusalem with the Stone of Destiny "
            "and the last Davidic princess to lands beyond the world's pillars. A "
            "sweeping historical epic tracing the migration of Israel's lost tribes "
            "from the ashes of Solomon's Temple to the emerald shores of the Celtic "
            "West. Faith, covenant, and divine providence collide in the ancient world."
        ),
        "chapter_dir": None,  # manuscript not in this workspace
        "chapter_glob": None,
        "extra_files": [],
    },
    "ss_book_2": {
        "title":       "The Red Hand & The Eternal Throne",
        "series":      "The Stone & Sceptre Chronicles",
        "series_tag":  "stone_sceptre",
        "book_num":    2,
        "slug":        "ss_book_2_red_hand",
        "word_count":  160000,
        "description": (
            "Hebrew refugees and Celtic warriors unite in Iberia to face the "
            "supernatural hordes of the giant-king Balor. The Davidic throne "
            "continues its journey westward as ancient covenants clash with dark "
            "powers. Book Two of The Stone & Sceptre Chronicles — where biblical "
            "archaeology meets Celtic myth in a war for civilization's soul."
        ),
        "chapter_dir": None,  # manuscript not in this workspace
        "chapter_glob": None,
        "extra_files": [],
    },
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_chapter_text(chapter_path: Path, max_chars: int = 4000) -> str:
    """Read chapter markdown, strip YAML front-matter, return first max_chars."""
    text = chapter_path.read_text(encoding="utf-8")
    # Strip YAML front-matter if present
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]
    return text.strip()[:max_chars]


def get_chapter_files(book: dict) -> list[tuple[int, Path]]:
    """Return sorted list of (chapter_number, path) for a book."""
    if not book["chapter_dir"] or not book["chapter_dir"].exists():
        return []

    chapters = []
    # Main chapter files
    if book["chapter_glob"]:
        for f in sorted(book["chapter_dir"].glob(book["chapter_glob"])):
            # Extract chapter number from filename
            name = f.stem
            for part in name.split("_"):
                if part.isdigit():
                    chapters.append((int(part), f))
                    break
            else:
                chapters.append((0, f))

    # Extra files (prologues, epilogues)
    for extra in book.get("extra_files", []):
        p = book["chapter_dir"] / extra
        if p.exists():
            if "PROLOGUE" in extra.upper():
                chapters.insert(0, (0, p))
            else:
                chapters.append((999, p))

    return chapters


def post_agent9(endpoint: str, payload: dict, timeout: int = 300) -> dict:
    """POST to Agent 9 and return JSON response."""
    url = f"{AGENT_9_URL}{endpoint}"
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def save_asset(book_slug: str, asset_type: str, filename: str, data: dict):
    """Save a marketing asset as JSON."""
    out_dir = MARKETING / book_slug / asset_type
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info(f"  Saved: {out_path.relative_to(PROJECT_ROOT)}")


# ── Asset Generators ──────────────────────────────────────────────────────────

def generate_seo(book_key: str, book: dict, dry_run: bool = False):
    """Generate SEO metadata for a book."""
    log.info(f"[SEO] {book['title']}")
    if dry_run:
        log.info("  (dry-run) Would generate SEO metadata")
        return

    result = post_agent9("/seo-metadata", {
        "book_title":  book["title"],
        "description": book["description"],
        "genre":       "Christian Apocalyptic Fiction" if "nephilim" in book["series_tag"]
                       else "Biblical Historical Fiction",
    })
    save_asset(book["slug"], "seo", "seo_metadata.json", result)


def generate_social(book_key: str, book: dict, dry_run: bool = False,
                    max_chapters: int = 4):
    """Generate social media content for key chapters."""
    chapters = get_chapter_files(book)
    if not chapters:
        log.info(f"[SOCIAL] {book['title']} — no chapter files available, skipping")
        return

    # Pick chapters: prologue, first, middle, climax
    picks = _pick_representative_chapters(chapters, max_chapters)

    for ch_num, ch_path in picks:
        label = ch_path.stem
        log.info(f"[SOCIAL] {book['title']} — {label}")
        if dry_run:
            log.info("  (dry-run) Would generate social content")
            continue

        text = load_chapter_text(ch_path)
        result = post_agent9("/generate-social", {
            "chapter_text":  text,
            "book":          book["book_num"],
            "chapter":       ch_num,
            "series_title":  book["series"],
        })
        save_asset(
            book["slug"], "social",
            f"social_ch{ch_num:02d}_{label}.json",
            result,
        )
        time.sleep(2)  # breathe between LLM calls


def generate_youtube(book_key: str, book: dict, dry_run: bool = False,
                     max_chapters: int = 4):
    """Generate YouTube anchor briefs for key chapters."""
    chapters = get_chapter_files(book)
    if not chapters:
        log.info(f"[YOUTUBE] {book['title']} — no chapter files available, skipping")
        return

    picks = _pick_representative_chapters(chapters, max_chapters)

    for ch_num, ch_path in picks:
        label = ch_path.stem
        log.info(f"[YOUTUBE] {book['title']} — {label}")
        if dry_run:
            log.info("  (dry-run) Would generate YouTube brief")
            continue

        text = load_chapter_text(ch_path)
        result = post_agent9("/youtube-anchor", {
            "chapter_text":  text,
            "book":          book["book_num"],
            "chapter":       ch_num,
        })
        save_asset(
            book["slug"], "youtube",
            f"youtube_ch{ch_num:02d}_{label}.json",
            result,
        )
        time.sleep(2)


def generate_serialization(book_key: str, book: dict, dry_run: bool = False):
    """Generate serialization schedule for a book."""
    chapters = get_chapter_files(book)
    total = len(chapters) if chapters else 17  # estimate if no files

    log.info(f"[SERIAL] {book['title']} ({total} chapters)")
    if dry_run:
        log.info("  (dry-run) Would generate serialization schedule")
        return

    result = post_agent9("/serialization-schedule", {
        "book":                   book["book_num"],
        "total_chapters":         total,
        "dtc_exclusivity_days":   14,
    })
    save_asset(book["slug"], "serialization", "serialization_schedule.json", result)


def run_nz_grants(dry_run: bool = False):
    """Trigger the NZ grant scrape cycle."""
    log.info("[GRANTS] NZ literary grant scrape")
    if dry_run:
        log.info("  (dry-run) Would trigger NZ grant scrape")
        return

    result = post_agent9("/scrape-nz-grants", {})
    # Save to MARKETING root
    out_dir = MARKETING / "_grants"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"nz_grants_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info(f"  Saved: {out_path.relative_to(PROJECT_ROOT)}")


def _pick_representative_chapters(
    chapters: list[tuple[int, Path]], max_picks: int
) -> list[tuple[int, Path]]:
    """Pick representative chapters: prologue/first, early-mid, mid, climax."""
    if len(chapters) <= max_picks:
        return chapters

    n = len(chapters)
    indices = [0]  # first (prologue or ch1)

    if max_picks >= 4:
        indices.append(n // 4)       # early act
        indices.append(n // 2)       # midpoint
        indices.append(n - 2)        # climax (penultimate)
    elif max_picks >= 3:
        indices.append(n // 2)
        indices.append(n - 2)
    elif max_picks >= 2:
        indices.append(n - 2)

    # Deduplicate while preserving order
    seen = set()
    picks = []
    for i in indices:
        if i not in seen and i < n:
            seen.add(i)
            picks.append(chapters[i])

    return picks[:max_picks]


# ── Dashboard ─────────────────────────────────────────────────────────────────

def print_dashboard():
    """Print a summary of all generated marketing assets."""
    if not MARKETING.exists():
        log.info("No MARKETING/ directory yet.")
        return

    log.info("")
    log.info("=" * 70)
    log.info("  MARKETING BLITZ — ASSET DASHBOARD")
    log.info("=" * 70)

    total_files = 0
    for book_dir in sorted(MARKETING.iterdir()):
        if not book_dir.is_dir():
            continue
        log.info(f"\n  {book_dir.name}/")
        for asset_dir in sorted(book_dir.iterdir()):
            if not asset_dir.is_dir():
                continue
            files = list(asset_dir.glob("*.json"))
            total_files += len(files)
            log.info(f"    {asset_dir.name}/  ({len(files)} assets)")
            for f in sorted(files):
                size_kb = f.stat().st_size / 1024
                log.info(f"      {f.name}  ({size_kb:.1f} KB)")

    log.info(f"\n  TOTAL: {total_files} marketing assets generated")
    log.info("=" * 70)


# ── Main ──────────────────────────────────────────────────────────────────────

ASSET_TYPES = ["seo", "social", "youtube", "serialization"]

ASSET_RUNNERS = {
    "seo":            generate_seo,
    "social":         generate_social,
    "youtube":        generate_youtube,
    "serialization":  generate_serialization,
}


def main():
    parser = argparse.ArgumentParser(
        description="Marketing Blitz — fire Agent 9 against all published books"
    )
    parser.add_argument(
        "--books", nargs="+", type=int, default=None,
        help="Book numbers to target (e.g., --books 1 2). Default: all."
    )
    parser.add_argument(
        "--series", choices=["nc", "ss", "all"], default="all",
        help="Series filter: nc=Nephilim, ss=Stone&Sceptre, all=both. Default: all."
    )
    parser.add_argument(
        "--assets", nargs="+", choices=ASSET_TYPES, default=None,
        help="Asset types to generate. Default: all."
    )
    parser.add_argument(
        "--max-chapters", type=int, default=4,
        help="Max chapters per book for social/youtube (default: 4)."
    )
    parser.add_argument(
        "--grants-only", action="store_true",
        help="Only run NZ grant scrape."
    )
    parser.add_argument(
        "--no-grants", action="store_true",
        help="Skip NZ grant scrape."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show plan without calling Agent 9."
    )
    args = parser.parse_args()

    log.info("=" * 70)
    log.info("  KERMAN GILD PUBLISHING — MARKETING BLITZ")
    log.info(f"  Agent 9: {AGENT_9_URL}")
    log.info(f"  Output:  {MARKETING}")
    log.info(f"  Time:    {datetime.now().isoformat()}")
    if args.dry_run:
        log.info("  MODE:    DRY RUN (no API calls)")
    log.info("=" * 70)

    # Health check
    if not args.dry_run:
        try:
            r = requests.get(f"{AGENT_9_URL}/health", timeout=5)
            health = r.json()
            if health.get("status") != "ok":
                log.error(f"Agent 9 health check failed: {health}")
                sys.exit(1)
            log.info("Agent 9 health: OK")
        except Exception as e:
            log.error(f"Cannot reach Agent 9 at {AGENT_9_URL}: {e}")
            log.error("Start the swarm first: .\\Start-TNCSwarm.ps1")
            sys.exit(1)

    # Grants-only mode
    if args.grants_only:
        run_nz_grants(dry_run=args.dry_run)
        print_dashboard()
        return

    # Filter books
    target_books = {}
    for key, book in BOOK_CATALOG.items():
        # Series filter
        if args.series != "all":
            if args.series == "nc" and "nephilim" not in book["series_tag"]:
                continue
            if args.series == "ss" and "stone" not in book["series_tag"]:
                continue
        # Book number filter
        if args.books and book["book_num"] not in args.books:
            continue
        target_books[key] = book

    if not target_books:
        log.error("No books matched the filter criteria.")
        sys.exit(1)

    assets = args.assets or ASSET_TYPES
    log.info(f"Targeting {len(target_books)} books: "
             f"{', '.join(b['title'] for b in target_books.values())}")
    log.info(f"Assets: {', '.join(assets)}")
    log.info("")

    # Execute
    start = time.time()
    errors = []

    for book_key, book in target_books.items():
        log.info(f"{'─' * 50}")
        log.info(f"  {book['series']} — {book['title']}")
        log.info(f"{'─' * 50}")

        for asset_type in assets:
            runner = ASSET_RUNNERS[asset_type]
            try:
                if asset_type in ("social", "youtube"):
                    runner(book_key, book, dry_run=args.dry_run,
                           max_chapters=args.max_chapters)
                else:
                    runner(book_key, book, dry_run=args.dry_run)
            except requests.exceptions.ConnectionError:
                msg = f"{book['title']} / {asset_type}: Agent 9 connection refused"
                log.error(msg)
                errors.append(msg)
            except requests.exceptions.Timeout:
                msg = f"{book['title']} / {asset_type}: Agent 9 timed out (300s)"
                log.error(msg)
                errors.append(msg)
            except Exception as e:
                msg = f"{book['title']} / {asset_type}: {e}"
                log.error(msg)
                errors.append(msg)

    # NZ Grants (unless skipped)
    if not args.no_grants:
        try:
            run_nz_grants(dry_run=args.dry_run)
        except Exception as e:
            errors.append(f"NZ Grants: {e}")

    elapsed = time.time() - start
    log.info("")
    log.info(f"Blitz completed in {elapsed:.0f}s")

    if errors:
        log.warning(f"{len(errors)} error(s):")
        for err in errors:
            log.warning(f"  - {err}")

    print_dashboard()


if __name__ == "__main__":
    main()
