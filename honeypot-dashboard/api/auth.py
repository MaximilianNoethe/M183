"""Auth for /api/* routes: HTTP Basic Auth (browser) or Bearer token (scripts)."""

import hmac
import os
from functools import wraps

from flask import Response, request


def _valid_basic(user, password):
    want_user = os.getenv("DASHBOARD_USER", "")
    want_pw = os.getenv("DASHBOARD_PASSWORD", "")
    return hmac.compare_digest(user, want_user) and hmac.compare_digest(password, want_pw)


def _valid_token(header):
    want = os.getenv("API_TOKEN", "")
    if not want or not header.startswith("Bearer "):
        return False
    return hmac.compare_digest(header[len("Bearer "):], want)


def requires_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        ok = _valid_token(request.headers.get("Authorization", "")) or (
            auth is not None and _valid_basic(auth.username or "", auth.password or "")
        )
        if not ok:
            return Response(
                "Authentication required", 401,
                {"WWW-Authenticate": 'Basic realm="honeypot"'},
            )
        return fn(*args, **kwargs)

    return wrapper
