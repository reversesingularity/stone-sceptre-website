"""
Web Scraper — lightweight trend monitoring, competitor analysis, and hashtag
tracking for Agent 13. Uses httpx for HTTP requests. No heavy browser
dependencies — designed for public page scraping and API-based data.
"""

import json
import re
from datetime import datetime, timezone
from typing import Optional
from html.parser import HTMLParser

import httpx

try:
    from . import memory_store as ms
except ImportError:
    import memory_store as ms


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class _TextExtractor(HTMLParser):
    """Simple HTML-to-text extractor."""
    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            cleaned = data.strip()
            if cleaned:
                self._text.append(cleaned)

    def get_text(self) -> str:
        return "\n".join(self._text)


def extract_text(html: str) -> str:
    """Extract visible text from HTML."""
    parser = _TextExtractor()
    parser.feed(html)
    return parser.get_text()


# ── Generic Page Scraper ─────────────────────────────────────────────────

async def scrape_page(url: str, timeout: int = 30) -> dict:
    """Scrape a single page and return extracted text + metadata."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TNCAgent13/1.0; +https://kermangild.com)",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            text = extract_text(r.text)
            # Extract title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""
            # Extract meta description
            desc_match = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
                r.text, re.IGNORECASE
            )
            meta_desc = desc_match.group(1).strip() if desc_match else ""
            return {
                "url": url,
                "status": r.status_code,
                "title": title,
                "meta_description": meta_desc,
                "text_length": len(text),
                "text_preview": text[:2000],
                "scraped_at": _now(),
            }
    except Exception as exc:
        return {"url": url, "error": str(exc), "scraped_at": _now()}


# ── Competitor Analysis ──────────────────────────────────────────────────

COMPETITOR_SOURCES = [
    # Christian fiction / speculative fiction comparison sites
    {"name": "Goodreads Christian Fantasy", "url": "https://www.goodreads.com/shelf/show/christian-fantasy", "type": "competitor"},
    {"name": "Realm Makers", "url": "https://www.realmmakers.com/", "type": "industry"},
]


async def scrape_competitor(conn, url: str, name: str = "", source_type: str = "competitor") -> dict:
    """Scrape a competitor page and store results."""
    result = await scrape_page(url)
    result["source_name"] = name or url
    ms.insert_row(conn, "scrape_results", {
        "source": url,
        "source_type": source_type,
        "query": name,
        "data": json.dumps(result),
        "scraped_at": _now(),
    })
    return result


# ── Trend Monitoring ─────────────────────────────────────────────────────

# Public RSS/Atom feeds for book/fiction trends
TREND_FEEDS = [
    {"name": "Publishers Weekly", "url": "https://www.publishersweekly.com/pw/feeds/recent/index.xml", "type": "industry"},
    {"name": "BookRiot", "url": "https://bookriot.com/feed/", "type": "ya_trends"},
]


async def scrape_trends(conn, custom_urls: list[str] | None = None) -> list[dict]:
    """Scrape trend sources and store results."""
    sources = custom_urls or [f["url"] for f in TREND_FEEDS]
    results = []
    for url in sources:
        result = await scrape_page(url)
        ms.insert_row(conn, "scrape_results", {
            "source": url,
            "source_type": "trend",
            "query": "trend_scan",
            "data": json.dumps(result),
            "scraped_at": _now(),
        })
        results.append(result)
    return results


# ── Amazon ASIN Lookup (metadata only) ───────────────────────────────────

async def scrape_amazon_metadata(asin: str) -> dict:
    """Scrape basic metadata from an Amazon product page (title, rank, categories)."""
    url = f"https://www.amazon.com/dp/{asin}"
    result = await scrape_page(url)
    # Extract bestseller rank if present
    text = result.get("text_preview", "")
    rank_match = re.search(r"#([\d,]+)\s+in\s+([\w\s&]+)", text)
    if rank_match:
        result["bestseller_rank"] = rank_match.group(1).replace(",", "")
        result["category"] = rank_match.group(2).strip()
    return result


# ── Scrape Results Retrieval ─────────────────────────────────────────────

def get_scrape_results(conn, source_type: str | None = None, limit: int = 50) -> list[dict]:
    if source_type:
        rows = ms.list_rows(conn, "scrape_results", "source_type=?", (source_type,), limit)
    else:
        rows = ms.list_rows(conn, "scrape_results", limit=limit)
    for r in rows:
        if r.get("data"):
            try:
                r["data"] = json.loads(r["data"])
            except (json.JSONDecodeError, TypeError):
                pass
    return rows


def get_scrape_summary(conn) -> dict:
    """Summary of all scraping activity."""
    all_rows = ms.list_rows(conn, "scrape_results", limit=1000)
    by_type = {}
    for r in all_rows:
        t = r.get("source_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return {
        "total_scrapes": len(all_rows),
        "by_type": by_type,
        "sources_scraped": list(set(r.get("source", "") for r in all_rows)),
    }
