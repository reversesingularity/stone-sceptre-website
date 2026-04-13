"""
Autonomous Scheduler — Agent 13 works 24/6 and rests on the Sabbath.

Sabbath window: Friday sundown → Saturday sundown (local time).
Sundown is approximated at 18:00 local unless overridden.

Task cycle (runs every CYCLE_INTERVAL_MINUTES):
  1. Content generation — pick a random un-covered chapter, generate + queue
  2. Trend scraping — monitor RSS feeds & competitor pages
  3. SEO keyword suggestions — periodic discovery for long-tail terms
  4. Queue processing — attempt to post queued items whose scheduled_at has passed
  5. Campaign health — log status snapshots into memory

Each task has its own cadence so heavier tasks (content gen) run less frequently
than lighter ones (queue processing).
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

try:
    from . import memory_store, campaign_planner, seo_optimizer, social_media, scraper, poster
except ImportError:
    import memory_store
    import campaign_planner
    import seo_optimizer
    import social_media
    import scraper
    import poster

log = logging.getLogger("agent13.scheduler")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CYCLE_INTERVAL_MINUTES = 15        # Main loop wakes every 15 min
CONTENT_GEN_INTERVAL_HOURS = 4     # New content every 4 hours
TREND_SCRAPE_INTERVAL_HOURS = 6    # Trend scan every 6 hours
SEO_SUGGEST_INTERVAL_HOURS = 12    # Keyword discovery every 12 hours
QUEUE_PROCESS_INTERVAL_MINUTES = 30  # Check post queue every 30 min
CAMPAIGN_LOG_INTERVAL_HOURS = 8    # Campaign health snapshot every 8 hours

SABBATH_SUNDOWN_HOUR = 18          # 6 PM local — approximate sundown
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"

# Book 1 chapters available for content generation
MANUSCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "MANUSCRIPT" / "book_1"
CHAPTER_FILES = sorted(MANUSCRIPT_DIR.glob("CHAPTER_*.md"))

# Platforms to distribute generated content to
DEFAULT_PLATFORMS = ["twitter", "instagram", "tiktok", "linkedin", "threads"]

# Content types to cycle through
CONTENT_TYPES = [
    "twitter_thread", "tiktok_script", "newsletter_blurb",
    "royalroad_chapter_note", "amazon_a_plus",
]

TONES = ["urgent", "hopeful", "mysterious", "theological"]

# ---------------------------------------------------------------------------
# Sabbath Logic
# ---------------------------------------------------------------------------

def is_sabbath(now: Optional[datetime] = None) -> bool:
    """Return True if current local time falls within Friday 18:00 → Saturday 18:00."""
    if now is None:
        now = datetime.now()
    weekday = now.weekday()  # Monday=0 … Sunday=6
    hour = now.hour

    # Friday (4) after sundown
    if weekday == 4 and hour >= SABBATH_SUNDOWN_HOUR:
        return True
    # Saturday (5) before sundown
    if weekday == 5 and hour < SABBATH_SUNDOWN_HOUR:
        return True
    return False


def time_until_sabbath_ends(now: Optional[datetime] = None) -> timedelta:
    """Return how long until the Sabbath ends (Saturday at sundown)."""
    if now is None:
        now = datetime.now()
    # Find next Saturday 18:00
    weekday = now.weekday()
    if weekday == 4:
        # It's Friday — Sabbath ends tomorrow (Saturday) at sundown
        days_ahead = 1
    elif weekday == 5:
        # It's Saturday — Sabbath ends today at sundown
        days_ahead = 0
    else:
        days_ahead = (5 - weekday) % 7
    end = now.replace(hour=SABBATH_SUNDOWN_HOUR, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
    if end <= now:
        end += timedelta(days=7)
    return end - now


# ---------------------------------------------------------------------------
# Task Timestamps (track last execution of each task)
# ---------------------------------------------------------------------------

class _TaskTimers:
    """Track when each background task last ran."""
    def __init__(self):
        self.last_content_gen: Optional[datetime] = None
        self.last_trend_scrape: Optional[datetime] = None
        self.last_seo_suggest: Optional[datetime] = None
        self.last_queue_process: Optional[datetime] = None
        self.last_campaign_log: Optional[datetime] = None
        self.cycles_completed: int = 0
        self.content_generated: int = 0
        self.errors: int = 0

    def is_due(self, last: Optional[datetime], interval_hours: float) -> bool:
        if last is None:
            return True
        elapsed = (datetime.now(timezone.utc) - last).total_seconds() / 3600
        return elapsed >= interval_hours

    def status(self) -> dict:
        def _fmt(dt):
            return dt.isoformat() if dt else "never"
        return {
            "cycles_completed": self.cycles_completed,
            "content_generated": self.content_generated,
            "errors": self.errors,
            "last_content_gen": _fmt(self.last_content_gen),
            "last_trend_scrape": _fmt(self.last_trend_scrape),
            "last_seo_suggest": _fmt(self.last_seo_suggest),
            "last_queue_process": _fmt(self.last_queue_process),
            "last_campaign_log": _fmt(self.last_campaign_log),
        }

_timers = _TaskTimers()

# ---------------------------------------------------------------------------
# Scheduler State
# ---------------------------------------------------------------------------

_running: bool = False
_task: Optional[asyncio.Task] = None


def get_status() -> dict:
    now = datetime.now()
    sabbath = is_sabbath(now)
    status = {
        "running": _running,
        "is_sabbath": sabbath,
        "mode": "resting — Sabbath" if sabbath else "working",
        "current_time": now.isoformat(),
        "cycle_interval_min": CYCLE_INTERVAL_MINUTES,
        "chapters_available": len(CHAPTER_FILES),
    }
    status.update(_timers.status())
    if sabbath:
        remaining = time_until_sabbath_ends(now)
        status["sabbath_ends_in"] = str(remaining).split(".")[0]
    return status


# ---------------------------------------------------------------------------
# Individual Tasks
# ---------------------------------------------------------------------------

async def _task_generate_content(conn) -> dict:
    """Pick a chapter, generate content for a random platform, and queue it."""
    import httpx

    if not CHAPTER_FILES:
        log.warning("No chapter files found in %s", MANUSCRIPT_DIR)
        return {"skipped": "no chapters found"}

    # Pick a chapter — favor chapters we've generated less content for
    chapter_file = random.choice(CHAPTER_FILES)
    chapter_name = chapter_file.stem
    # Extract chapter number from filename like CHAPTER_01_THE_AWAKENING
    parts = chapter_name.split("_")
    try:
        chapter_num = int(parts[1])
    except (IndexError, ValueError):
        chapter_num = 1

    # Read a chunk of the chapter (first 6000 chars for prompt)
    source_text = chapter_file.read_text(encoding="utf-8")[:6000]
    if len(source_text) < 100:
        return {"skipped": f"chapter {chapter_num} too short"}

    content_type = random.choice(CONTENT_TYPES)
    tone = random.choice(TONES)

    # Get voice profile prompt fragment
    voice_fragment = campaign_planner.get_voice_prompt_fragment(conn, "TNC Brand Voice")

    # Get canon context from Qdrant
    canon_context = ""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            embed_resp = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": source_text[:2000]},
            )
            embed_resp.raise_for_status()
            vec = embed_resp.json()["embedding"]
            search_resp = await client.post(
                "http://localhost:6333/collections/nephilim_chronicles/points/search",
                json={"vector": vec, "limit": 3, "with_payload": True},
            )
            search_resp.raise_for_status()
            results = search_resp.json().get("result", [])
            canon_context = "\n\n".join(
                r.get("payload", {}).get("excerpt", "")
                for r in results if r.get("payload")
            )
    except Exception as exc:
        log.debug("Qdrant context pull failed (non-fatal): %s", exc)

    # Get audience context for prompt enrichment
    audiences = campaign_planner.get_audiences(conn)
    audience_context = ""
    if audiences:
        ya = next((a for a in audiences if "Young Adult" in a.get("name", "")), audiences[0])
        audience_context = (
            f"\nTarget audience: {ya['name']}\n"
            f"Demographics: {json.dumps(ya.get('demographics', {}))}\n"
            f"Content preferences: {json.dumps(ya.get('content_preferences', {}))}\n"
        )

    # Build system prompt
    system_prompts = {
        "twitter_thread": (
            "You are a marketing copywriter for The Nephilim Chronicles — a Christian "
            "apocalyptic fiction series. Write a compelling Twitter/X thread (3-7 tweets, "
            "each ≤280 chars). Hooks, cliffhangers, theological intrigue."
        ),
        "tiktok_script": (
            "You are a TikTok script writer for The Nephilim Chronicles. Write a 30-60s "
            "script with a powerful hook in the first 3 seconds. Visual cues in [brackets]."
        ),
        "newsletter_blurb": (
            "Write a Substack newsletter blurb for The Nephilim Chronicles. 200-400 words. "
            "Open with an intriguing question. End with a call-to-action."
        ),
        "royalroad_chapter_note": (
            "Write an author's note for a Royal Road chapter posting. Conversational, insider "
            "tone. Tease what's coming. 100-250 words."
        ),
        "amazon_a_plus": (
            "Write Amazon A+ content: headline, 3 USP bullet points, short paragraph. "
            "Focus: Tom Clancy meets Frank Peretti. Unique magic system: Acoustic Paradigm."
        ),
    }
    system = system_prompts.get(content_type, system_prompts["twitter_thread"])

    user_msg = (
        f"Content type: {content_type}\nTone: {tone}\n"
        f"Book 1, Chapter {chapter_num}\n{audience_context}\n{voice_fragment}\n"
        f"--- SOURCE ---\n{source_text[:5000]}\n--- END ---\n"
    )
    if canon_context:
        user_msg += f"\n--- CANON CONTEXT ---\n{canon_context[:2000]}\n--- END ---\n"

    user_msg += (
        "\nGenerate THREE versions:\n"
        "1. SHORT (≤150 words)\n2. MEDIUM (150-350 words)\n3. LONG (350-600 words)\n\n"
        "Also provide: 5-8 hashtags (include #NephilimChronicles #ChristianFiction), "
        "3-5 emojis, 5-8 SEO keywords.\n\n"
        "Format as valid JSON: {short, medium, long, hashtags, emojis, seo_keywords}"
    )

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "system": system,
        "prompt": user_msg,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 4096},
    })

    try:
        async with httpx.AsyncClient(timeout=300) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                content=payload,
                headers={"Content-Type": "application/json"},
            )
            r.raise_for_status()
            raw = r.json().get("response", "")
    except Exception as exc:
        log.error("Content generation failed: %s", exc)
        return {"error": str(exc)}

    # Parse LLM response
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1]
    if "```" in text:
        text = text.split("```", 1)[0]
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {
            "short": raw[:500], "medium": raw[:1500], "long": raw,
            "hashtags": ["#NephilimChronicles", "#ChristianFiction"],
            "emojis": ["⚔️", "📖", "🔥"],
            "seo_keywords": ["nephilim", "christian fiction"],
        }

    for key in ("short", "medium", "long"):
        val = parsed.get(key)
        if isinstance(val, list):
            parsed[key] = "\n\n".join(str(item) for item in val)

    hashtags = parsed.get("hashtags", ["#NephilimChronicles", "#ChristianFiction"])

    # Distribute to social platforms
    variants = {
        "short": parsed.get("short", ""),
        "medium": parsed.get("medium", ""),
        "long": parsed.get("long", ""),
    }

    # Get active campaign (if any) to associate content with
    campaigns = campaign_planner.list_campaigns(conn, "active")
    campaign_id = campaigns[0]["id"] if campaigns else None

    queued = social_media.distribute_content(
        conn, variants, hashtags,
        campaign_id=campaign_id,
        platforms=DEFAULT_PLATFORMS,
    )

    # Update SEO topic authority
    for kw in parsed.get("seo_keywords", [])[:5]:
        seo_optimizer.update_topic_authority(conn, kw, score_delta=0.5,
                                             related_keywords=parsed.get("seo_keywords", []))

    _timers.content_generated += 1
    log.info("AUTO-GEN: %s for Ch%d (%s tone) → queued to %d platforms",
             content_type, chapter_num, tone, len(queued))

    return {
        "content_type": content_type,
        "chapter": chapter_num,
        "tone": tone,
        "platforms_queued": len(queued),
        "hashtags": hashtags,
    }


async def _task_scrape_trends(conn) -> dict:
    """Scrape RSS trend feeds for competitor and market intelligence."""
    try:
        results = await scraper.scrape_trends(conn)
        log.info("TREND-SCAN: scraped %d trend sources", len(results))
        return {"sources_scraped": len(results)}
    except Exception as exc:
        log.error("Trend scrape failed: %s", exc)
        return {"error": str(exc)}


async def _task_seo_suggest(conn) -> dict:
    """Run periodic SEO keyword discovery via LLM."""
    topics = [
        "nephilim mythology in young adult fiction",
        "christian fantasy book club discussions",
        "angel war fiction BookTok trending",
        "book of enoch modern fantasy novels",
        "dark christian speculative fiction series",
        "mars ancient alien mystery novels",
        "celtic warrior mythology books",
        "Frank Peretti spiritual warfare fiction",
    ]
    topic = random.choice(topics)
    try:
        suggestions = await seo_optimizer.suggest_keywords(conn, topic, "young adult readers 16-25")
        log.info("SEO-DISCOVER: suggested keywords for '%s': %s", topic, suggestions[:3])
        return {"topic": topic, "suggestions_count": len(suggestions)}
    except Exception as exc:
        log.error("SEO suggestion failed: %s", exc)
        return {"error": str(exc)}


async def _task_process_queue(conn) -> dict:
    """Process the queue: auto-post via API, stage manual items for clipboard."""
    result = await poster.auto_post_queue(conn, limit=20)
    total = result.get("api_posted", 0) + result.get("manual_ready", 0)
    if total:
        log.info("QUEUE-PROCESS: %d API-posted, %d staged for manual, %d failed",
                 result.get("api_posted", 0), result.get("manual_ready", 0),
                 result.get("failed", 0))
    return result


async def _task_campaign_health(conn) -> dict:
    """Snapshot campaign health into memory for tracking over time."""
    campaigns = campaign_planner.list_campaigns(conn)
    queue_stats = social_media.get_queue_stats(conn)
    seo_report = seo_optimizer.get_keyword_report(conn)

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_campaigns": len([c for c in campaigns if c.get("status") == "active"]),
        "total_campaigns": len(campaigns),
        "queue_total": queue_stats.get("total", 0),
        "queue_posted": queue_stats.get("by_status", {}).get("posted", 0),
        "seo_keywords_tracked": seo_report.get("total_tracked", 0),
        "seo_trending_up": seo_report.get("up", 0),
    }
    memory_store.remember(conn, "scheduler", "campaign_health_snapshot", snapshot)
    log.info("HEALTH-SNAP: %d campaigns, %d queued, %d SEO keywords",
             snapshot["total_campaigns"], snapshot["queue_total"], snapshot["seo_keywords_tracked"])
    return snapshot


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

async def _scheduler_loop(conn):
    """Main scheduler loop — runs until stopped or interrupted."""
    global _running
    _running = True
    log.info("═══ SCHEDULER STARTED — Agent 13 works 24/6, rests on the Sabbath ═══")

    while _running:
        now = datetime.now()
        now_utc = datetime.now(timezone.utc)

        # ── Sabbath Rest ──────────────────────────────────────────────
        if is_sabbath(now):
            remaining = time_until_sabbath_ends(now)
            log.info("🕊️  SABBATH REST — resuming in %s", str(remaining).split(".")[0])
            memory_store.remember(conn, "scheduler", "sabbath_rest", {
                "entered": now_utc.isoformat(),
                "resumes_in": str(remaining).split(".")[0],
            })
            # Sleep in 5-minute increments so we can respond to stop requests
            while is_sabbath() and _running:
                await asyncio.sleep(300)  # 5 minutes
            if not _running:
                break
            log.info("═══ SABBATH ENDED — resuming work ═══")
            memory_store.remember(conn, "scheduler", "sabbath_resume", {
                "resumed_at": datetime.now(timezone.utc).isoformat(),
            })
            continue

        # ── Work Cycle ────────────────────────────────────────────────
        _timers.cycles_completed += 1
        cycle_num = _timers.cycles_completed
        log.info("─── CYCLE %d ───", cycle_num)

        # Task 1: Content Generation (every CONTENT_GEN_INTERVAL_HOURS)
        if _timers.is_due(_timers.last_content_gen, CONTENT_GEN_INTERVAL_HOURS):
            try:
                result = await _task_generate_content(conn)
                _timers.last_content_gen = now_utc
                memory_store.remember(conn, "scheduler", "last_content_gen", result)
            except Exception as exc:
                log.error("Content gen task failed: %s", exc)
                _timers.errors += 1

        # Task 2: Trend Scraping (every TREND_SCRAPE_INTERVAL_HOURS)
        if _timers.is_due(_timers.last_trend_scrape, TREND_SCRAPE_INTERVAL_HOURS):
            try:
                result = await _task_scrape_trends(conn)
                _timers.last_trend_scrape = now_utc
                memory_store.remember(conn, "scheduler", "last_trend_scrape", result)
            except Exception as exc:
                log.error("Trend scrape task failed: %s", exc)
                _timers.errors += 1

        # Task 3: SEO Keyword Discovery (every SEO_SUGGEST_INTERVAL_HOURS)
        if _timers.is_due(_timers.last_seo_suggest, SEO_SUGGEST_INTERVAL_HOURS):
            try:
                result = await _task_seo_suggest(conn)
                _timers.last_seo_suggest = now_utc
                memory_store.remember(conn, "scheduler", "last_seo_suggest", result)
            except Exception as exc:
                log.error("SEO suggest task failed: %s", exc)
                _timers.errors += 1

        # Task 4: Queue Processing (every QUEUE_PROCESS_INTERVAL_MINUTES)
        queue_interval_h = QUEUE_PROCESS_INTERVAL_MINUTES / 60
        if _timers.is_due(_timers.last_queue_process, queue_interval_h):
            try:
                result = await _task_process_queue(conn)
                _timers.last_queue_process = now_utc
            except Exception as exc:
                log.error("Queue processing failed: %s", exc)
                _timers.errors += 1

        # Task 5: Campaign Health Snapshot (every CAMPAIGN_LOG_INTERVAL_HOURS)
        if _timers.is_due(_timers.last_campaign_log, CAMPAIGN_LOG_INTERVAL_HOURS):
            try:
                result = await _task_campaign_health(conn)
                _timers.last_campaign_log = now_utc
            except Exception as exc:
                log.error("Campaign health task failed: %s", exc)
                _timers.errors += 1

        log.info("─── CYCLE %d COMPLETE — sleeping %d min ───", cycle_num, CYCLE_INTERVAL_MINUTES)
        # Sleep in 1-minute increments so stop requests are responsive
        for _ in range(CYCLE_INTERVAL_MINUTES):
            if not _running:
                break
            await asyncio.sleep(60)

    log.info("═══ SCHEDULER STOPPED ═══")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start(conn) -> bool:
    """Start the autonomous scheduler as a background asyncio task."""
    global _task, _running
    if _running and _task and not _task.done():
        log.warning("Scheduler already running")
        return False
    _task = asyncio.get_event_loop().create_task(_scheduler_loop(conn))
    return True


def stop() -> bool:
    """Request the scheduler to stop gracefully."""
    global _running
    if not _running:
        return False
    _running = False
    log.info("Scheduler stop requested — will halt at next cycle boundary")
    return True
