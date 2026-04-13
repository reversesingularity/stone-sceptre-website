"""
Persistent Memory Store — SQLite-backed agent memory for Agent 13.
Provides campaign state, SEO tracking, audience segments, content calendar,
voice profiles, and general learning memory across sessions.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent.parent / "LOGS" / "agent13_memory.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create all tables if they don't exist."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        target_audience TEXT,
        start_date TEXT,
        end_date TEXT,
        goals TEXT,
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS content_calendar (
        id TEXT PRIMARY KEY,
        campaign_id TEXT REFERENCES campaigns(id),
        platform TEXT,
        content_type TEXT,
        scheduled_date TEXT,
        status TEXT DEFAULT 'draft',
        content TEXT,
        hashtags TEXT,
        seo_keywords TEXT,
        book_number INTEGER,
        chapter_number INTEGER,
        created_at TEXT,
        posted_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS seo_keywords (
        id TEXT PRIMARY KEY,
        keyword TEXT NOT NULL UNIQUE,
        current_rank INTEGER,
        previous_rank INTEGER,
        trend TEXT DEFAULT 'new',
        search_volume INTEGER,
        difficulty REAL,
        last_checked TEXT,
        history TEXT DEFAULT '[]',
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS topic_authority (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL UNIQUE,
        authority_score REAL DEFAULT 0.0,
        related_keywords TEXT DEFAULT '[]',
        content_count INTEGER DEFAULT 0,
        internal_links TEXT DEFAULT '[]',
        last_updated TEXT,
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS audience_segments (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        demographics TEXT DEFAULT '{}',
        interests TEXT DEFAULT '[]',
        content_preferences TEXT DEFAULT '{}',
        engagement_history TEXT DEFAULT '[]',
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS voice_profiles (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        tone_attributes TEXT DEFAULT '{}',
        vocabulary TEXT DEFAULT '[]',
        avoid TEXT DEFAULT '[]',
        examples TEXT DEFAULT '[]',
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS social_queue (
        id TEXT PRIMARY KEY,
        campaign_id TEXT,
        platform TEXT NOT NULL,
        content TEXT NOT NULL,
        media_urls TEXT DEFAULT '[]',
        hashtags TEXT DEFAULT '[]',
        scheduled_at TEXT,
        status TEXT DEFAULT 'queued',
        posted_at TEXT,
        error TEXT,
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS scrape_results (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        source_type TEXT,
        query TEXT,
        data TEXT DEFAULT '{}',
        scraped_at TEXT,
        created_at TEXT,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS memory (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        metadata TEXT DEFAULT '{}',
        created_at TEXT,
        updated_at TEXT,
        UNIQUE(category, key)
    );
    """)
    conn.commit()


# ── Generic CRUD helpers ─────────────────────────────────────────────────

def insert_row(conn: sqlite3.Connection, table: str, data: dict) -> str:
    """Insert a row and return its id."""
    if "id" not in data:
        data["id"] = _uid()
    if "created_at" not in data:
        data["created_at"] = _now()
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    return data["id"]


def update_row(conn: sqlite3.Connection, table: str, row_id: str, updates: dict) -> bool:
    updates["updated_at"] = _now()
    sets = ", ".join(f"{k}=?" for k in updates)
    cur = conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", [*updates.values(), row_id])
    conn.commit()
    return cur.rowcount > 0


def get_row(conn: sqlite3.Connection, table: str, row_id: str) -> Optional[dict]:
    cur = conn.execute(f"SELECT * FROM {table} WHERE id=?", [row_id])
    row = cur.fetchone()
    return dict(row) if row else None


def list_rows(conn: sqlite3.Connection, table: str, where: str = "", params: tuple = (), limit: int = 100) -> list[dict]:
    q = f"SELECT * FROM {table}"
    if where:
        q += f" WHERE {where}"
    q += f" LIMIT {limit}"
    return [dict(r) for r in conn.execute(q, params).fetchall()]


def delete_row(conn: sqlite3.Connection, table: str, row_id: str) -> bool:
    cur = conn.execute(f"DELETE FROM {table} WHERE id=?", [row_id])
    conn.commit()
    return cur.rowcount > 0


# ── Memory-specific helpers ──────────────────────────────────────────────

def remember(conn: sqlite3.Connection, category: str, key: str, value: Any, metadata: dict | None = None) -> str:
    """Store or update a memory entry."""
    now = _now()
    meta_json = json.dumps(metadata or {})
    val_str = json.dumps(value) if not isinstance(value, str) else value
    conn.execute(
        "INSERT INTO memory (id, category, key, value, metadata, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(category, key) DO UPDATE SET value=?, metadata=?, updated_at=?",
        [_uid(), category, key, val_str, meta_json, now, now, val_str, meta_json, now],
    )
    conn.commit()
    return key


def recall(conn: sqlite3.Connection, category: str, key: str | None = None) -> Any:
    """Recall a specific memory or all memories in a category."""
    if key:
        cur = conn.execute("SELECT value FROM memory WHERE category=? AND key=?", [category, key])
        row = cur.fetchone()
        if not row:
            return None
        try:
            return json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            return row["value"]
    else:
        rows = conn.execute("SELECT key, value FROM memory WHERE category=?", [category]).fetchall()
        result = {}
        for r in rows:
            try:
                result[r["key"]] = json.loads(r["value"])
            except (json.JSONDecodeError, TypeError):
                result[r["key"]] = r["value"]
        return result
