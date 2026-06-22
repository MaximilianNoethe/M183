"""HaveIBeenPwned k-Anonymity check: only the first 5 SHA1 chars leave the server."""

import hashlib

import requests

API = "https://api.pwnedpasswords.com/range/"


def check_password(password):
    if not password:
        return 0
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    resp = requests.get(API + prefix, timeout=5)
    resp.raise_for_status()
    for line in resp.text.splitlines():
        found, _, count = line.partition(":")
        if found == suffix:
            return int(count)
    return 0
