"""CSV export of all attacks (auth-protected)."""

import csv
import io

from flask import Blueprint, Response, jsonify

from api.auth import requires_auth
from parser import db

bp = Blueprint("export", __name__)

COLUMNS = ["timestamp", "src_ip", "country", "city", "latitude", "longitude",
           "asn", "org", "username", "password", "event_type", "raw_command"]


@bp.route("/api/export/csv")
@requires_auth
def export_csv():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT " + ", ".join(COLUMNS) + " FROM attacks ORDER BY timestamp"
        ).fetchall()
    finally:
        conn.close()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(COLUMNS)
    for r in rows:
        writer.writerow([r[c] for c in COLUMNS])
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=honeypot_attacks.csv"},
    )


@bp.route("/api/export/json")
@requires_auth
def export_json():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT " + ", ".join(COLUMNS) + " FROM attacks ORDER BY timestamp"
        ).fetchall()
    finally:
        conn.close()
    resp = jsonify([dict(r) for r in rows])
    resp.headers["Content-Disposition"] = "attachment; filename=honeypot_attacks.json"
    return resp
