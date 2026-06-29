"""Security headers (every response) + rate limiting + JSON errors on the API."""

from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' cdn.jsdelivr.net unpkg.com; "
        "style-src 'self' unpkg.com; "
        "img-src 'self' data: *.tile.openstreetmap.org *.basemaps.cartocdn.com"
    ),
}


def register_middleware(app):
    Limiter(get_remote_address, app=app, default_limits=["60 per minute"])

    @app.after_request
    def set_headers(resp):
        for key, value in HEADERS.items():
            resp.headers[key] = value
        return resp

    def json_error(status, message):
        return jsonify(error=message), status

    app.register_error_handler(404, lambda e: json_error(404, "not found"))
    app.register_error_handler(429, lambda e: json_error(429, "rate limit exceeded"))
    app.register_error_handler(500, lambda e: json_error(500, "internal server error"))
