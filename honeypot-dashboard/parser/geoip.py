"""Week 2: GeoIP enrichment via ip-api.com, with ip_cache lookups first.

Always check the `ip_cache` table before calling the API (45 req/min limit).
STUB — implemented in Week 2.
"""

from __future__ import annotations


def get_geo(ip: str, conn) -> tuple:
    """Return (country, city, latitude, longitude) for an IP, cache-first."""
    raise NotImplementedError("Week 2: GeoIP enrichment not implemented yet.")
