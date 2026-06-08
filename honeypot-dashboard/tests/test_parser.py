"""Tests for parser/db.py (Week 1).

Week 2+ parser tests are added when log_parser/geoip are implemented.
"""

import sqlite3

import pytest

from parser import db


@pytest.fixture
def temp_db(tmp_path):
    """An initialised honeypot DB in a temp file. Yields the path."""
    path = str(tmp_path / "test_honeypot.db")
    db.init_db(path)
    return path


def test_init_db_creates_tables(temp_db):
    conn = db.get_connection(temp_db)
    try:
        names = {
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    finally:
        conn.close()
    assert {"attacks", "ip_cache", "parser_state"} <= names


def test_init_db_creates_indexes(temp_db):
    conn = db.get_connection(temp_db)
    try:
        idx = {
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
        }
    finally:
        conn.close()
    assert {
        "idx_attacks_src_ip",
        "idx_attacks_ts",
        "idx_attacks_country",
    } <= idx


def test_init_db_is_idempotent(temp_db):
    # Running init twice must not raise.
    db.init_db(temp_db)
    db.init_db(temp_db)


def test_connection_row_factory(temp_db):
    conn = db.get_connection(temp_db)
    try:
        conn.execute(
            "INSERT INTO attacks (timestamp, src_ip, username) VALUES (?, ?, ?)",
            ("2026-06-08T00:00:00Z", "192.0.2.1", "root"),
        )
        conn.commit()
        row = conn.execute(
            "SELECT src_ip, username FROM attacks WHERE src_ip = ?", ("192.0.2.1",)
        ).fetchone()
    finally:
        conn.close()
    # sqlite3.Row supports name-based access.
    assert row["src_ip"] == "192.0.2.1"
    assert row["username"] == "root"


def test_attacks_schema_columns(temp_db):
    conn = db.get_connection(temp_db)
    try:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(attacks)")}
    finally:
        conn.close()
    expected = {
        "id", "timestamp", "src_ip", "country", "city", "latitude",
        "longitude", "username", "password", "event_type", "raw_command",
    }
    assert cols == expected
