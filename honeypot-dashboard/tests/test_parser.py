"""Tests for parser/db.py (Week 1) and the log parser + geoip (Week 2)."""

from pathlib import Path

import pytest

from parser import db, geoip, log_parser

FIXTURE = str(Path(__file__).parent / "fixtures" / "sample_cowrie.json")


@pytest.fixture
def temp_db(tmp_path):
    """An initialised honeypot DB in a temp file. Yields the path."""
    path = str(tmp_path / "test_honeypot.db")
    db.init_db(path)
    return path


@pytest.fixture
def fake_geo(monkeypatch):
    """Stub out GeoIP so parser tests never hit the network."""
    monkeypatch.setattr(
        geoip, "get_geo", lambda ip, conn: ("Testland", "Test City", 1.0, 2.0)
    )


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


def _count(db_path):
    conn = db.get_connection(db_path)
    try:
        return conn.execute("SELECT COUNT(*) AS c FROM attacks").fetchone()["c"]
    finally:
        conn.close()


def test_run_inserts_tracked_events(temp_db, fake_geo):
    n = log_parser.run(log_path=FIXTURE, db_path=temp_db)
    assert n == 20
    assert _count(temp_db) == 20


def test_run_is_idempotent(temp_db, fake_geo):
    log_parser.run(log_path=FIXTURE, db_path=temp_db)
    second = log_parser.run(log_path=FIXTURE, db_path=temp_db)
    assert second == 0
    assert _count(temp_db) == 20


def test_login_credentials_extracted(temp_db, fake_geo):
    log_parser.run(log_path=FIXTURE, db_path=temp_db)
    conn = db.get_connection(temp_db)
    try:
        row = conn.execute(
            "SELECT username, password, event_type, country FROM attacks WHERE src_ip = ?",
            ("192.0.2.1",),
        ).fetchone()
    finally:
        conn.close()
    assert row["username"] == "root"
    assert row["password"] == "123456"
    assert row["event_type"] == "cowrie.login.failed"
    assert row["country"] == "Testland"


def test_command_input_extracted(temp_db, fake_geo):
    log_parser.run(log_path=FIXTURE, db_path=temp_db)
    conn = db.get_connection(temp_db)
    try:
        row = conn.execute(
            "SELECT raw_command, event_type FROM attacks WHERE src_ip = ?",
            ("192.0.2.18",),
        ).fetchone()
    finally:
        conn.close()
    assert row["raw_command"] == "uname -a; cat /etc/passwd"
    assert row["event_type"] == "cowrie.command.input"


def test_missing_log_returns_zero(temp_db, fake_geo):
    assert log_parser.run(log_path="/no/such/cowrie.json", db_path=temp_db) == 0


def test_geoip_uses_cache_first(temp_db, monkeypatch):
    conn = db.get_connection(temp_db)
    try:
        db.cache_set(conn, "192.0.2.50", "Cacheland", "Cache City", 5.0, 6.0,
                     "2026-06-15T00:00:00Z")
        conn.commit()
        monkeypatch.setattr(geoip, "_lookup",
                            lambda ip: pytest.fail("API must not be called when cached"))
        geo = geoip.get_geo("192.0.2.50", conn)
    finally:
        conn.close()
    assert geo == ("Cacheland", "Cache City", 5.0, 6.0)
