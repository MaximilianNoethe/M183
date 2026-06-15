# Honeypot + Live Attack Map
 
 
**Stack:** Python · Flask · Cowrie · SQLite · Leaflet.js · Chart.js  
**Server:** Kamatera · Ubuntu 22.04 · 1 vCPU / 2 GB / 30 GB · Frankfurt  
**Kosten:** Kamatera 30-day free trial (hourly billing; delete server before trial ends)

## Architecture
 
```
Internet (echte Angreifer)
        │
        ▼
  [Cowrie Honeypot]  ←── SSH Port 22 / Telnet Port 23
  JSON logs bei jedem Angriff
        │
        ▼
  [log_parser.py]    ←── Lauft jede 5 min via cron
  GeoIP enrichment → SQLite DB
        │
        ▼
  [Flask API]        ←── /api/attacks  /api/stats  /api/recent
        │
        ▼
  [Dashboard]        ←── Leaflet world map + Chart.js stats
```
 
---
 
## Projekt Status
 
| Week | Topic | Status |
|------|-------|--------|
| 1 | VPS · Cowrie · Firewall | In progress |
| 2 | Log Parser · SQLite · GeoIP | ⬜ Not started |
| 3 | Flask API · Auth · Security Headers | ⬜ Not started |
| 4 | Dashboard · World Map · Charts | ⬜ Not started |
| 5 | Analysis · HIBP · Botnet Detection | ⬜ Not started |
| 6 | HTTPS · Hardening · Documentation | ⬜ Not started |
  
---
 
## Journal
 
> Dieses Journal tracked was ich geplant habe vs. was ich wirklich erreicht habe in dieser Woche
> Das Journal wird nach jedem Arbeitsblock geupdated
 
---
 
### Week 1 — Infrastructure & Honeypot Sensor
 
**Period:** `08.06.2026`  
**Status:** VPS läuft, Honeypot noch nicht live
 
#### Geplant
- Kamatera VPS bestellen, Ubuntu 22.04
- Echten SSH auf Port 2222 verschieben —> *Skript fertig, noch nicht ausgeführt*
- UFW Firewall konfigurieren (Ports 22, 23, 2222, 8080) —> *Skript fertig, noch nicht ausgeführt*
- Cowrie installieren und konfigurieren (JSON-Logs, Fake-Hostname) —> *Skript fertig, noch nicht ausgeführt*
- iptables NAT: Port 22 -> Cowrie Port 2222 -> *Skript fertig, noch nicht ausgeführt*
- Ersten Log-Eintrag in `cowrie.json` bestätigen —> *offen*
#### Erledigt
- Kamatera VPS bestellt & läuft: Frankfurt, Ubuntu 22.04, Type B, 1 vCPU / 2 GB RAM / 30 GB SSD, öffentliche WAN-IP.
- SSH-Key erstellt: auf dem Mac.
- Kompletter Week-1-Code geschrieben: (lokal, noch nicht auf dem Server ausgeführt):
  - parser/db.py -> DB-Schema + Testss
  - scripts/setup_server.sh -> SSH Hardening, UFW, iptables NAT
  - scripts/setup_cowrie.sh —> Cowrie Install + JSON Logging
  - systemd/ —> Units für Cowrie, Parser Timer und API
- Projektgerüst: für alle 6 Wochen + .gitignore, requirements.txt, .env.example.

#### Probleme & Notizen
- Hetzner → Kamatera gewechselt um den 30-Tage-Gratis-Trial zu nutzen.
- Reminder: Server vor Trial-Ende (30 Tage) löschen, sonst wird abgezahlt.
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
 
