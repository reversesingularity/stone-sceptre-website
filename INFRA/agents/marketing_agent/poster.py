"""
Social Media Poster — handles actual posting to platform APIs.

Supports:
  - Twitter/X v2 API  (OAuth 1.0a — direct posting)
  - LinkedIn API       (OAuth 2.0 — text posts)
  - Facebook Graph API (page posts)
  - Threads API        (Meta Threads publishing)

Platforms that can't be API-posted (TikTok, Instagram, Substack, Royal Road)
are exported as clipboard-ready text via the /social/clipboard endpoint.

API keys are loaded from environment variables or a .env file at project root.
If keys are absent, the poster logs a warning and skips that platform.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

try:
    from . import memory_store
except ImportError:
    import memory_store

log = logging.getLogger("agent13.poster")

# ---------------------------------------------------------------------------
# Load .env if present
# ---------------------------------------------------------------------------
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"
if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and val and key not in os.environ:
                os.environ[key] = val


# ---------------------------------------------------------------------------
# Platform credentials (from env vars)
# ---------------------------------------------------------------------------

def _get_twitter_creds() -> Optional[dict]:
    keys = ["TWITTER_API_KEY", "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"]
    vals = {k: os.environ.get(k) for k in keys}
    if all(vals.values()):
        return vals
    return None


def _get_linkedin_creds() -> Optional[dict]:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    person_id = os.environ.get("LINKEDIN_PERSON_ID")
    if token and person_id:
        return {"access_token": token, "person_id": person_id}
    return None


def _get_facebook_creds() -> Optional[dict]:
    token = os.environ.get("FACEBOOK_PAGE_TOKEN")
    page_id = os.environ.get("FACEBOOK_PAGE_ID")
    if token and page_id:
        return {"page_token": token, "page_id": page_id}
    return None


def _get_threads_creds() -> Optional[dict]:
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")
    if token and user_id:
        return {"access_token": token, "user_id": user_id}
    return None


def get_configured_platforms() -> dict:
    """Return which platforms have valid API credentials configured."""
    return {
        "twitter": _get_twitter_creds() is not None,
        "linkedin": _get_linkedin_creds() is not None,
        "facebook": _get_facebook_creds() is not None,
        "threads": _get_threads_creds() is not None,
        "tiktok": False,      # Video-first — manual only
        "instagram": False,   # Requires Meta Business Suite — manual
        "substack": False,    # No API — manual
        "royalroad": False,   # No API — manual
    }


# Manual-only platforms (no API posting available)
MANUAL_PLATFORMS = {"tiktok", "instagram", "substack", "royalroad"}

# ---------------------------------------------------------------------------
# Twitter/X v2 API Posting (OAuth 1.0a)
# ---------------------------------------------------------------------------

def _twitter_oauth_header(method: str, url: str, creds: dict) -> dict:
    """Build OAuth 1.0a header for Twitter API v2."""
    import hashlib
    import hmac
    import time
    import urllib.parse
    import uuid

    oauth_params = {
        "oauth_consumer_key": creds["TWITTER_API_KEY"],
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds["TWITTER_ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }

    # Build signature base string
    params_str = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted(oauth_params.items())
    )
    base = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(params_str, safe='')}"

    signing_key = (
        f"{urllib.parse.quote(creds['TWITTER_API_SECRET'], safe='')}"
        f"&{urllib.parse.quote(creds['TWITTER_ACCESS_SECRET'], safe='')}"
    )
    signature = hmac.new(
        signing_key.encode(), base.encode(), hashlib.sha1
    ).digest()
    import base64
    oauth_params["oauth_signature"] = base64.b64encode(signature).decode()

    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    return {"Authorization": auth_header, "Content-Type": "application/json"}


async def post_twitter(text: str) -> dict:
    """Post a tweet via Twitter API v2. Returns {"posted": True, "id": ...} or error."""
    creds = _get_twitter_creds()
    if not creds:
        return {"posted": False, "error": "Twitter API keys not configured"}

    url = "https://api.twitter.com/2/tweets"
    headers = _twitter_oauth_header("POST", url, creds)

    # Handle threads: if text has numbered tweets (1/N format), post as thread
    lines = text.strip().split("\n\n")
    tweet_ids = []

    async with httpx.AsyncClient(timeout=30) as client:
        reply_to = None
        for i, tweet_text in enumerate(lines):
            tweet_text = tweet_text.strip()
            if not tweet_text or len(tweet_text) > 280:
                # Truncate if over limit
                tweet_text = tweet_text[:277] + "..."

            payload = {"text": tweet_text}
            if reply_to:
                payload["reply"] = {"in_reply_to_tweet_id": reply_to}

            # Regenerate auth header for each request (timestamp changes)
            headers = _twitter_oauth_header("POST", url, creds)
            resp = await client.post(url, json=payload, headers=headers)

            if resp.status_code in (200, 201):
                data = resp.json().get("data", {})
                tweet_id = data.get("id")
                tweet_ids.append(tweet_id)
                reply_to = tweet_id
                log.info("TWITTER: posted tweet %d/%d (id=%s)", i + 1, len(lines), tweet_id)
            else:
                error = resp.text[:300]
                log.error("TWITTER: post failed (status=%d): %s", resp.status_code, error)
                return {
                    "posted": False,
                    "error": f"HTTP {resp.status_code}: {error}",
                    "tweets_posted": len(tweet_ids),
                }

    return {"posted": True, "tweet_ids": tweet_ids, "thread_length": len(tweet_ids)}


# ---------------------------------------------------------------------------
# LinkedIn API Posting
# ---------------------------------------------------------------------------

async def post_linkedin(text: str) -> dict:
    """Post to LinkedIn via v2 API."""
    creds = _get_linkedin_creds()
    if not creds:
        return {"posted": False, "error": "LinkedIn API keys not configured"}

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {creds['access_token']}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": f"urn:li:person:{creds['person_id']}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text[:3000]},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code in (200, 201):
            log.info("LINKEDIN: posted successfully")
            return {"posted": True, "response": resp.json()}
        else:
            error = resp.text[:300]
            log.error("LINKEDIN: post failed (status=%d): %s", resp.status_code, error)
            return {"posted": False, "error": f"HTTP {resp.status_code}: {error}"}


# ---------------------------------------------------------------------------
# Facebook Page Posting
# ---------------------------------------------------------------------------

async def post_facebook(text: str) -> dict:
    """Post to a Facebook Page via Graph API."""
    creds = _get_facebook_creds()
    if not creds:
        return {"posted": False, "error": "Facebook API keys not configured"}

    url = f"https://graph.facebook.com/v19.0/{creds['page_id']}/feed"
    params = {"message": text[:63206], "access_token": creds["page_token"]}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, params=params)
        if resp.status_code == 200:
            post_id = resp.json().get("id")
            log.info("FACEBOOK: posted (id=%s)", post_id)
            return {"posted": True, "post_id": post_id}
        else:
            error = resp.text[:300]
            log.error("FACEBOOK: post failed: %s", error)
            return {"posted": False, "error": error}


# ---------------------------------------------------------------------------
# Threads API Posting (Meta)
# ---------------------------------------------------------------------------

async def post_threads(text: str) -> dict:
    """Post to Threads via Meta's Threads API."""
    creds = _get_threads_creds()
    if not creds:
        return {"posted": False, "error": "Threads API keys not configured"}

    # Step 1: Create container
    create_url = f"https://graph.threads.net/v1.0/{creds['user_id']}/threads"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(create_url, params={
            "media_type": "TEXT",
            "text": text[:500],
            "access_token": creds["access_token"],
        })
        if resp.status_code != 200:
            return {"posted": False, "error": resp.text[:300]}

        container_id = resp.json().get("id")

        # Step 2: Publish
        publish_url = f"https://graph.threads.net/v1.0/{creds['user_id']}/threads_publish"
        resp2 = await client.post(publish_url, params={
            "creation_id": container_id,
            "access_token": creds["access_token"],
        })
        if resp2.status_code == 200:
            log.info("THREADS: posted (id=%s)", resp2.json().get("id"))
            return {"posted": True, "post_id": resp2.json().get("id")}
        else:
            return {"posted": False, "error": resp2.text[:300]}


# ---------------------------------------------------------------------------
# Universal Dispatcher
# ---------------------------------------------------------------------------

_PLATFORM_POSTERS = {
    "twitter": post_twitter,
    "linkedin": post_linkedin,
    "facebook": post_facebook,
    "threads": post_threads,
}


async def post_to_platform(platform: str, content: str) -> dict:
    """Post content to a specific platform. Returns result dict."""
    poster = _PLATFORM_POSTERS.get(platform)
    if not poster:
        return {"posted": False, "error": f"No API poster for '{platform}' — use clipboard instead",
                "manual": True}
    try:
        return await poster(content)
    except Exception as exc:
        log.error("Post to %s failed: %s", platform, exc)
        return {"posted": False, "error": str(exc)}


async def auto_post_queue(conn, limit: int = 10) -> dict:
    """
    Process queued items: post via API where possible, mark manual items
    as 'ready_manual' so clipboard endpoint can pick them up.
    """
    import social_media

    queued = social_media.get_queue(conn, status="queued", limit=limit)
    results = {"api_posted": 0, "manual_ready": 0, "failed": 0, "skipped_no_keys": 0}

    for item in queued:
        platform = item.get("platform", "")
        content = item.get("content", "")
        item_id = item["id"]

        if platform in MANUAL_PLATFORMS:
            # Move to ready_manual so clipboard picks it up
            memory_store.update_row(conn, "social_queue", item_id,
                                    {"status": "ready_manual"})
            results["manual_ready"] += 1
            continue

        configured = get_configured_platforms()
        if not configured.get(platform, False):
            # API not configured — move to ready_manual as fallback
            memory_store.update_row(conn, "social_queue", item_id,
                                    {"status": "ready_manual"})
            results["skipped_no_keys"] += 1
            results["manual_ready"] += 1
            continue

        # Try to post via API
        result = await post_to_platform(platform, content)
        if result.get("posted"):
            social_media.mark_posted(conn, item_id)
            # Store platform response in memory for analytics
            memory_store.remember(conn, "post_results", f"{platform}_{item_id}", result)
            results["api_posted"] += 1
        else:
            social_media.mark_failed(conn, item_id, result.get("error", "unknown"))
            results["failed"] += 1

    return results


# ---------------------------------------------------------------------------
# Clipboard Formatter — for manual posting
# ---------------------------------------------------------------------------

def get_clipboard_items(conn, limit: int = 20) -> list[dict]:
    """
    Get items ready for manual copy-paste, formatted per platform.
    Returns items with status 'ready_manual' or 'queued' on manual-only platforms.
    """
    import social_media

    items = []

    # Get ready_manual items
    manual_items = social_media.get_queue(conn, status="ready_manual", limit=limit)

    # Also get queued items on manual-only platforms
    for platform in MANUAL_PLATFORMS:
        manual_items.extend(social_media.get_queue(conn, platform=platform, status="queued", limit=5))

    seen = set()
    for item in manual_items:
        if item["id"] in seen:
            continue
        seen.add(item["id"])

        content = item.get("content", "")
        hashtags = item.get("hashtags", [])
        if isinstance(hashtags, str):
            try:
                hashtags = json.loads(hashtags)
            except (json.JSONDecodeError, TypeError):
                hashtags = []

        platform = item.get("platform", "unknown")

        items.append({
            "id": item["id"],
            "platform": platform,
            "content": content,
            "hashtags": hashtags,
            "char_count": len(content),
            "created_at": item.get("created_at", ""),
            "copy_ready": _format_copy_ready(content, hashtags, platform),
        })

    return items


def _format_copy_ready(content: str, hashtags: list[str], platform: str) -> str:
    """Format content as a ready-to-paste string for the given platform."""
    tag_str = " ".join(hashtags) if hashtags else ""

    if platform == "tiktok":
        # TikTok: content + hashtags, under 2200 chars
        combined = f"{content}\n\n{tag_str}".strip()
        return combined[:2200]

    elif platform == "instagram":
        # Instagram: content, then ./.  line break, then hashtags
        return f"{content}\n.\n.\n.\n{tag_str}".strip()[:2200]

    elif platform == "substack":
        # Substack newsletter: just the content (no hashtags)
        return content

    elif platform == "royalroad":
        # Royal Road: author note format
        return f"**Author's Note:**\n\n{content}"

    else:
        # Generic: content + hashtags
        return f"{content}\n\n{tag_str}".strip()


def mark_manually_posted(conn, item_id: str) -> bool:
    """Mark a clipboard item as posted after manual copy-paste."""
    return memory_store.update_row(conn, "social_queue", item_id, {
        "status": "posted",
        "posted_at": datetime.now(timezone.utc).isoformat(),
    })
