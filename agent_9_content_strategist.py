"""
DESKTOP-SINGULA — Agent 9: Content Strategist & NZ Grant Monitor
================================================================
HTTP server (port 8772) providing two complementary capabilities:

1. CONTENT STRATEGY — Automates the content lifecycle for Kerman Gild Publishing:
   - Social media content generation (TikTok scripts, LinkedIn posts)
   - SEO metadata for Amazon KDP (7-keyword slots, categories, A/B titles)
   - Paid serialization scheduling (14-day DTC exclusivity windows)
   - YouTube "Super" anchor content briefs

2. NZ GRANT MONITOR — Scrapes NZ literary funding sources:
   - NZSA (nzsa.org.nz)
   - Mātātuhi Foundation
   - Creative NZ grants
   Self-correction: on scrape failure → RSS → sitemap → cached → flag for HITL

Endpoints:
   POST /generate-social         — Social media content from chapter text
   POST /seo-metadata            — Amazon KDP SEO optimization
   POST /serialization-schedule  — Paid serialization release calendar
   POST /scrape-nz-grants        — Trigger NZ grant scrape cycle
   POST /youtube-anchor          — YouTube content briefs from chapters
   GET  /opportunities           — Current OPPORTUNITIES_LOG.md
   GET  /health                  — Health check

Governance: AGENT_9, APPEND-only permissions (see governance.py)

Usage:
    python agent_9_content_strategist.py [--port 8772] [--log-level INFO]
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

API_PORT          = int(os.environ.get("AGENT_9_PORT", "8772"))
NEMOTRON_ROUTER   = "http://localhost:8768"
OPPORTUNITIES_LOG = PROJECT_ROOT / "LOGS" / "OPPORTUNITIES_LOG.md"

# NZ Grant Sources (URLs for scraping)
NZ_GRANT_SOURCES = [
    {
        "name": "NZSA — New Zealand Society of Authors",
        "url": "https://www.nzsa.co.nz/grants-and-opportunities/",
        "rss": "https://www.nzsa.co.nz/feed/",
        "type": "grants",
    },
    {
        "name": "Mātātuhi Foundation",
        "url": "https://www.matatuhi.org.nz/",
        "rss": None,
        "type": "grants",
    },
    {
        "name": "Creative NZ — Literature Grants",
        "url": "https://www.creativenz.govt.nz/funding-and-support/find-opportunities",
        "rss": "https://www.creativenz.govt.nz/rss",
        "type": "government",
    },
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AGENT-9] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_DIR / "agent_9.log"), encoding="utf-8"),
    ]
)
logger = logging.getLogger("agent_9")


# ── Nemotron Router Helper ────────────────────────────────────────────────────

def call_nemotron(prompt: str, system: str = "", max_tokens: int = 2048,
                  task_type: str = "content_strategy",
                  json_mode: bool = False) -> str:
    """Route a request through the Nemotron Tool Router cascade."""
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


# ── Content Strategy Endpoints ────────────────────────────────────────────────

def generate_social_content(chapter_text: str, book: int, chapter: int,
                            series_title: str = "The Nephilim Chronicles") -> dict:
    """Generate social media content from a chapter excerpt."""
    system = (
        "You are a social media strategist for Kerman Gild Publishing. "
        "You create viral, hook-driven content for dark fantasy / apocalyptic fiction. "
        "Target audience: 25-45, C.S. Lewis + Tom Clancy crossover readers. "
        "Platforms: TikTok (60s max), LinkedIn (thought leadership), Twitter/X (thread). "
        "RESPOND ONLY WITH VALID JSON. No prose, no markdown, no code blocks, no explanation."
    )
    prompt = f"""Generate social media content for:
Series: {series_title}
Book: {book}  Chapter: {chapter}

Chapter excerpt (first 2000 chars):
\"\"\"{chapter_text[:2000]}\"\"\"

Return JSON with these keys:
{{
  "tiktok_script": "60-second script with hook, body, CTA (under 150 words)",
  "tiktok_hashtags": ["list", "of", "hashtags"],
  "linkedin_post": "300-word thought leadership post connecting chapter themes to current events",
  "twitter_thread": ["tweet 1 (hook)", "tweet 2", "tweet 3", "tweet 4 (CTA)"],
  "youtube_community_post": "Engaging community post teasing the chapter"
}}

Return ONLY the JSON object. No explanatory text, no markdown, no code blocks."""

    raw = call_nemotron(prompt, system=system, max_tokens=1500,
                        task_type="content_strategy", json_mode=True)

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}

    result["book"] = book
    result["chapter"] = chapter
    result["generated_at"] = datetime.now().isoformat()
    return result


def generate_seo_metadata(book_title: str, book_description: str,
                          genre: str = "Christian Apocalyptic Fiction") -> dict:
    """Generate Amazon KDP SEO metadata."""
    system = (
        "You are an Amazon KDP SEO specialist. "
        "Generate metadata optimized for discovery in Amazon's A10 search algorithm. "
        "Focus on reader-intent keywords, not author-intent."
    )
    prompt = f"""Generate Amazon KDP SEO metadata for:
Title: {book_title}
Genre: {genre}
Description: {book_description[:1000]}

Return JSON:
{{
  "keywords_7": ["7 Amazon keyword slots (each up to 50 chars, no commas within)"],
  "categories_bisac": ["Primary BISAC", "Secondary BISAC"],
  "ab_titles": [
    {{"title": "Option A", "subtitle": "Subtitle A"}},
    {{"title": "Option B", "subtitle": "Subtitle B"}}
  ],
  "description_html": "<p>Amazon-optimized HTML description (4000 char max)</p>",
  "search_terms_analysis": "Brief analysis of keyword competition and strategy"
}}"""

    raw = call_nemotron(prompt, system=system, max_tokens=1500,
                        task_type="content_strategy")

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}

    result["generated_at"] = datetime.now().isoformat()
    return result


def generate_serialization_schedule(book: int, total_chapters: int,
                                    dtc_exclusivity_days: int = 14) -> dict:
    """Plan paid serialization release calendar."""
    system = (
        "You are a publishing strategist specializing in serialized fiction monetization. "
        "Plan a release schedule that maximizes reader retention and revenue."
    )
    prompt = f"""Create a serialization release schedule:
Book: {book}
Total chapters: {total_chapters}
DTC exclusivity window: {dtc_exclusivity_days} days per chapter
Platforms: DTC website (exclusive first), then Kindle Vella, Royal Road, Wattpad Paid

Rules:
- First 3 chapters free everywhere (reader acquisition)
- Chapters 4+ have {dtc_exclusivity_days}-day DTC exclusivity before wide release
- Build cliffhangers at natural story break points
- Include email automation triggers

Return JSON:
{{
  "schedule": [
    {{"chapter": 1, "dtc_release": "Day 0", "wide_release": "Day 0", "free": true, "email_trigger": "welcome_sequence"}},
    ...
  ],
  "revenue_projections": {{
    "dtc_per_chapter": "$X",
    "kindle_vella_tokens": "X tokens/chapter estimate",
    "total_estimated_30_day": "$X"
  }},
  "marketing_notes": "Strategy notes"
}}"""

    raw = call_nemotron(prompt, system=system, max_tokens=2000,
                        task_type="content_strategy")

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}

    result["book"] = book
    result["generated_at"] = datetime.now().isoformat()
    return result


def generate_youtube_anchor(chapter_text: str, book: int, chapter: int) -> dict:
    """Generate YouTube 'Super' anchor content brief from chapter."""
    system = (
        "You are a YouTube content strategist for a dark fantasy fiction brand. "
        "Create 'anchor' content briefs — long-form videos that establish authority, "
        "drive book sales, and build the Nephilim Chronicles community."
    )
    prompt = f"""Create a YouTube anchor content brief for:
Series: The Nephilim Chronicles
Book: {book}  Chapter: {chapter}

Chapter excerpt:
\"\"\"{chapter_text[:3000]}\"\"\"

Return JSON:
{{
  "video_title": "Optimized YouTube title (under 60 chars)",
  "thumbnail_concept": "Description of click-worthy thumbnail",
  "hook_script": "First 30 seconds script (the hook — must grab in 5s)",
  "outline": [
    {{"timestamp": "0:00", "section": "Hook", "notes": "..."}},
    {{"timestamp": "0:30", "section": "Context", "notes": "..."}},
    ...
  ],
  "target_length_minutes": 12,
  "cta": "End card CTA script",
  "tags": ["youtube", "tags"],
  "description_seo": "SEO-optimized YouTube description (first 200 chars most important)"
}}"""

    raw = call_nemotron(prompt, system=system, max_tokens=2000,
                        task_type="content_strategy")

    result = _extract_json(raw)
    if not result:
        result = {"error": "LLM returned non-JSON", "raw": raw[:500]}

    result["book"] = book
    result["chapter"] = chapter
    result["generated_at"] = datetime.now().isoformat()
    return result


# ── NZ Grant Monitor ──────────────────────────────────────────────────────────

def scrape_nz_grants() -> dict:
    """
    Scrape NZ literary grant sources with self-correction cascade:
      1. Direct page scrape
      2. RSS feed fallback
      3. Sitemap discovery
      4. Flag for HITL review
    """
    results = []
    errors = []

    for source in NZ_GRANT_SOURCES:
        entry = {
            "source": source["name"],
            "url": source["url"],
            "opportunities": [],
            "status": "unknown",
            "scraped_at": datetime.now().isoformat(),
        }

        # Tier 1: Direct page fetch
        try:
            r = requests.get(
                source["url"],
                headers={"User-Agent": "KermanGildBot/1.0 (+https://kermangild.com)"},
                timeout=15,
            )
            if r.status_code == 200:
                # Use LLM to extract structured grant data from HTML
                opportunities = _extract_grants_from_html(
                    r.text[:8000], source["name"]
                )
                entry["opportunities"] = opportunities
                entry["status"] = "scraped"
                results.append(entry)
                continue
            else:
                logger.warning(f"  {source['name']}: HTTP {r.status_code}")
        except Exception as e:
            logger.warning(f"  {source['name']} direct scrape failed: {e}")

        # Tier 2: RSS fallback
        if source.get("rss"):
            try:
                r = requests.get(
                    source["rss"],
                    headers={"User-Agent": "KermanGildBot/1.0"},
                    timeout=15,
                )
                if r.status_code == 200:
                    opportunities = _extract_grants_from_rss(
                        r.text[:8000], source["name"]
                    )
                    entry["opportunities"] = opportunities
                    entry["status"] = "scraped_via_rss"
                    results.append(entry)
                    continue
            except Exception as e:
                logger.warning(f"  {source['name']} RSS fallback failed: {e}")

        # Tier 3: Flag for HITL
        entry["status"] = "needs_human_review"
        entry["error"] = "All automated scrape methods failed"
        errors.append(source["name"])
        results.append(entry)

    # Update OPPORTUNITIES_LOG.md
    _update_opportunities_log(results)

    return {
        "sources_checked": len(NZ_GRANT_SOURCES),
        "successful": len(NZ_GRANT_SOURCES) - len(errors),
        "needs_review": errors,
        "results": results,
        "scraped_at": datetime.now().isoformat(),
    }


def _extract_grants_from_html(html_text: str, source_name: str) -> list:
    """Use LLM to extract structured grant info from raw HTML."""
    prompt = f"""Extract grant/funding opportunities from this webpage content.
Source: {source_name}

HTML content (truncated):
\"\"\"
{html_text[:6000]}
\"\"\"

Return JSON array of opportunities:
[
  {{
    "title": "Grant name",
    "deadline": "YYYY-MM-DD or 'rolling' or 'unknown'",
    "amount": "$X or 'varies' or 'unknown'",
    "eligibility": "Brief eligibility notes",
    "url": "Direct link if found",
    "relevance": "high/medium/low (for NZ-based fiction publisher)"
  }}
]
Only return the JSON array. If no grants found, return []."""

    raw = call_nemotron(prompt, max_tokens=1000, task_type="nz_grants")
    try:
        # Try to extract JSON array
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def _extract_grants_from_rss(rss_text: str, source_name: str) -> list:
    """Use LLM to extract grant info from RSS XML."""
    prompt = f"""Extract grant/funding opportunities from this RSS feed.
Source: {source_name}

RSS content (truncated):
\"\"\"
{rss_text[:6000]}
\"\"\"

Return JSON array of opportunities:
[
  {{
    "title": "Grant name",
    "deadline": "YYYY-MM-DD or 'rolling' or 'unknown'",
    "amount": "$X or 'varies' or 'unknown'",
    "eligibility": "Brief eligibility notes",
    "url": "Direct link if found",
    "relevance": "high/medium/low (for NZ-based fiction publisher)"
  }}
]
Only return the JSON array. If no grants found, return []."""

    raw = call_nemotron(prompt, max_tokens=1000, task_type="nz_grants")
    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def _update_opportunities_log(results: list):
    """Append new findings to OPPORTUNITIES_LOG.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"\n## Scrape: {timestamp}\n"]

    for entry in results:
        lines.append(f"### {entry['source']} — Status: {entry['status']}")
        if entry["opportunities"]:
            lines.append("| Title | Deadline | Amount | Relevance |")
            lines.append("|-------|----------|--------|-----------|")
            for opp in entry["opportunities"]:
                lines.append(
                    f"| {opp.get('title', '?')} "
                    f"| {opp.get('deadline', '?')} "
                    f"| {opp.get('amount', '?')} "
                    f"| {opp.get('relevance', '?')} |"
                )
        else:
            lines.append("_No opportunities extracted._")
        lines.append("")

    try:
        with open(OPPORTUNITIES_LOG, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Updated {OPPORTUNITIES_LOG.name}")
    except Exception as e:
        logger.error(f"Failed to update opportunities log: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict | None:
    """Find and parse the first JSON object in text.

    Handles three formats:
    1. Bare JSON string
    2. Markdown code blocks: ```json {...} ```
    3. JSON embedded in prose (uses balanced brace counting)
    """
    if not text:
        return None
    text = text.strip()
    # 1. Direct parse (clean response)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 2. Markdown code block: ```json {...} ```
    import re
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 3. Balanced brace extraction (finds first complete {...})
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    start = -1  # reset and keep scanning
    return None


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class Agent9Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        logger.debug(f"HTTP {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self.send_json({
                "status":  "ok",
                "service": "agent_9_content_strategist",
                "port":    API_PORT,
            })

        elif self.path == "/opportunities":
            if OPPORTUNITIES_LOG.exists():
                content = OPPORTUNITIES_LOG.read_text(encoding="utf-8")
                self.send_json({"log": content})
            else:
                self.send_json({"log": "(no opportunities log yet)"})

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        try:
            body = self.read_json_body()
        except Exception:
            self.send_json({"error": "Invalid JSON body"}, 400)
            return

        if self.path == "/generate-social":
            chapter_text = body.get("chapter_text", "")
            book = body.get("book", 1)
            chapter = body.get("chapter", 1)
            if not chapter_text:
                self.send_json({"error": "chapter_text required"}, 400)
                return
            result = generate_social_content(chapter_text, book, chapter)
            self.send_json(result)

        elif self.path == "/seo-metadata":
            title = body.get("book_title", "")
            desc = body.get("description", "")
            if not title:
                self.send_json({"error": "book_title required"}, 400)
                return
            result = generate_seo_metadata(title, desc)
            self.send_json(result)

        elif self.path == "/serialization-schedule":
            book = body.get("book", 1)
            total_chapters = body.get("total_chapters", 20)
            dtc_days = body.get("dtc_exclusivity_days", 14)
            result = generate_serialization_schedule(book, total_chapters, dtc_days)
            self.send_json(result)

        elif self.path == "/youtube-anchor":
            chapter_text = body.get("chapter_text", "")
            book = body.get("book", 1)
            chapter = body.get("chapter", 1)
            if not chapter_text:
                self.send_json({"error": "chapter_text required"}, 400)
                return
            result = generate_youtube_anchor(chapter_text, book, chapter)
            self.send_json(result)

        elif self.path == "/scrape-nz-grants":
            logger.info("NZ Grant scrape triggered")
            result = scrape_nz_grants()
            self.send_json(result)

        else:
            self.send_json({"error": f"Unknown endpoint: {self.path}"}, 404)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agent 9: Content Strategist & NZ Grant Monitor"
    )
    parser.add_argument("--port", type=int, default=API_PORT)
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))
    port = args.port

    server = HTTPServer(("0.0.0.0", port), Agent9Handler)
    logger.info(f"Agent 9 — Content Strategist listening on :{port}")
    logger.info(f"  Nemotron Router: {NEMOTRON_ROUTER}")
    logger.info(f"  Opportunities Log: {OPPORTUNITIES_LOG}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Agent 9 shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
