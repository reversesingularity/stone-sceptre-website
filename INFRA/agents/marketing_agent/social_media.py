"""
Social Media Queue & Platform Adapters — posting queue, platform-specific
formatting, and scheduling for Agent 13.
"""

import json
from datetime import datetime, timezone
from typing import Optional

try:
    from . import memory_store as ms
except ImportError:
    import memory_store as ms

# Platform character limits and formatting rules
PLATFORM_SPECS = {
    "twitter": {"max_chars": 280, "max_hashtags": 5, "thread_max": 10, "media": True},
    "tiktok": {"max_chars": 2200, "max_hashtags": 8, "media": True, "video_required": True},
    "instagram": {"max_chars": 2200, "max_hashtags": 30, "media": True},
    "facebook": {"max_chars": 63206, "max_hashtags": 10, "media": True},
    "linkedin": {"max_chars": 3000, "max_hashtags": 5, "media": True},
    "substack": {"max_chars": None, "max_hashtags": 0, "media": True},
    "royalroad": {"max_chars": None, "max_hashtags": 0, "media": False},
    "threads": {"max_chars": 500, "max_hashtags": 5, "media": True},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Queue Management ─────────────────────────────────────────────────────

def add_to_queue(
    conn,
    platform: str,
    content: str,
    scheduled_at: str | None = None,
    campaign_id: str | None = None,
    hashtags: list[str] | None = None,
    media_urls: list[str] | None = None,
) -> dict:
    """Add content to the social posting queue."""
    qid = ms.insert_row(conn, "social_queue", {
        "platform": platform,
        "content": content,
        "campaign_id": campaign_id,
        "hashtags": json.dumps(hashtags or []),
        "media_urls": json.dumps(media_urls or []),
        "scheduled_at": scheduled_at,
        "status": "queued",
    })
    return ms.get_row(conn, "social_queue", qid)


def get_queue(conn, platform: str | None = None, status: str = "queued", limit: int = 50) -> list[dict]:
    conditions, params = ["status=?"], [status]
    if platform:
        conditions.append("platform=?")
        params.append(platform)
    rows = ms.list_rows(conn, "social_queue", " AND ".join(conditions), tuple(params), limit)
    for r in rows:
        for key in ("hashtags", "media_urls"):
            if r.get(key):
                try:
                    r[key] = json.loads(r[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


def mark_posted(conn, queue_id: str) -> bool:
    return ms.update_row(conn, "social_queue", queue_id, {
        "status": "posted",
        "posted_at": _now(),
    })


def mark_failed(conn, queue_id: str, error: str) -> bool:
    return ms.update_row(conn, "social_queue", queue_id, {
        "status": "failed",
        "error": error,
    })


def get_queue_stats(conn) -> dict:
    """Get posting queue statistics."""
    all_rows = ms.list_rows(conn, "social_queue", limit=1000)
    by_status = {}
    by_platform = {}
    for r in all_rows:
        s = r.get("status", "unknown")
        p = r.get("platform", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        by_platform[p] = by_platform.get(p, 0) + 1
    return {
        "total": len(all_rows),
        "by_status": by_status,
        "by_platform": by_platform,
    }


# ── Platform Formatting ──────────────────────────────────────────────────

def format_for_platform(content: str, platform: str, hashtags: list[str] | None = None) -> dict:
    """Format content for a specific platform, respecting character limits."""
    spec = PLATFORM_SPECS.get(platform, {"max_chars": None, "max_hashtags": 10})
    max_chars = spec.get("max_chars")
    max_tags = spec.get("max_hashtags", 5)

    tags = (hashtags or [])[:max_tags]
    tag_str = " ".join(tags) if tags else ""

    if platform == "twitter":
        return _format_twitter_thread(content, tags)
    elif platform == "tiktok":
        return _format_tiktok(content, tags)
    elif platform == "instagram":
        return _format_instagram(content, tags)
    elif platform == "linkedin":
        return _format_linkedin(content, tags)
    else:
        # Generic formatting
        body = content
        if tag_str:
            body = f"{content}\n\n{tag_str}"
        if max_chars and len(body) > max_chars:
            body = body[:max_chars - 3] + "..."
        return {"platform": platform, "formatted": body, "char_count": len(body)}


def _format_twitter_thread(content: str, hashtags: list[str]) -> dict:
    """Split content into a Twitter thread with proper numbering."""
    max_tweet = 280
    tag_str = " ".join(hashtags[:3])
    tag_len = len(tag_str) + 1 if tag_str else 0

    # Split on double newlines first (natural breaks)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    tweets = []

    for i, para in enumerate(paragraphs):
        available = max_tweet - tag_len - 6  # reserve for numbering " (X/Y)"
        if len(para) <= available:
            tweets.append(para)
        else:
            # Split long paragraphs at sentence boundaries
            words = para.split()
            current = []
            for word in words:
                test = " ".join(current + [word])
                if len(test) > available:
                    if current:
                        tweets.append(" ".join(current))
                    current = [word]
                else:
                    current.append(word)
            if current:
                tweets.append(" ".join(current))

    # Number tweets and add hashtags to last
    total = len(tweets)
    formatted = []
    for i, tweet in enumerate(tweets[:10]):  # Twitter thread max ~10
        numbered = f"{tweet} ({i+1}/{total})" if total > 1 else tweet
        if i == total - 1 and tag_str:
            numbered = f"{numbered}\n{tag_str}"
        if len(numbered) > max_tweet:
            numbered = numbered[:max_tweet - 3] + "..."
        formatted.append(numbered)

    return {
        "platform": "twitter",
        "thread": formatted,
        "tweet_count": len(formatted),
        "char_counts": [len(t) for t in formatted],
    }


def _format_tiktok(content: str, hashtags: list[str]) -> dict:
    tag_str = " ".join(hashtags[:8])
    # TikTok caption with hashtags
    caption = f"{content}\n\n{tag_str}" if tag_str else content
    if len(caption) > 2200:
        caption = caption[:2197] + "..."
    return {
        "platform": "tiktok",
        "caption": caption,
        "char_count": len(caption),
        "note": "Video script should be 30-60 seconds. Hook in first 3 seconds.",
    }


def _format_instagram(content: str, hashtags: list[str]) -> dict:
    tag_str = "\n.\n.\n.\n" + " ".join(hashtags[:30]) if hashtags else ""
    post = f"{content}{tag_str}"
    if len(post) > 2200:
        post = post[:2197] + "..."
    return {
        "platform": "instagram",
        "caption": post,
        "char_count": len(post),
        "note": "Include eye-catching image or carousel. First line is the hook.",
    }


def _format_linkedin(content: str, hashtags: list[str]) -> dict:
    tag_str = "\n\n" + " ".join(hashtags[:5]) if hashtags else ""
    post = f"{content}{tag_str}"
    if len(post) > 3000:
        post = post[:2997] + "..."
    return {
        "platform": "linkedin",
        "post": post,
        "char_count": len(post),
        "note": "Professional tone. Hook in first 2 lines (before 'see more').",
    }


# ── Cross-Platform Campaign Distribution ─────────────────────────────────

def distribute_content(conn, content_variants: dict, hashtags: list[str],
                       campaign_id: str | None = None,
                       platforms: list[str] | None = None,
                       scheduled_at: str | None = None) -> list[dict]:
    """Take generated content variants and queue them across platforms."""
    target_platforms = platforms or ["twitter", "instagram", "tiktok", "linkedin"]
    queued = []

    for platform in target_platforms:
        # Select appropriate variant length for each platform
        if platform == "twitter":
            source = content_variants.get("short", content_variants.get("medium", ""))
        elif platform in ("tiktok", "instagram"):
            source = content_variants.get("medium", content_variants.get("short", ""))
        else:
            source = content_variants.get("long", content_variants.get("medium", ""))

        if not source:
            continue

        formatted = format_for_platform(source, platform, hashtags)
        display = formatted.get("formatted") or formatted.get("caption") or formatted.get("post") or ""
        if formatted.get("thread"):
            display = "\n---\n".join(formatted["thread"])

        item = add_to_queue(
            conn, platform, display,
            scheduled_at=scheduled_at,
            campaign_id=campaign_id,
            hashtags=hashtags,
        )
        queued.append({**item, "format_info": formatted})

    return queued
