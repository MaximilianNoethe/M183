import base64

import pytest

from api.app import create_app
from parser import db

AUTH = {"Authorization": "Basic " + base64.b64encode(b"tester:secret").decode()}


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "api.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("DASHBOARD_USER", "tester")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    db.init_db(str(db_path))
    conn = db.get_connection(str(db_path))
    db.insert_attack(conn, timestamp="2026-06-22T11:00:00Z", src_ip="192.0.2.1",
                     event_type="cowrie.login.failed", username="root",
                     password="123456", country="Testland", city="Testville",
                     latitude=1.0, longitude=2.0)
    db.insert_attack(conn, timestamp="2026-06-22T12:00:00Z", src_ip="192.0.2.2",
                     event_type="cowrie.command.input", raw_command="uname -a",
                     country="Testland", latitude=3.0, longitude=4.0)
    conn.commit()
    conn.close()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_requires_auth(client):
    assert client.get("/api/stats").status_code == 401


def test_stats(client):
    data = client.get("/api/stats", headers=AUTH).get_json()
    assert data["total"] == 2
    assert data["unique_ips"] == 2
    assert {"value": "root", "count": 1} in data["top_usernames"]


def test_attacks_map(client):
    rows = client.get("/api/attacks", headers=AUTH).get_json()
    assert len(rows) == 2
    assert all(r["latitude"] is not None for r in rows)


def test_recent_is_sorted(client):
    rows = client.get("/api/recent", headers=AUTH).get_json()
    assert rows[0]["timestamp"] >= rows[-1]["timestamp"]


def test_search_filters(client):
    rows = client.get("/api/search?username=root", headers=AUTH).get_json()
    assert len(rows) == 1 and rows[0]["src_ip"] == "192.0.2.1"


def test_search_injection_safe(client):
    rows = client.get("/api/search?username=' OR '1'='1", headers=AUTH).get_json()
    assert rows == []


def test_security_headers(client):
    resp = client.get("/api/stats", headers=AUTH)
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
