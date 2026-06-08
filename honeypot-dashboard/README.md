# 🍯 Honeypot + Live Attack Map
 
> Personal security research project — real SSH/Telnet honeypot collecting genuine attack data from the internet, visualized on a live world map dashboard.
 
**Stack:** Python · Flask · Cowrie · SQLite · Leaflet.js · Chart.js  
**Server:** Hetzner CX22 · Ubuntu 22.04  
**Cost:** ~4 CHF/month (Free trial used)
 
---
 
## Quick Start
 
```bash
git clone https://github.com/YOUR_USERNAME/honeypot-dashboard
cd honeypot-dashboard
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit with your values
python3 -m api.app          # dashboard on http://localhost:8080
```
 
For full VPS deployment see [`scripts/setup_server.sh`](scripts/setup_server.sh).
 
---
 
## Architecture
 
```
Internet (real attackers)
        │
        ▼
  [Cowrie Honeypot]  ←── SSH Port 22 / Telnet Port 23
  JSON logs every hit
        │
        ▼
  [log_parser.py]    ←── runs every 5 min via cron
  GeoIP enrichment → SQLite DB
        │
        ▼
  [Flask API]        ←── /api/attacks  /api/stats  /api/recent
        │
        ▼
  [Dashboard]        ←── Leaflet world map + Chart.js stats
```
 
---
 
## Project Status
 
| Week | Topic | Status |
|------|-------|--------|
| 1 | VPS · Cowrie · Firewall | ⬜ Not started |
| 2 | Log Parser · SQLite · GeoIP | ⬜ Not started |
| 3 | Flask API · Auth · Security Headers | ⬜ Not started |
| 4 | Dashboard · World Map · Charts | ⬜ Not started |
| 5 | Analysis · HIBP · Botnet Detection | ⬜ Not started |
| 6 | HTTPS · Hardening · Documentation | ⬜ Not started |
  
---
 
## Journal
 
> This journal tracks what was planned vs. what actually happened each week.
> Updated at the end of every session.
 
---
 
### Week 1 — Infrastructure & Honeypot Sensor
 
**Period:** `08.06.2026`  
**Status:** ⬜ Not started
 
#### Planned
- [ ] Hetzner CX22 VPS bestellen, Ubuntu 22.04
- [ ] Echten SSH auf Port 2222 verschieben
- [ ] UFW Firewall konfigurieren (Ports 22, 23, 2222, 8080)
- [ ] Cowrie installieren und konfigurieren (JSON-Logs, Fake-Hostname)
- [ ] iptables NAT: Port 22 → Cowrie Port 2222
- [ ] Ersten Log-Eintrag in `cowrie.json` bestätigen
#### Actually done
> *(Fill in after the session)*
 
-
#### Problems & notes
> *(Anything unexpected, links, commands that helped)*
 
-
---
 
### Week 2 — Log Parser & Database Pipeline
 
**Period:** `DD.MM.YYYY – DD.MM.YYYY`  
**Status:** ⬜ Not started
 
#### Planned
- [ ] SQLite Schema erstellen (`attacks` + `ip_cache` Tabellen, Indizes)
- [ ] `parser/log_parser.py` schreiben — Cowrie JSON → DB
- [ ] `parser/geoip.py` — ip-api.com Integration mit Cache
- [ ] Deduplizierung: Parser merkt sich letzten verarbeiteten Log-Offset
- [ ] Cron-Job einrichten: alle 5 Minuten
- [ ] DB mit echten Daten bestätigen (`SELECT COUNT(*) FROM attacks`)
#### Actually done
> *(Fill in after the session)*
 
-
#### Problems & notes
> *(Anything unexpected, links, commands that helped)*
 
-
---
 
### Week 3 — Flask REST API
 
**Period:** `DD.MM.YYYY – DD.MM.YYYY`  
**Status:** ⬜ Not started
 
#### Planned
- [ ] Flask App Factory in `api/app.py`
- [ ] `GET /api/attacks` — Kartendaten (IP-Cluster mit lat/lon/count)
- [ ] `GET /api/stats` — Aggregierte Statistiken
- [ ] `GET /api/recent` — Live-Feed letzte 50 Events
- [ ] HTTP Basic Auth Decorator (`api/auth.py`)
- [ ] Security Headers Middleware (CSP, X-Frame-Options, etc.)
- [ ] Rate Limiting via `flask-limiter` (60 req/min)
- [ ] Alle SQL-Queries: nur Parameterized Statements
#### Actually done
> *(Fill in after the session)*
 
-
#### Problems & notes
> *(Anything unexpected, links, commands that helped)*
 
-
---
 
### Week 4 — Dashboard Frontend
 
**Period:** `DD.MM.YYYY – DD.MM.YYYY`  
**Status:** ⬜ Not started
 
#### Planned
- [ ] Leaflet.js Weltkarte mit CartoDB Dark Theme
- [ ] Circle Markers skaliert nach `log(count)`, Popups mit Details
- [ ] Stat-Karten: Total Angriffe, Unique IPs, Länder
- [ ] Chart.js: Top 10 Passwörter (Bar), Angriffe pro Stunde (Line)
- [ ] Live-Feed Tabelle: letzte 50 Angriffe scrollend
- [ ] Auto-Refresh alle 30 Sekunden (kein Full-Page-Reload)
- [ ] Design: Terminal-Ästhetik (#0a0a0a bg, #00ff41 text, Monospace)
- [ ] Alles via `textContent` rendern — kein `innerHTML`
#### Actually done
> *(Fill in after the session)*
 
-
#### Problems & notes
> *(Anything unexpected, links, commands that helped)*
 
-
---
 
### Week 5 — Analysis & Advanced Features
 
**Period:** `DD.MM.YYYY – DD.MM.YYYY`  
**Status:** ⬜ Not started
 
#### Planned
- [ ] `analysis/hibp_check.py` — k-Anonymity SHA1-Prefix Check
- [ ] `analysis/botnet_detector.py` — koordinierte Angriffe erkennen
- [ ] `GET /api/analysis/passwords` — Top Passwörter + HIBP Treffer
- [ ] `GET /api/analysis/botnet` — verdächtige Angriffswellen
- [ ] `GET /api/export/csv` — Auth-geschützter Daten-Export
- [ ] Analysis-Tab im Dashboard
#### Actually done
> *(Fill in after the session)*
 
-
#### Problems & notes
> *(Anything unexpected, links, commands that helped)*
 
-
---
 
### Week 6 — HTTPS, Hardening & Documentation
 
**Period:** `DD.MM.YYYY – DD.MM.YYYY`  
**Status:** ⬜ Not started
 
#### Planned
- [ ] nginx Reverse Proxy vor Flask
- [ ] Let's Encrypt Zertifikat via Certbot
- [ ] HSTS Header in nginx
- [ ] Fail2Ban: SSH Port 2222 + Dashboard Rate-Limit
- [ ] Alle Secrets in `.env` — keine Hardcoded Values
- [ ] `git log` prüfen — keine Secrets in History
- [ ] `RESEARCH.md` schreiben (Findings, Statistiken, Erkenntnisse)
- [ ] README finalisieren mit Screenshots
#### Actually done
> *(Fill in after the session)*
 
-
#### Problems & notes
> *(Anything unexpected, links, commands that helped)*
 
-
---
 
## Research Findings
 
> *(Filled in during Week 6 — real data from the honeypot)*
 
| Metric | Value |
|--------|-------|
| Time to first attack after deployment | — |
| Total attacks collected | — |
| Unique attacker IPs | — |
| Countries represented | — |
| Most attacked username | — |
| Most tried password | — |
| Longest single botnet wave | — |
| Password found in HIBP (top hit) | — |
 
