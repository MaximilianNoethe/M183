"""Analysis endpoints: HIBP password check, botnet waves, top attacker commands."""

from flask import Blueprint, jsonify

from analysis import botnet_detector, hibp_check
from api.auth import requires_auth
from parser import db

bp = Blueprint("analysis", __name__)

_hibp_cache = {}


@bp.route("/api/analysis/passwords")
@requires_auth
def passwords():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT password AS value, COUNT(*) AS count FROM attacks
               WHERE password IS NOT NULL AND password != ''
               GROUP BY password ORDER BY count DESC LIMIT 15"""
        ).fetchall()
    finally:
        conn.close()
    result = []
    for r in rows:
        pw = r["value"]
        if pw not in _hibp_cache:
            try:
                _hibp_cache[pw] = hibp_check.check_password(pw)
            except Exception:
                _hibp_cache[pw] = None
        result.append({"value": pw, "count": r["count"], "pwned": _hibp_cache[pw]})
    return jsonify(result)


@bp.route("/api/analysis/botnet")
@requires_auth
def botnet():
    conn = db.get_connection()
    try:
        waves = botnet_detector.detect_botnets(conn)
    finally:
        conn.close()
    return jsonify(waves)


@bp.route("/api/analysis/commands")
@requires_auth
def commands():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT raw_command AS value, COUNT(*) AS count FROM attacks
               WHERE raw_command IS NOT NULL AND raw_command != ''
               GROUP BY raw_command ORDER BY count DESC LIMIT 15"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/api/analysis/downloads")
@requires_auth
def downloads():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT raw_command AS value, COUNT(*) AS count FROM attacks
               WHERE raw_command IS NOT NULL AND raw_command != ''
                 AND (raw_command LIKE '%wget%' OR raw_command LIKE '%curl%'
                      OR raw_command LIKE '%http%'
                      OR event_type = 'cowrie.session.file_download')
               GROUP BY raw_command ORDER BY count DESC LIMIT 15"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/api/analysis/timeline")
@requires_auth
def timeline():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT substr(timestamp, 1, 10) AS day, COUNT(*) AS count,
                      COUNT(DISTINCT src_ip) AS ips
               FROM attacks GROUP BY day ORDER BY day"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/api/analysis/attackers")
@requires_auth
def attackers():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT src_ip, country, asn, COUNT(*) AS count,
                      MIN(timestamp) AS first_seen, MAX(timestamp) AS last_seen
               FROM attacks
               GROUP BY src_ip ORDER BY count DESC LIMIT 15"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/api/analysis/providers")
@requires_auth
def providers():
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT asn AS value, COUNT(*) AS count,
                      COUNT(DISTINCT src_ip) AS ips FROM attacks
               WHERE asn IS NOT NULL AND asn != ''
               GROUP BY asn ORDER BY count DESC LIMIT 10"""
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])
