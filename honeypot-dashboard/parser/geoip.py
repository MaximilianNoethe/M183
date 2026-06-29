"""GeoIP enrichment via ip-api.com. Always checks ip_cache before calling out."""

import os
import time
from datetime import datetime, timezone

import requests

from parser import db

ENDPOINT = os.getenv("GEOIP_ENDPOINT", "http://ip-api.com/json/")
BATCH_ENDPOINT = os.getenv("GEOIP_BATCH_ENDPOINT", "http://ip-api.com/batch")

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
        return (None, None, None, None, None, None)
    if data.get("status") != "success":
        return (None, None, None, None, None, None)
    return (data.get("country"), data.get("city"), data.get("lat"), data.get("lon"),
            data.get("as"), data.get("org"))


def lookup_batch(ips):
    """Resolve up to 100 IPs per ip-api batch request. Returns {ip: geo dict}."""
    out = {}
    for i in range(0, len(ips), 100):
        chunk = ips[i:i + 100]
        try:
            data = requests.post(BATCH_ENDPOINT, json=chunk, timeout=10).json()
        except requests.RequestException:
            continue
        for entry in data:
            if entry.get("status") != "success":
                continue
            out[entry.get("query")] = {
                "country": entry.get("country"), "city": entry.get("city"),
                "latitude": entry.get("lat"), "longitude": entry.get("lon"),
                "asn": entry.get("as"), "org": entry.get("org"),
            }
        if i + 100 < len(ips):
            time.sleep(1.4)  # batch endpoint allows ~15 req/min
    return out


def warm_cache(conn, ips):
    """Batch-resolve all not-yet-cached IPs into ip_cache before per-row enrichment."""
    missing = [ip for ip in dict.fromkeys(ips) if not db.cache_get(conn, ip)]
    if not missing:
        return 0
    found = lookup_batch(missing)
    now = datetime.now(timezone.utc).isoformat()
    for ip, geo in found.items():
        db.cache_set(conn, ip, geo["country"], geo["city"], geo["latitude"],
                     geo["longitude"], now, asn=geo["asn"], org=geo["org"])
    return len(found)


def get_geo(ip, conn):
    cached = db.cache_get(conn, ip)
    if cached:
        return {"country": cached["country"], "city": cached["city"],
                "latitude": cached["latitude"], "longitude": cached["longitude"],
                "asn": cached["asn"], "org": cached["org"]}
    country, city, lat, lon, asn, org = _lookup(ip)
    now = datetime.now(timezone.utc).isoformat()
    db.cache_set(conn, ip, country, city, lat, lon, now, asn=asn, org=org)
    return {"country": country, "city": city, "latitude": lat, "longitude": lon,
            "asn": asn, "org": org}
