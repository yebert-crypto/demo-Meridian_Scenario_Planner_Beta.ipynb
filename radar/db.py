import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from radar.models import Client, Signal, SignalType

import os
_data_dir = Path(os.getenv("DATA_DIR", Path(__file__).parent.parent / "data"))
DB_PATH = _data_dir / "meridian.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ticker TEXT,
                domain TEXT,
                industry TEXT,
                relationship_partner TEXT,
                is_active INTEGER DEFAULT 1,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                client_name TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                headline TEXT NOT NULL,
                summary TEXT NOT NULL,
                source_url TEXT,
                source_name TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                published_at TEXT,
                is_read INTEGER DEFAULT 0,
                is_dismissed INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 4,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            );

            CREATE INDEX IF NOT EXISTS idx_signals_client ON signals(client_id);
            CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
            CREATE INDEX IF NOT EXISTS idx_signals_detected ON signals(detected_at DESC);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_signals_dedup
                ON signals(client_id, signal_type, source_url);
        """)


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# --- Clients ---

def upsert_client(c: Client) -> int:
    with _conn() as conn:
        cur = conn.execute("""
            INSERT INTO clients (name, ticker, domain, industry, relationship_partner, is_active, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
        """, (c.name, c.ticker, c.domain, c.industry, c.relationship_partner, int(c.is_active), c.notes))
        if cur.lastrowid:
            return cur.lastrowid
        row = conn.execute("SELECT id FROM clients WHERE name = ?", (c.name,)).fetchone()
        return row["id"]


def get_clients(active_only: bool = True) -> list[Client]:
    with _conn() as conn:
        query = "SELECT * FROM clients"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        rows = conn.execute(query).fetchall()
    return [_row_to_client(r) for r in rows]


def _row_to_client(r) -> Client:
    return Client(
        id=r["id"], name=r["name"], ticker=r["ticker"], domain=r["domain"],
        industry=r["industry"], relationship_partner=r["relationship_partner"],
        is_active=bool(r["is_active"]), notes=r["notes"],
    )


# --- Signals ---

def insert_signal(s: Signal) -> Optional[int]:
    """Returns new signal id, or None if duplicate."""
    with _conn() as conn:
        try:
            cur = conn.execute("""
                INSERT INTO signals
                    (client_id, client_name, signal_type, headline, summary,
                     source_url, source_name, detected_at, published_at, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s.client_id, s.client_name, s.signal_type.value, s.headline,
                s.summary, s.source_url, s.source_name,
                s.detected_at.isoformat(), s.published_at.isoformat() if s.published_at else None,
                s.priority,
            ))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None  # duplicate


def get_signals(
    client_id: Optional[int] = None,
    signal_types: Optional[list[SignalType]] = None,
    include_dismissed: bool = False,
    limit: int = 200,
) -> list[Signal]:
    clauses, params = [], []
    if client_id:
        clauses.append("client_id = ?")
        params.append(client_id)
    if signal_types:
        placeholders = ",".join("?" * len(signal_types))
        clauses.append(f"signal_type IN ({placeholders})")
        params.extend(t.value for t in signal_types)
    if not include_dismissed:
        clauses.append("is_dismissed = 0")

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    query = f"SELECT * FROM signals {where} ORDER BY detected_at DESC LIMIT ?"
    params.append(limit)

    with _conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_signal(r) for r in rows]


def mark_read(signal_id: int):
    with _conn() as conn:
        conn.execute("UPDATE signals SET is_read = 1 WHERE id = ?", (signal_id,))


def mark_dismissed(signal_id: int):
    with _conn() as conn:
        conn.execute("UPDATE signals SET is_dismissed = 1 WHERE id = ?", (signal_id,))


def get_signal_counts() -> dict:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT signal_type, COUNT(*) as cnt
            FROM signals WHERE is_dismissed = 0
            GROUP BY signal_type
        """).fetchall()
    return {r["signal_type"]: r["cnt"] for r in rows}


def get_unread_count() -> int:
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM signals WHERE is_read = 0 AND is_dismissed = 0"
        ).fetchone()
    return row["cnt"]


def _row_to_signal(r) -> Signal:
    s = Signal(
        id=r["id"],
        client_id=r["client_id"],
        client_name=r["client_name"],
        signal_type=SignalType(r["signal_type"]),
        headline=r["headline"],
        summary=r["summary"],
        source_url=r["source_url"],
        source_name=r["source_name"],
        detected_at=datetime.fromisoformat(r["detected_at"]),
        published_at=datetime.fromisoformat(r["published_at"]) if r["published_at"] else None,
        is_read=bool(r["is_read"]),
        is_dismissed=bool(r["is_dismissed"]),
    )
    return s
