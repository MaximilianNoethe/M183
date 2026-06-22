"""Security headers (every response) + rate limiting on the API."""

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
