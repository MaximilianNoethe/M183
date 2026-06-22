"""Map data: one point per attacker IP with geo + hit count."""

from flask import Blueprint, jsonify

from api.auth import requires_auth
from parser import db

bp = Blueprint("attacks", __name__)


@bp.route("/api/attacks")
@requires_auth
def attacks():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT src_ip, country, city, latitude, longitude, COUNT(*) AS count
               FROM attacks
               WHERE latitude IS NOT NULL
               GROUP BY src_ip
               ORDER BY count DESC"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])
