"""Unauthenticated health check for monitoring/uptime probes."""

from flask import Blueprint, jsonify

from parser import db

bp = Blueprint("health", __name__)


@bp.route("/api/health")
def health():
    try:
        conn = db.get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS total, MAX(timestamp) AS last FROM attacks"
            ).fetchone()
        finally:
            conn.close()
    except Exception:
        return jsonify(status="error", database=False), 503
    return jsonify(
        status="ok",
        database=True,
        total_attacks=row["total"],
        last_attack=row["last"],
    )
