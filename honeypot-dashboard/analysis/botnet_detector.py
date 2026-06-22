"""Detect coordinated attack waves: many distinct IPs hitting in the same minute."""


def detect_botnets(conn, min_ips=5, limit=20):
    rows = conn.execute(
        """SELECT substr(timestamp, 1, 16) AS window,
                  COUNT(DISTINCT src_ip) AS ip_count,
                  COUNT(*) AS attempts
           FROM attacks
           GROUP BY window
           HAVING ip_count >= ?
           ORDER BY ip_count DESC, attempts DESC
           LIMIT ?""",
        (min_ips, limit),
    ).fetchall()
    return [dict(r) for r in rows]
