"""Read new cowrie.json lines, enrich via GeoIP, store in SQLite."""

import glob
import json
import os
from datetime import datetime, timezone

from parser import db, geoip

TRACKED = {
    "cowrie.login.failed",
    "cowrie.login.success",
    "cowrie.command.input",
    "cowrie.session.connect",
    "cowrie.session.file_download",
}


def _log_path():
    return os.getenv("COWRIE_LOG_PATH", "/opt/honeypot/cowrie/var/log/cowrie/cowrie.json")


def _log_files():
    # current log plus daily-rotated files (cowrie.json.2026-06-21 …), oldest first
    main = _log_path()
    return sorted(glob.glob(main + ".*")) + [main]


def run(log_path=None, db_path=None):
    log_path = log_path or _log_path()
    db.init_db(db_path)
    if not os.path.exists(log_path):
        return 0

    conn = db.get_connection(db_path)
    inserted = 0
    try:
        offset = db.get_offset(conn, log_path)
        with open(log_path, "r", encoding="utf-8") as fh:
            fh.seek(offset)
            lines = fh.readlines()
            new_offset = fh.tell()

        events = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("eventid") not in TRACKED or not event.get("src_ip"):
                continue
            events.append(event)

        # one batch GeoIP call warms the cache for every new IP up front
        geoip.warm_cache(conn, [e["src_ip"] for e in events])

        for event in events:
            ip = event["src_ip"]
            geo = geoip.get_geo(ip, conn)
            db.insert_attack(
                conn,
                timestamp=event.get("timestamp"),
                src_ip=ip,
                event_type=event.get("eventid"),
                username=event.get("username"),
                password=event.get("password"),
                raw_command=event.get("input") or event.get("url"),
                country=geo["country"],
                city=geo["city"],
                latitude=geo["latitude"],
                longitude=geo["longitude"],
                asn=geo["asn"],
                org=geo["org"],
            )
            inserted += 1
        db.set_offset(conn, log_path, new_offset, datetime.now(timezone.utc).isoformat())
        conn.commit()
    finally:
        conn.close()
    return inserted


def run_all(db_path=None):
    return sum(run(log_path=path, db_path=db_path) for path in _log_files())


if __name__ == "__main__":
    print(f"Inserted {run_all()} new attack rows.")
