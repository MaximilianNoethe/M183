"""GeoIP enrichment via ip-api.com. Always checks ip_cache before calling out."""

import os
import time
from datetime import datetime, timezone

import requests

from parser import db

ENDPOINT = os.getenv("GEOIP_ENDPOINT", "http://ip-api.com/json/")

_last_call = 0.0  # throttle live calls to stay under ip-api's 45 req/min


def _lookup(ip):
    global _last_call
    wait = 1.4 - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()
    try:
        data = requests.get(ENDPOINT + ip, timeout=5).json()
    except requests.RequestException:
        return (None, None, None, None)
    if data.get("status") != "success":
        return (None, None, None, None)
    return (data.get("country"), data.get("city"), data.get("lat"), data.get("lon"))


def get_geo(ip, conn):
    cached = db.cache_get(conn, ip)
    if cached:
        return (cached["country"], cached["city"], cached["latitude"], cached["longitude"])
    country, city, lat, lon = _lookup(ip)
    now = datetime.now(timezone.utc).isoformat()
    db.cache_set(conn, ip, country, city, lat, lon, now)
    return (country, city, lat, lon)
