"""HTTP Basic Auth for /api/* routes. Credentials from DASHBOARD_USER/PASSWORD."""

import hmac
import os
from functools import wraps

from flask import Response, request


def _valid(user, password):
    want_user = os.getenv("DASHBOARD_USER", "")
    want_pw = os.getenv("DASHBOARD_PASSWORD", "")
    return hmac.compare_digest(user, want_user) and hmac.compare_digest(password, want_pw)


def requires_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not _valid(auth.username or "", auth.password or ""):
            return Response(
                "Authentication required", 401,
                {"WWW-Authenticate": 'Basic realm="honeypot"'},
            )
        return fn(*args, **kwargs)

    return wrapper
