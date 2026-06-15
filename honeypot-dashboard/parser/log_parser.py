"""Read new cowrie.json lines, enrich via GeoIP, store in SQLite."""

import json
import os
from datetime import datetime, timezone

from parser import db, geoip

TRACKED = {
    "cowrie.login.failed",
    "cowrie.login.success",
    "cowrie.command.input",
    "cowrie.session.connect",
}


def _log_path():
    return os.getenv("COWRIE_LOG_PATH", "/opt/honeypot/cowrie/var/log/cowrie/cowrie.json")


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
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("eventid") not in TRACKED:
                    continue
                ip = event.get("src_ip")
                if not ip:
                    continue
                country, city, lat, lon = geoip.get_geo(ip, conn)
                db.insert_attack(
                    conn,
                    timestamp=event.get("timestamp"),
                    src_ip=ip,
                    event_type=event.get("eventid"),
                    username=event.get("username"),
                    password=event.get("password"),
                    raw_command=event.get("input"),
                    country=country,
                    city=city,
                    latitude=lat,
                    longitude=lon,
                )
                inserted += 1
            new_offset = fh.tell()
        db.set_offset(conn, log_path, new_offset, datetime.now(timezone.utc).isoformat())
        conn.commit()
    finally:
        conn.close()
    return inserted


if __name__ == "__main__":
    print(f"Inserted {run()} new attack rows.")
