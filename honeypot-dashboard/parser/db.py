"""SQLite connection helper and schema init."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "honeypot.db"


def get_db_path() -> str:
    return os.getenv("DATABASE_PATH") or str(DEFAULT_DB_PATH)


SCHEMA = """
CREATE TABLE IF NOT EXISTS attacks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT NOT NULL,
    src_ip       TEXT NOT NULL,
    country      TEXT,
    city         TEXT,
    latitude     REAL,
    longitude    REAL,
    username     TEXT,
    password     TEXT,
    event_type   TEXT,
    raw_command  TEXT
);

CREATE TABLE IF NOT EXISTS ip_cache (
    ip           TEXT PRIMARY KEY,
    country      TEXT,
    city         TEXT,
    latitude     REAL,
    longitude    REAL,
    last_lookup  TEXT
);

-- byte offset per log file so re-runs skip already-processed lines
CREATE TABLE IF NOT EXISTS parser_state (
    log_path     TEXT PRIMARY KEY,
    byte_offset  INTEGER NOT NULL DEFAULT 0,
    last_run     TEXT
);

CREATE INDEX IF NOT EXISTS idx_attacks_src_ip  ON attacks(src_ip);
CREATE INDEX IF NOT EXISTS idx_attacks_ts      ON attacks(timestamp);
CREATE INDEX IF NOT EXISTS idx_attacks_country ON attacks(country);
"""


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def insert_attack(conn, *, timestamp, src_ip, event_type, username=None,
                  password=None, raw_command=None, country=None, city=None,
                  latitude=None, longitude=None):
    conn.execute(
        """INSERT INTO attacks
               (timestamp, src_ip, country, city, latitude, longitude,
                username, password, event_type, raw_command)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (timestamp, src_ip, country, city, latitude, longitude,
         username, password, event_type, raw_command),
    )


def get_offset(conn, log_path):
    row = conn.execute(
        "SELECT byte_offset FROM parser_state WHERE log_path = ?", (log_path,)
    ).fetchone()
    return row["byte_offset"] if row else 0


def set_offset(conn, log_path, offset, last_run):
    conn.execute(
        """INSERT INTO parser_state (log_path, byte_offset, last_run)
           VALUES (?, ?, ?)
           ON CONFLICT(log_path) DO UPDATE SET
               byte_offset = excluded.byte_offset,
               last_run = excluded.last_run""",
        (log_path, offset, last_run),
    )


def cache_get(conn, ip):
    return conn.execute(
        "SELECT country, city, latitude, longitude FROM ip_cache WHERE ip = ?",
        (ip,),
    ).fetchone()


def cache_set(conn, ip, country, city, latitude, longitude, last_lookup):
    conn.execute(
        """INSERT INTO ip_cache (ip, country, city, latitude, longitude, last_lookup)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(ip) DO UPDATE SET
               country = excluded.country,
               city = excluded.city,
               latitude = excluded.latitude,
               longitude = excluded.longitude,
               last_lookup = excluded.last_lookup""",
        (ip, country, city, latitude, longitude, last_lookup),
    )


if __name__ == "__main__":
    init_db()
    print(f"Initialised honeypot database at {get_db_path()}")
