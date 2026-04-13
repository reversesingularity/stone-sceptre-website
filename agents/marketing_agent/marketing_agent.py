"""
Marketing Content Agent (Agent 13) — Port 8773
Full-spectrum marketing engine: content generation, social media management,
campaign planning, SEO optimization, web scraping, and persistent memory.

Capabilities:
  - Content generation (Twitter, TikTok, newsletter, Royal Road, Amazon A+, grants)
  - Social media posting queue with platform-specific formatting
  - Campaign & content calendar with audience segment targeting
  - SEO keyword tracking, topic authority, and content optimization
  - Web scraping for trend monitoring and competitor analysis
  - Persistent memory (SQLite) for long-term marketing intelligence

Part of The Nephilim Chronicles Creative Swarm.
"""

import json
import sys
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure submodules importable when run as __main__
_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

import memory_store
import campaign_planner
import seo_optimizer
import social_media
import scraper
import scheduler
import poster

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_PORT = 8773
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "nephilim_chronicles"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "LOGS"
LOG_DIR.mkdir(exist_ok=True)
MARKETING_LOG = LOG_DIR / "marketing_log.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Agent13] %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "marketing_agent.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("agent13")

# ---------------------------------------------------------------------------
# Rate limiter (token-bucket, 10 req/min)
# ---------------------------------------------------------------------------
class _RateLimiter:
    def __init__(self, max_tokens: int = 10, refill_seconds: float = 60.0):
        self.max_tokens = max_tokens
        self.refill_seconds = refill_seconds
        self.tokens = float(max_tokens)
        self.last_refill = time.monotonic()

    def acquire(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * (self.max_tokens / self.refill_seconds))
        self.last_refill = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

_limiter = _RateLimiter(max_tokens=10, refill_seconds=60.0)

# ---------------------------------------------------------------------------
# Persistent Memory DB
# ---------------------------------------------------------------------------
_db = memory_store.get_connection()
memory_store.init_db(_db)

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------
class ContentType(str, Enum):
    twitter_thread = "twitter_thread"
    tiktok_script = "tiktok_script"
    newsletter_blurb = "newsletter_blurb"
    royalroad_chapter_note = "royalroad_chapter_note"
    amazon_a_plus = "amazon_a_plus"
    grant_application = "grant_application"

class Tone(str, Enum):
    urgent = "urgent"
    hopeful = "hopeful"
    mysterious = "mysterious"
    theological = "theological"

class ContentRequest(BaseModel):
    content_type: ContentType
    source_text: str = Field(..., min_length=20, max_length=50_000)
    target_audience: str = "Christian speculative fiction readers"
    key_themes: list[str] = Field(default_factory=lambda: ["acoustic reality", "endurance commission", "Two Witnesses"])
    book_number: int = Field(ge=1, le=5)
    chapter_number: int = Field(ge=0, le=30)
    tone: Tone = Tone.urgent

class ContentVariant(BaseModel):
    short: str
    medium: str
    long: str

class ContentResponse(BaseModel):
    content_type: str
    variants: ContentVariant
    hashtags: list[str]
    emojis: list[str]
    seo_keywords: list[str]
    book: int
    chapter: int
    generated_at: str

# ---------------------------------------------------------------------------
# System prompts per content type
# ---------------------------------------------------------------------------
_SYSTEM_PROMPTS: dict[str, str] = {
    "twitter_thread": (
        "You are a marketing copywriter for a Christian apocalyptic fiction series called "
        "The Nephilim Chronicles. Write a compelling Twitter/X thread (3-7 tweets, each ≤280 chars). "
        "Use hooks, cliffhangers, and theological intrigue. Thread should make readers NEED to read the book."
    ),
    "tiktok_script": (
        "You are a TikTok script writer for The Nephilim Chronicles — a Christian apocalyptic fiction series. "
        "Write a 30-60 second script with a powerful hook in the first 3 seconds. "
        "Include visual direction cues in [brackets]. Tone: dramatic, urgent, cinematic."
    ),
    "newsletter_blurb": (
        "You are writing a Substack/newsletter blurb for The Nephilim Chronicles. "
        "200-400 words. Open with an intriguing question or revelation from the scene. "
        "End with a call-to-action. Maintain literary quality — this audience reads seriously."
    ),
    "royalroad_chapter_note": (
        "You are writing an author's note for a Royal Road chapter posting of The Nephilim Chronicles. "
        "Conversational, insider tone. Tease what's coming. Reference the lore without spoiling. "
        "Include a question to drive comments. 100-250 words."
    ),
    "amazon_a_plus": (
        "You are writing Amazon A+ content modules for The Nephilim Chronicles. "
        "Create compelling product description copy: headline, 3 bullet points highlighting unique selling "
        "propositions, and a short paragraph. Focus on genre positioning: Tom Clancy meets Frank Peretti. "
        "Emphasise the Acoustic Paradigm as the unique magic system."
    ),
    "grant_application": (
        "You are writing grant application copy for The Nephilim Chronicles project — "
        "a Christian apocalyptic fiction series blending 1 Enoch mythology, Celtic legend, and "
        "Revelation eschatology. Formal, evidence-based register. Emphasise literary merit, "
        "theological scholarship, cultural significance, and market viability."
    ),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _build_prompt(req: ContentRequest, context: str = "") -> str:
    system = _SYSTEM_PROMPTS[req.content_type.value]
    user_msg = (
        f"Content type: {req.content_type.value}\n"
        f"Tone: {req.tone.value}\n"
        f"Target audience: {req.target_audience}\n"
        f"Key themes: {', '.join(req.key_themes)}\n"
        f"Book {req.book_number}, Chapter {req.chapter_number}\n\n"
        f"--- SOURCE SCENE ---\n{req.source_text[:8000]}\n--- END ---\n\n"
    )
    if context:
        user_msg += f"--- CANON CONTEXT ---\n{context[:4000]}\n--- END ---\n\n"

    user_msg += (
        "Generate THREE versions:\n"
        "1. SHORT (≤150 words)\n"
        "2. MEDIUM (150-350 words)\n"
        "3. LONG (350-600 words)\n\n"
        "Also provide:\n"
        "- 5-8 hashtags (include #NephilimChronicles #ChristianFiction)\n"
        "- 3-5 relevant emojis\n"
        "- 5-8 SEO keywords\n\n"
        "Format your response as valid JSON with keys: "
        "short, medium, long, hashtags, emojis, seo_keywords"
    )
    return json.dumps({
        "model": OLLAMA_MODEL,
        "system": system,
        "prompt": user_msg,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 4096},
    })


async def _query_qdrant(text: str, limit: int = 3) -> str:
    """Pull relevant canon context from Qdrant via embedding similarity."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            embed_resp = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text[:4000]},
            )
            embed_resp.raise_for_status()
            vec = embed_resp.json()["embedding"]

            search_resp = await client.post(
                f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search",
                json={"vector": vec, "limit": limit, "with_payload": True},
            )
            search_resp.raise_for_status()
            results = search_resp.json().get("result", [])
            chunks = [r.get("payload", {}).get("excerpt", "") for r in results if r.get("payload")]
            return "\n\n".join(chunks)
    except Exception as exc:
        log.warning("Qdrant context pull failed (non-fatal): %s", exc)
        return ""


def _parse_llm_response(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and list values."""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1]
    if "```" in text:
        text = text.split("```", 1)[0]
    # Try to find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {
            "short": raw[:500],
            "medium": raw[:1500],
            "long": raw,
            "hashtags": ["#NephilimChronicles", "#ChristianFiction"],
            "emojis": ["⚔️", "📖", "🔥"],
            "seo_keywords": ["nephilim", "christian fiction", "apocalyptic"],
        }
    # LLM may return list values (e.g. tweet arrays) — join them into strings
    for key in ("short", "medium", "long"):
        val = parsed.get(key)
        if isinstance(val, list):
            parsed[key] = "\n\n".join(str(item) for item in val)
    return parsed


def _log_generation(req: ContentRequest, resp: ContentResponse) -> None:
    """Append generation record to marketing_log.json."""
    entry = {
        "timestamp": resp.generated_at,
        "content_type": resp.content_type,
        "book": resp.book,
        "chapter": resp.chapter,
        "hashtags": resp.hashtags,
        "seo_keywords": resp.seo_keywords,
        "short_preview": resp.variants.short[:200],
    }
    try:
        existing = json.loads(MARKETING_LOG.read_text(encoding="utf-8")) if MARKETING_LOG.exists() else []
    except (json.JSONDecodeError, OSError):
        existing = []
    existing.append(entry)
    MARKETING_LOG.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# FastAPI App (with lifespan for scheduler auto-start)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def _lifespan(application: FastAPI):
    """Auto-start the 24/6 scheduler when the server boots."""
    scheduler.start(_db)
    log.info("Autonomous scheduler started — working 24/6, resting on the Sabbath")
    yield
    scheduler.stop()
    log.info("Scheduler stopped via lifespan shutdown")

app = FastAPI(
    title="Marketing Content Agent (Agent 13)",
    description=(
        "Full-spectrum marketing engine for The Nephilim Chronicles. "
        "Content generation, social media management, campaign planning, "
        "SEO optimization, web scraping, and persistent memory. "
        "Autonomous 24/6 scheduler — rests on the Sabbath."
    ),
    version="2.1.0",
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    ollama_ok = False
    qdrant_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{QDRANT_URL}/collections")
            qdrant_ok = r.status_code == 200
    except Exception:
        pass
    queue_stats = social_media.get_queue_stats(_db)
    kw_report = seo_optimizer.get_keyword_report(_db)
    return {
        "service": "marketing_content_agent",
        "agent_id": 13,
        "port": API_PORT,
        "status": "ok" if ollama_ok else "degraded",
        "version": "2.1.0",
        "ollama": "up" if ollama_ok else "down",
        "qdrant": "up" if qdrant_ok else "down",
        "model": OLLAMA_MODEL,
        "rate_limit": "10/min",
        "capabilities": [
            "content_generation", "social_media_queue", "campaign_planning",
            "seo_optimization", "web_scraping", "persistent_memory",
            "autonomous_scheduler_24_6",
        ],
        "scheduler": scheduler.get_status(),
        "social_queue": queue_stats,
        "seo_keywords_tracked": kw_report["total_tracked"],
        "memory_db": str(memory_store.DB_PATH),
    }


# ── Content Generation (original, upgraded) ──────────────────────────────

@app.post("/generate_content", response_model=ContentResponse)
async def generate_content(req: ContentRequest):
    if not _limiter.acquire():
        raise HTTPException(status_code=429, detail="Rate limit exceeded (10 req/min). Try again shortly.")

    log.info("Generating %s for Book %d Ch%d (tone=%s)", req.content_type.value, req.book_number, req.chapter_number, req.tone.value)

    # Pull optional Qdrant context
    context = await _query_qdrant(req.source_text[:1000])

    # Build and send prompt to Ollama
    payload = _build_prompt(req, context)
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            r = await client.post(f"{OLLAMA_URL}/api/generate", content=payload, headers={"Content-Type": "application/json"})
            r.raise_for_status()
            raw = r.json().get("response", "")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama generation timed out")
    except Exception as exc:
        log.error("Ollama call failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Ollama generation failed: {exc}")

    parsed = _parse_llm_response(raw)

    resp = ContentResponse(
        content_type=req.content_type.value,
        variants=ContentVariant(
            short=parsed.get("short", ""),
            medium=parsed.get("medium", ""),
            long=parsed.get("long", ""),
        ),
        hashtags=parsed.get("hashtags", ["#NephilimChronicles", "#ChristianFiction"]),
        emojis=parsed.get("emojis", ["⚔️", "📖"]),
        seo_keywords=parsed.get("seo_keywords", ["nephilim chronicles", "christian fiction"]),
        book=req.book_number,
        chapter=req.chapter_number,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    # Update SEO topic authority from generated keywords
    for kw in resp.seo_keywords[:5]:
        seo_optimizer.update_topic_authority(_db, kw, score_delta=0.5,
                                             related_keywords=resp.seo_keywords)

    _log_generation(req, resp)
    log.info("Generated %s — %d/%d/%d chars (S/M/L)", req.content_type.value,
             len(resp.variants.short), len(resp.variants.medium), len(resp.variants.long))
    return resp


# ── Generate + Auto-Queue to Social Platforms ────────────────────────────

class GenerateAndQueueRequest(ContentRequest):
    platforms: list[str] = Field(default=["twitter", "instagram", "tiktok", "linkedin"])
    campaign_id: Optional[str] = None
    scheduled_at: Optional[str] = None

@app.post("/generate_and_queue")
async def generate_and_queue(req: GenerateAndQueueRequest):
    """Generate content AND automatically queue it across platforms."""
    # Generate content
    content_req = ContentRequest(
        content_type=req.content_type,
        source_text=req.source_text,
        target_audience=req.target_audience,
        key_themes=req.key_themes,
        book_number=req.book_number,
        chapter_number=req.chapter_number,
        tone=req.tone,
    )
    generated = await generate_content(content_req)

    # Queue across platforms
    variants = {
        "short": generated.variants.short,
        "medium": generated.variants.medium,
        "long": generated.variants.long,
    }
    queued = social_media.distribute_content(
        _db, variants, generated.hashtags,
        campaign_id=req.campaign_id,
        platforms=req.platforms,
        scheduled_at=req.scheduled_at,
    )
    log.info("Generated + queued to %d platforms", len(queued))
    return {"generated": generated, "queued_count": len(queued), "platforms": req.platforms}


# ═══════════════════════════════════════════════════════════════════════════
# CAMPAIGN MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

class CampaignCreate(BaseModel):
    name: str
    target_audience: str = "Young adult Christian fiction readers"
    goals: list[str] = Field(default_factory=lambda: ["increase visibility", "drive sales"])
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@app.post("/campaigns")
async def create_campaign(req: CampaignCreate):
    camp = campaign_planner.create_campaign(
        _db, req.name, req.target_audience, req.goals, req.start_date, req.end_date)
    log.info("Created campaign: %s", req.name)
    return camp

@app.get("/campaigns")
async def list_campaigns(status: Optional[str] = None):
    return campaign_planner.list_campaigns(_db, status)

@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    row = memory_store.get_row(_db, "campaigns", campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return row

@app.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, updates: dict):
    if not campaign_planner.update_campaign(_db, campaign_id, **updates):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"updated": True}


# ── Content Calendar ─────────────────────────────────────────────────────

class CalendarEntry(BaseModel):
    platform: str
    content_type: str
    scheduled_date: str
    content: dict
    campaign_id: Optional[str] = None
    hashtags: list[str] = Field(default_factory=list)
    seo_keywords: list[str] = Field(default_factory=list)
    book_number: int = 1
    chapter_number: int = 0

@app.post("/calendar")
async def schedule_content(req: CalendarEntry):
    entry = campaign_planner.schedule_content(
        _db, req.platform, req.content_type, req.scheduled_date,
        req.content, req.campaign_id, req.hashtags, req.seo_keywords,
        req.book_number, req.chapter_number)
    return entry

@app.get("/calendar")
async def get_calendar(status: Optional[str] = None, platform: Optional[str] = None):
    return campaign_planner.get_calendar(_db, status, platform)

@app.get("/calendar/upcoming")
async def get_upcoming():
    return campaign_planner.get_upcoming(_db)

@app.put("/calendar/{content_id}/status")
async def update_content_status(content_id: str, status: str = Query(...)):
    if not campaign_planner.update_content_status(_db, content_id, status):
        raise HTTPException(status_code=404, detail="Content not found")
    return {"updated": True}


# ═══════════════════════════════════════════════════════════════════════════
# AUDIENCE SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════

class AudienceCreate(BaseModel):
    name: str
    description: str
    demographics: dict = Field(default_factory=dict)
    interests: list[str] = Field(default_factory=list)
    content_preferences: dict = Field(default_factory=dict)

@app.post("/audiences")
async def create_audience(req: AudienceCreate):
    aud = campaign_planner.create_audience(
        _db, req.name, req.description, req.demographics,
        req.interests, req.content_preferences)
    log.info("Created audience segment: %s", req.name)
    return aud

@app.get("/audiences")
async def get_audiences():
    return campaign_planner.get_audiences(_db)


# ── Voice Profiles ───────────────────────────────────────────────────────

class VoiceProfileCreate(BaseModel):
    name: str
    description: str
    tone_attributes: dict = Field(default_factory=dict)
    vocabulary: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)

@app.post("/voice-profiles")
async def create_voice_profile(req: VoiceProfileCreate):
    vp = campaign_planner.create_voice_profile(
        _db, req.name, req.description, req.tone_attributes,
        req.vocabulary, req.avoid, req.examples)
    log.info("Created voice profile: %s", req.name)
    return vp

@app.get("/voice-profiles")
async def get_voice_profiles():
    return campaign_planner.get_voice_profiles(_db)


# ═══════════════════════════════════════════════════════════════════════════
# SOCIAL MEDIA QUEUE
# ═══════════════════════════════════════════════════════════════════════════

class SocialQueueAdd(BaseModel):
    platform: str
    content: str
    campaign_id: Optional[str] = None
    hashtags: list[str] = Field(default_factory=list)
    media_urls: list[str] = Field(default_factory=list)
    scheduled_at: Optional[str] = None

@app.post("/social/queue")
async def add_to_social_queue(req: SocialQueueAdd):
    item = social_media.add_to_queue(
        _db, req.platform, req.content, req.scheduled_at,
        req.campaign_id, req.hashtags, req.media_urls)
    log.info("Queued content for %s", req.platform)
    return item

@app.get("/social/queue")
async def get_social_queue(platform: Optional[str] = None, status: str = "queued"):
    return social_media.get_queue(_db, platform, status)

@app.get("/social/queue/stats")
async def get_queue_stats():
    return social_media.get_queue_stats(_db)

@app.post("/social/queue/{queue_id}/posted")
async def mark_posted(queue_id: str):
    if not social_media.mark_posted(_db, queue_id):
        raise HTTPException(status_code=404, detail="Queue item not found")
    return {"marked": "posted"}

@app.post("/social/queue/{queue_id}/failed")
async def mark_failed(queue_id: str, error: str = Query(default="manual")):
    if not social_media.mark_failed(_db, queue_id, error):
        raise HTTPException(status_code=404, detail="Queue item not found")
    return {"marked": "failed"}

@app.post("/social/format")
async def format_for_platform_endpoint(platform: str = Query(...), content: str = Query(...),
                                        hashtags: list[str] = Query(default=[])):
    return social_media.format_for_platform(content, platform, hashtags)

@app.get("/social/platforms")
async def list_platforms():
    return social_media.PLATFORM_SPECS


# ── Posting & Clipboard ──────────────────────────────────────────────────

@app.get("/social/clipboard")
async def get_clipboard():
    """Get queue items formatted for manual copy-paste."""
    items = poster.get_clipboard_items(_db)
    return {"count": len(items), "items": items}


@app.post("/social/clipboard/{item_id}/done")
async def mark_clipboard_done(item_id: str):
    """Mark a clipboard item as manually posted."""
    if not poster.mark_manually_posted(_db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"marked": "posted"}


@app.post("/social/post-now")
async def post_now(limit: int = Query(default=10, ge=1, le=50)):
    """Process the queue: auto-post via API where keys exist, stage manual items."""
    results = await poster.auto_post_queue(_db, limit=limit)
    log.info("POST-NOW: %s", results)
    return results


@app.get("/social/api-status")
async def api_status():
    """Which platform APIs are configured and ready to post."""
    return poster.get_configured_platforms()


# ═══════════════════════════════════════════════════════════════════════════
# SEO OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════

class KeywordAdd(BaseModel):
    keyword: str
    search_volume: int = 0
    difficulty: float = 0.0

class KeywordRankUpdate(BaseModel):
    keyword: str
    rank: int

@app.post("/seo/keywords")
async def add_seo_keyword(req: KeywordAdd):
    kw = seo_optimizer.add_keyword(_db, req.keyword, req.search_volume, req.difficulty)
    log.info("Tracking SEO keyword: %s", req.keyword)
    return kw

@app.get("/seo/keywords")
async def get_seo_keywords(trend: Optional[str] = None):
    return seo_optimizer.get_keywords(_db, trend)

@app.post("/seo/keywords/rank")
async def update_keyword_rank(req: KeywordRankUpdate):
    if not seo_optimizer.update_keyword_rank(_db, req.keyword, req.rank):
        raise HTTPException(status_code=404, detail="Keyword not tracked")
    return {"updated": True}

@app.get("/seo/report")
async def get_seo_report():
    return seo_optimizer.get_keyword_report(_db)

@app.get("/seo/authority")
async def get_topic_authority():
    return seo_optimizer.get_topic_authority(_db)

@app.post("/seo/analyze")
async def analyze_content_seo(content: str = Query(...), keywords: list[str] = Query(default=[])):
    return await seo_optimizer.analyze_content_seo(content, keywords or None)

@app.post("/seo/suggest-keywords")
async def suggest_keywords(topic: str = Query(...), audience: str = Query(default="young adult readers")):
    suggestions = await seo_optimizer.suggest_keywords(_db, topic, audience)
    return {"topic": topic, "audience": audience, "suggestions": suggestions}


# ═══════════════════════════════════════════════════════════════════════════
# WEB SCRAPING
# ═══════════════════════════════════════════════════════════════════════════

class ScrapeRequest(BaseModel):
    url: str
    name: str = ""
    source_type: str = "competitor"

@app.post("/scrape/page")
async def scrape_page_endpoint(req: ScrapeRequest):
    result = await scraper.scrape_competitor(_db, req.url, req.name, req.source_type)
    log.info("Scraped: %s", req.url)
    return result

@app.post("/scrape/trends")
async def scrape_trends(urls: list[str] | None = None):
    results = await scraper.scrape_trends(_db, urls)
    log.info("Scraped %d trend sources", len(results))
    return results

@app.post("/scrape/amazon/{asin}")
async def scrape_amazon(asin: str):
    return await scraper.scrape_amazon_metadata(asin)

@app.get("/scrape/results")
async def get_scrape_results(source_type: Optional[str] = None):
    return scraper.get_scrape_results(_db, source_type)

@app.get("/scrape/summary")
async def get_scrape_summary():
    return scraper.get_scrape_summary(_db)


# ═══════════════════════════════════════════════════════════════════════════
# PERSISTENT MEMORY
# ═══════════════════════════════════════════════════════════════════════════

class MemoryStore(BaseModel):
    category: str
    key: str
    value: str | dict | list
    metadata: dict = Field(default_factory=dict)

@app.post("/memory")
async def store_memory(req: MemoryStore):
    memory_store.remember(_db, req.category, req.key, req.value, req.metadata)
    return {"stored": True, "category": req.category, "key": req.key}

@app.get("/memory/{category}")
async def recall_memory(category: str, key: Optional[str] = None):
    result = memory_store.recall(_db, category, key)
    if result is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"category": category, "key": key, "value": result}

@app.get("/memory")
async def list_memory_categories():
    rows = _db.execute("SELECT DISTINCT category FROM memory").fetchall()
    return {"categories": [r["category"] for r in rows]}


# ═══════════════════════════════════════════════════════════════════════════
# AUTONOMOUS SCHEDULER  (24/6 — rests on the Sabbath)
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/scheduler/status")
async def scheduler_status():
    return scheduler.get_status()


@app.post("/scheduler/stop")
async def scheduler_stop():
    if scheduler.stop():
        log.info("Scheduler stop requested via API")
        return {"stopped": True, "message": "Scheduler will halt at next cycle boundary"}
    return {"stopped": False, "message": "Scheduler was not running"}


@app.post("/scheduler/start")
async def scheduler_start():
    if scheduler.start(_db):
        log.info("Scheduler (re)started via API")
        return {"started": True}
    return {"started": False, "message": "Scheduler already running"}


# ---------------------------------------------------------------------------
# Startup Seeding — pre-populate YA audience segment and core SEO keywords
# ---------------------------------------------------------------------------
def _seed_defaults():
    """Seed default audience segments, voice profiles, and SEO keywords on first run."""
    # Young Adult audience segment
    existing = campaign_planner.get_audiences(_db)
    existing_names = {a["name"] for a in existing}

    if "Young Adult Readers (16-25)" not in existing_names:
        campaign_planner.create_audience(_db,
            name="Young Adult Readers (16-25)",
            description=(
                "Core target: YA and New Adult readers aged 16-25 who consume "
                "supernatural thriller, fantasy, and faith-based fiction. Active on "
                "TikTok (#BookTok), Instagram (#Bookstagram), and Goodreads. "
                "Drawn to morally complex characters, fast pacing, and cosmic-scale stakes."
            ),
            demographics={"age_range": "16-25", "platforms": ["tiktok", "instagram", "goodreads", "threads"],
                          "reading_habits": "3-5 books/month", "format_preference": ["ebook", "audiobook"]},
            interests=["supernatural thriller", "angel mythology", "apocalyptic fiction",
                        "Celtic mythology", "faith and doubt", "conspiracy theories",
                        "ancient mysteries", "BookTok recommendations", "dark academia"],
            content_preferences={"tone": "urgent, mysterious, cinematic",
                                  "hook_style": "question or shocking revelation",
                                  "cta_style": "curiosity-driven, not salesy",
                                  "visual": "dark aesthetic, book covers, atmospheric stills"},
        )
        log.info("Seeded YA audience segment")

    if "Christian Fiction Community" not in existing_names:
        campaign_planner.create_audience(_db,
            name="Christian Fiction Community",
            description=(
                "Established Christian fiction readers — evangelical, Protestant, "
                "and Catholic audiences who value theological depth alongside "
                "entertainment. Active on Facebook groups, Goodreads, and Substack."
            ),
            demographics={"age_range": "25-55", "platforms": ["facebook", "goodreads", "substack"],
                          "reading_habits": "2-4 books/month", "format_preference": ["paperback", "ebook"]},
            interests=["biblical prophecy", "end times fiction", "Frank Peretti", "Ted Dekker",
                        "C.S. Lewis", "spiritual warfare", "Book of Enoch", "Revelation"],
            content_preferences={"tone": "theological, hopeful, reverent",
                                  "hook_style": "scripture-grounded revelation",
                                  "cta_style": "community and discussion oriented"},
        )
        log.info("Seeded Christian Fiction audience segment")

    if "#BookTok / Speculative Fiction" not in existing_names:
        campaign_planner.create_audience(_db,
            name="#BookTok / Speculative Fiction",
            description=(
                "Genre-agnostic BookTok community that gravitates toward high-concept "
                "speculative fiction, romantasy, dark fantasy, and sci-fi thrillers. "
                "Discovery-driven — one viral TikTok can drive 10K+ units."
            ),
            demographics={"age_range": "18-30", "platforms": ["tiktok", "instagram", "threads"],
                          "reading_habits": "4-8 books/month", "format_preference": ["ebook", "audiobook"]},
            interests=["speculative fiction", "romantasy", "dark fantasy", "sci-fi thriller",
                        "viral book recommendations", "book clubs", "indie authors"],
            content_preferences={"tone": "dramatic, cinematic, hook-heavy",
                                  "hook_style": "3-second attention grab",
                                  "cta_style": "FOMO, community, aesthetic"},
        )
        log.info("Seeded BookTok audience segment")

    # Seed voice profiles
    existing_vp = campaign_planner.get_voice_profiles(_db)
    vp_names = {v["name"] for v in existing_vp}

    if "TNC Brand Voice" not in vp_names:
        campaign_planner.create_voice_profile(_db,
            name="TNC Brand Voice",
            description="The Nephilim Chronicles official brand voice — literary weight meets cinematic urgency.",
            tone_attributes={"register": "literary", "urgency": "high", "mystery": "high",
                              "theological_depth": "medium-high", "accessibility": "medium"},
            vocabulary=["acoustic paradigm", "Cydonian", "Watchers", "Nephilim", "Mo Chrá",
                         "creation frequencies", "endurance commission", "Two Witnesses",
                         "celestial", "ancient", "revelation", "covenant"],
            avoid=["cheesy", "preachy", "sappy", "generic fantasy terms", "cringe",
                    "overly modern slang", "clickbait without substance"],
            examples=[
                "What if the cure wasn't a cure at all — but a frequency?",
                "They didn't fall. They descended. And they brought the blueprints of Heaven with them.",
                "Tom Clancy meets Frank Peretti. The war is real. The battlefield is acoustic.",
            ],
        )
        log.info("Seeded TNC brand voice profile")

    # Seed core SEO keywords
    core_keywords = [
        ("nephilim chronicles", 1200, 0.4),
        ("christian apocalyptic fiction", 2400, 0.3),
        ("book of enoch fiction", 1800, 0.2),
        ("angel mythology books", 3200, 0.5),
        ("supernatural thriller christian", 900, 0.2),
        ("young adult christian fantasy", 4400, 0.6),
        ("ya angel books", 2900, 0.5),
        ("nephilim books for teens", 1600, 0.3),
        ("christian speculative fiction", 1500, 0.3),
        ("end times fiction series", 2100, 0.4),
        ("celtic mythology fantasy", 2800, 0.5),
        ("frank peretti style books", 1100, 0.2),
        ("ted dekker similar books", 1300, 0.3),
        ("acoustic paradigm fiction", 50, 0.1),
        ("watcher mythology novels", 800, 0.2),
        ("mars ancient civilization books", 1900, 0.4),
        ("booktok christian fiction", 3600, 0.4),
        ("dark christian fantasy", 1400, 0.3),
    ]
    for kw, vol, diff in core_keywords:
        seo_optimizer.add_keyword(_db, kw, vol, diff)
    log.info("Seeded %d SEO keywords", len(core_keywords))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    _seed_defaults()
    log.info("Starting Marketing Content Agent (Agent 13) v2.1 on port %d", API_PORT)
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
