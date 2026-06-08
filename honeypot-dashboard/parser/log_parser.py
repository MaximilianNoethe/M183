"""Week 2: read cowrie.json, deduplicate, enrich with GeoIP, insert into SQLite.

Reads new lines since the last byte offset (stored in parser_state), parses each
JSON event, keeps security-relevant fields, and inserts into `attacks`. Run via
`python3 -m parser.log_parser` (systemd timer / cron every 5 min).

STUB — implemented in Week 2.
"""

from __future__ import annotations


def run() -> int:
    """Parse new Cowrie log lines into the DB. Returns count of inserted rows."""
    raise NotImplementedError("Week 2: log parser not implemented yet.")


if __name__ == "__main__":
    run()
