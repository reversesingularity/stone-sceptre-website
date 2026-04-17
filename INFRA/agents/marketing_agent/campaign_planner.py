"""
Campaign & Content Planner — long-term marketing workflow engine for Agent 13.
Manages campaigns, content calendars, audience segments, and voice profiles
with persistent memory across sessions.
"""

import json
from datetime import datetime, timezone
from typing import Optional

try:
    from . import memory_store as ms
except ImportError:
    import memory_store as ms


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Campaigns ────────────────────────────────────────────────────────────

def create_campaign(
    conn,
    name: str,
    target_audience: str,
    goals: list[str],
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    cid = ms.insert_row(conn, "campaigns", {
        "name": name,
        "status": "active",
        "target_audience": target_audience,
        "start_date": start_date or _now()[:10],
        "end_date": end_date,
        "goals": json.dumps(goals),
    })
    return ms.get_row(conn, "campaigns", cid)


def list_campaigns(conn, status: str | None = None) -> list[dict]:
    if status:
        return ms.list_rows(conn, "campaigns", "status=?", (status,))
    return ms.list_rows(conn, "campaigns")


def update_campaign(conn, campaign_id: str, **kwargs) -> bool:
    if "goals" in kwargs and isinstance(kwargs["goals"], list):
        kwargs["goals"] = json.dumps(kwargs["goals"])
    return ms.update_row(conn, "campaigns", campaign_id, kwargs)


# ── Content Calendar ─────────────────────────────────────────────────────

def schedule_content(
    conn,
    platform: str,
    content_type: str,
    scheduled_date: str,
    content: dict,
    campaign_id: str | None = None,
    hashtags: list[str] | None = None,
    seo_keywords: list[str] | None = None,
    book_number: int = 1,
    chapter_number: int = 0,
) -> dict:
    row_id = ms.insert_row(conn, "content_calendar", {
        "campaign_id": campaign_id,
        "platform": platform,
        "content_type": content_type,
        "scheduled_date": scheduled_date,
        "status": "scheduled",
        "content": json.dumps(content),
        "hashtags": json.dumps(hashtags or []),
        "seo_keywords": json.dumps(seo_keywords or []),
        "book_number": book_number,
        "chapter_number": chapter_number,
    })
    return ms.get_row(conn, "content_calendar", row_id)


def get_calendar(conn, status: str | None = None, platform: str | None = None, limit: int = 50) -> list[dict]:
    conditions, params = [], []
    if status:
        conditions.append("status=?")
        params.append(status)
    if platform:
        conditions.append("platform=?")
        params.append(platform)
    where = " AND ".join(conditions)
    rows = ms.list_rows(conn, "content_calendar", where, tuple(params), limit)
    for r in rows:
        for key in ("content", "hashtags", "seo_keywords"):
            if r.get(key):
                try:
                    r[key] = json.loads(r[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


def update_content_status(conn, content_id: str, status: str) -> bool:
    updates = {"status": status}
    if status == "posted":
        updates["posted_at"] = _now()
    return ms.update_row(conn, "content_calendar", content_id, updates)


def get_upcoming(conn, limit: int = 20) -> list[dict]:
    """Get upcoming scheduled content ordered by date."""
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM content_calendar WHERE status IN ('scheduled','draft') "
        "ORDER BY scheduled_date ASC LIMIT ?", [limit]
    ).fetchall()]
    for r in rows:
        for key in ("content", "hashtags", "seo_keywords"):
            if r.get(key):
                try:
                    r[key] = json.loads(r[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


# ── Audience Segments ────────────────────────────────────────────────────

def create_audience(conn, name: str, description: str, demographics: dict,
                    interests: list[str], content_preferences: dict) -> dict:
    aid = ms.insert_row(conn, "audience_segments", {
        "name": name,
        "description": description,
        "demographics": json.dumps(demographics),
        "interests": json.dumps(interests),
        "content_preferences": json.dumps(content_preferences),
    })
    return ms.get_row(conn, "audience_segments", aid)


def get_audiences(conn) -> list[dict]:
    rows = ms.list_rows(conn, "audience_segments")
    for r in rows:
        for key in ("demographics", "interests", "content_preferences", "engagement_history"):
            if r.get(key):
                try:
                    r[key] = json.loads(r[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


def log_engagement(conn, audience_id: str, event: dict) -> bool:
    row = ms.get_row(conn, "audience_segments", audience_id)
    if not row:
        return False
    history = json.loads(row.get("engagement_history", "[]") or "[]")
    event["timestamp"] = _now()
    history.append(event)
    # Keep last 200 events
    if len(history) > 200:
        history = history[-200:]
    return ms.update_row(conn, "audience_segments", audience_id, {
        "engagement_history": json.dumps(history)
    })


# ── Voice Profiles ───────────────────────────────────────────────────────

def create_voice_profile(conn, name: str, description: str,
                         tone_attributes: dict, vocabulary: list[str],
                         avoid: list[str], examples: list[str]) -> dict:
    vid = ms.insert_row(conn, "voice_profiles", {
        "name": name,
        "description": description,
        "tone_attributes": json.dumps(tone_attributes),
        "vocabulary": json.dumps(vocabulary),
        "avoid": json.dumps(avoid),
        "examples": json.dumps(examples),
    })
    return ms.get_row(conn, "voice_profiles", vid)


def get_voice_profiles(conn) -> list[dict]:
    rows = ms.list_rows(conn, "voice_profiles")
    for r in rows:
        for key in ("tone_attributes", "vocabulary", "avoid", "examples"):
            if r.get(key):
                try:
                    r[key] = json.loads(r[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


def get_voice_prompt_fragment(conn, profile_name: str) -> str:
    """Return a prompt fragment enforcing the voice profile."""
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM voice_profiles WHERE name=?", [profile_name]
    ).fetchall()]
    if not rows:
        return ""
    vp = rows[0]
    tone = json.loads(vp.get("tone_attributes", "{}") or "{}")
    vocab = json.loads(vp.get("vocabulary", "[]") or "[]")
    avoid = json.loads(vp.get("avoid", "[]") or "[]")
    parts = [f"\n--- VOICE PROFILE: {vp['name']} ---"]
    if vp.get("description"):
        parts.append(f"Voice: {vp['description']}")
    if tone:
        parts.append(f"Tone attributes: {', '.join(f'{k}: {v}' for k, v in tone.items())}")
    if vocab:
        parts.append(f"Preferred vocabulary: {', '.join(vocab[:20])}")
    if avoid:
        parts.append(f"AVOID these words/phrases: {', '.join(avoid[:20])}")
    parts.append("--- END VOICE PROFILE ---\n")
    return "\n".join(parts)


# ── Campaign Intelligence (LLM-assisted) ────────────────────────────────

def build_campaign_context(conn, campaign_id: str) -> str:
    """Build an LLM context string from campaign state for strategy generation."""
    campaign = ms.get_row(conn, "campaigns", campaign_id)
    if not campaign:
        return ""
    calendar = get_calendar(conn, platform=None, limit=20)
    campaign_calendar = [c for c in calendar if c.get("campaign_id") == campaign_id]
    audiences = get_audiences(conn)

    parts = [
        f"Campaign: {campaign['name']}",
        f"Status: {campaign['status']}",
        f"Target: {campaign.get('target_audience', 'general')}",
        f"Goals: {campaign.get('goals', '[]')}",
        f"Scheduled content items: {len(campaign_calendar)}",
        f"Audience segments: {len(audiences)}",
    ]
    for aud in audiences:
        parts.append(f"  - {aud['name']}: {aud.get('description', '')}")
    return "\n".join(parts)
