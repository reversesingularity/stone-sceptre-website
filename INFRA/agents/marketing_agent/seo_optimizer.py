"""
SEO Optimizer — keyword tracking, topic authority mapping, content gap analysis,
and internal linking recommendations for Agent 13.
Persistent state via memory_store SQLite backend.
"""

import json
from datetime import datetime, timezone
from typing import Optional

import httpx

try:
    from . import memory_store as ms
except ImportError:
    import memory_store as ms

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Keyword Tracking ─────────────────────────────────────────────────────

def add_keyword(conn, keyword: str, search_volume: int = 0, difficulty: float = 0.0) -> dict:
    """Add a keyword to track. Upserts if exists."""
    existing = conn.execute("SELECT id FROM seo_keywords WHERE keyword=?", [keyword]).fetchone()
    if existing:
        ms.update_row(conn, "seo_keywords", existing["id"], {
            "search_volume": search_volume,
            "difficulty": difficulty,
            "last_checked": _now(),
        })
        return ms.get_row(conn, "seo_keywords", existing["id"])
    kid = ms.insert_row(conn, "seo_keywords", {
        "keyword": keyword,
        "current_rank": 0,
        "previous_rank": 0,
        "trend": "new",
        "search_volume": search_volume,
        "difficulty": difficulty,
        "last_checked": _now(),
        "history": "[]",
    })
    return ms.get_row(conn, "seo_keywords", kid)


def update_keyword_rank(conn, keyword: str, new_rank: int) -> bool:
    row = conn.execute("SELECT * FROM seo_keywords WHERE keyword=?", [keyword]).fetchone()
    if not row:
        return False
    row = dict(row)
    prev = row.get("current_rank", 0)
    history = json.loads(row.get("history", "[]") or "[]")
    history.append({"date": _now()[:10], "rank": new_rank})
    if len(history) > 90:
        history = history[-90:]

    if new_rank < prev:
        trend = "up"
    elif new_rank > prev:
        trend = "down"
    elif prev == 0:
        trend = "new"
    else:
        trend = "stable"

    return ms.update_row(conn, "seo_keywords", row["id"], {
        "current_rank": new_rank,
        "previous_rank": prev,
        "trend": trend,
        "last_checked": _now(),
        "history": json.dumps(history),
    })


def get_keywords(conn, trend: str | None = None) -> list[dict]:
    if trend:
        rows = ms.list_rows(conn, "seo_keywords", "trend=?", (trend,))
    else:
        rows = ms.list_rows(conn, "seo_keywords")
    for r in rows:
        if r.get("history"):
            try:
                r["history"] = json.loads(r["history"])
            except (json.JSONDecodeError, TypeError):
                pass
    return rows


def get_keyword_report(conn) -> dict:
    """Generate a summary report of keyword positions and movements."""
    keywords = get_keywords(conn)
    return {
        "total_tracked": len(keywords),
        "trending_up": len([k for k in keywords if k.get("trend") == "up"]),
        "trending_down": len([k for k in keywords if k.get("trend") == "down"]),
        "stable": len([k for k in keywords if k.get("trend") == "stable"]),
        "new": len([k for k in keywords if k.get("trend") == "new"]),
        "top_10": [k["keyword"] for k in keywords if (k.get("current_rank") or 999) <= 10],
        "keywords": keywords,
    }


# ── Topic Authority ──────────────────────────────────────────────────────

def update_topic_authority(conn, topic: str, score_delta: float = 0.1,
                           related_keywords: list[str] | None = None,
                           internal_link: str | None = None) -> dict:
    existing = conn.execute("SELECT * FROM topic_authority WHERE topic=?", [topic]).fetchone()
    if existing:
        existing = dict(existing)
        new_score = min(100.0, (existing.get("authority_score", 0) or 0) + score_delta)
        kw = json.loads(existing.get("related_keywords", "[]") or "[]")
        links = json.loads(existing.get("internal_links", "[]") or "[]")
        if related_keywords:
            kw = list(set(kw + related_keywords))
        if internal_link and internal_link not in links:
            links.append(internal_link)
        ms.update_row(conn, "topic_authority", existing["id"], {
            "authority_score": new_score,
            "related_keywords": json.dumps(kw),
            "content_count": (existing.get("content_count", 0) or 0) + 1,
            "internal_links": json.dumps(links),
            "last_updated": _now(),
        })
        return ms.get_row(conn, "topic_authority", existing["id"])
    tid = ms.insert_row(conn, "topic_authority", {
        "topic": topic,
        "authority_score": score_delta,
        "related_keywords": json.dumps(related_keywords or []),
        "content_count": 1,
        "internal_links": json.dumps([internal_link] if internal_link else []),
        "last_updated": _now(),
    })
    return ms.get_row(conn, "topic_authority", tid)


def get_topic_authority(conn) -> list[dict]:
    rows = ms.list_rows(conn, "topic_authority")
    for r in rows:
        for key in ("related_keywords", "internal_links"):
            if r.get(key):
                try:
                    r[key] = json.loads(r[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return sorted(rows, key=lambda x: x.get("authority_score", 0), reverse=True)


# ── SEO Content Analysis (LLM-assisted) ─────────────────────────────────

async def analyze_content_seo(content: str, target_keywords: list[str] | None = None) -> dict:
    """Use LLM to analyze content for SEO quality and suggest improvements."""
    kw_section = ""
    if target_keywords:
        kw_section = f"\nTarget keywords to optimize for: {', '.join(target_keywords)}"

    prompt = json.dumps({
        "model": OLLAMA_MODEL,
        "system": (
            "You are an SEO analyst specializing in fiction and publishing. "
            "Analyze the provided content and return a JSON object with: "
            "keyword_density (dict of keyword->count), "
            "missing_keywords (list of relevant keywords not present), "
            "title_suggestions (list of 3 SEO-optimized titles), "
            "meta_description (150-160 char description), "
            "internal_link_suggestions (list of related topics to link to), "
            "readability_score (1-10), "
            "ya_appeal_score (1-10, how appealing to young adult readers), "
            "improvements (list of specific suggestions). "
            "Return ONLY valid JSON."
        ),
        "prompt": f"Analyze this content for SEO:{kw_section}\n\n{content[:6000]}",
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048},
    })
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                content=prompt,
                headers={"Content-Type": "application/json"},
            )
            r.raise_for_status()
            raw = r.json().get("response", "")
            # Parse JSON from response
            text = raw.strip()
            if "```json" in text:
                text = text.split("```json", 1)[1]
            if "```" in text:
                text = text.split("```", 1)[0]
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
    except Exception:
        pass
    return {"error": "SEO analysis failed", "improvements": []}


async def suggest_keywords(conn, topic: str, audience: str = "young adult readers") -> list[dict]:
    """Use LLM to suggest keywords for a topic, informed by existing tracked keywords."""
    existing = get_keywords(conn)
    existing_kw = [k["keyword"] for k in existing]

    prompt = json.dumps({
        "model": OLLAMA_MODEL,
        "system": (
            "You are a keyword research specialist for Christian fiction publishing. "
            "Suggest 10-15 SEO keywords targeting the specified audience. "
            "Return a JSON array of objects with: keyword, estimated_volume (low/medium/high), "
            "difficulty (easy/medium/hard), relevance (1-10). "
            "Focus on long-tail keywords that young adult and new adult readers would search. "
            "Return ONLY valid JSON array."
        ),
        "prompt": (
            f"Topic: {topic}\nTarget audience: {audience}\n"
            f"Already tracking: {', '.join(existing_kw[:30])}\n"
            f"Suggest NEW keywords not already tracked."
        ),
        "stream": False,
        "options": {"temperature": 0.5, "num_predict": 1024},
    })
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                content=prompt,
                headers={"Content-Type": "application/json"},
            )
            r.raise_for_status()
            raw = r.json().get("response", "")
            text = raw.strip()
            if "```json" in text:
                text = text.split("```json", 1)[1]
            if "```" in text:
                text = text.split("```", 1)[0]
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
    except Exception:
        pass
    return []
