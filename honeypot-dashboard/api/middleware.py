"""Week 3: security headers, rate limiting, CORS, request logging.

Security headers (set via after_request) — see CLAUDE.md:
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Content-Security-Policy: default-src 'self'; ...
STUB — Week 3.
"""

from __future__ import annotations


def register_middleware(app) -> None:
    """Attach security headers, rate limiter, CORS, and logging to the app."""
    raise NotImplementedError("Week 3: middleware not implemented yet.")
