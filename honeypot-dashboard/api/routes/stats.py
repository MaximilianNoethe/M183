"""Aggregated stats, recent feed, and search."""

from flask import Blueprint, jsonify, request

from api.auth import requires_auth
from parser import db

bp = Blueprint("stats", __name__)


@bp.route("/api/stats")
@requires_auth
def stats():
    conn = db.get_connection()
    try:
        totals = conn.execute(
            """SELECT COUNT(*) AS total,
                      COUNT(DISTINCT src_ip) AS unique_ips,
                      COUNT(DISTINCT country) AS countries,
                      MIN(timestamp) AS first_seen,
                      MAX(timestamp) AS last_seen
               FROM attacks"""
        ).fetchone()
        top_usernames = conn.execute(
            """SELECT username AS value, COUNT(*) AS count FROM attacks
               WHERE username IS NOT NULL AND username != ''
               GROUP BY username ORDER BY count DESC LIMIT 10"""
        ).fetchall()
        top_passwords = conn.execute(
            """SELECT password AS value, COUNT(*) AS count FROM attacks
               WHERE password IS NOT NULL AND password != ''
               GROUP BY password ORDER BY count DESC LIMIT 10"""
        ).fetchall()
        top_countries = conn.execute(
            """SELECT country AS value, COUNT(*) AS count FROM attacks
               WHERE country IS NOT NULL AND country != ''
               GROUP BY country ORDER BY count DESC LIMIT 10"""
        ).fetchall()
        per_hour = conn.execute(
            """SELECT substr(timestamp, 1, 13) AS hour, COUNT(*) AS count
               FROM attacks GROUP BY hour ORDER BY hour"""
        ).fetchall()
    finally:
        conn.close()
    per_hour = [dict(r) for r in per_hour]
    busiest = max(per_hour, key=lambda r: r["count"], default=None)
    return jsonify({
        "total": totals["total"],
        "unique_ips": totals["unique_ips"],
        "countries": totals["countries"],
        "first_seen": totals["first_seen"],
        "last_seen": totals["last_seen"],
        "busiest_hour": busiest,
        "top_usernames": [dict(r) for r in top_usernames],
        "top_passwords": [dict(r) for r in top_passwords],
        "top_countries": [dict(r) for r in top_countries],
        "per_hour": per_hour,
    })


@bp.route("/api/recent")
@requires_auth
def recent():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT timestamp, src_ip, country, username, password,
                      event_type, raw_command
               FROM attacks ORDER BY timestamp DESC LIMIT 50"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/api/search")
@requires_auth
def search():
    available = {
        "ip": "src_ip LIKE ?",
        "country": "country LIKE ?",
        "username": "username LIKE ?",
    }
    clauses, params = [], []
    for arg, clause in available.items():
        value = request.args.get(arg, "").strip()[:64]  # cap to keep queries bounded
        if value:
            clauses.append(clause)
            params.append(f"%{value}%")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT timestamp, src_ip, country, username, password, event_type "
            "FROM attacks" + where + " ORDER BY timestamp DESC LIMIT 100",
            params,
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])
