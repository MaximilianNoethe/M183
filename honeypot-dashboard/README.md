# Honeypot + Live Attack Map

[![tests](https://github.com/MaximilianNoethe/M183/actions/workflows/tests.yml/badge.svg)](https://github.com/MaximilianNoethe/M183/actions/workflows/tests.yml)

**Stack:** Python · Flask · Cowrie · SQLite · Leaflet.js · Chart.js  
**Server:** Kamatera · Ubuntu 22.04 · 1 vCPU / 2 GB / 30 GB · Frankfurt  
**Kosten:** Kamatera 30-day free trial (hourly billing; delete server before trial ends)

## Architektur
 
```
Internet (echte Angreifer)
        │   SSH :22 / Telnet :23  ──NAT──>  Cowrie :2223 / :2224
        ▼
  [Cowrie Honeypot]              JSON-Logs bei jedem Angriff
        │
        ▼
  [log_parser.py]                systemd-Timer alle 5 min, liest auch rotierte Logs
  GeoIP + ASN (ip-api, Cache)  ─────────────>  SQLite
        │
        ▼
  [Flask API]   /api/health /attacks /stats /recent /search
                /api/analysis/* (HIBP · Botnet · Befehle · Provider · Attacker · Timeline)
                /api/export/csv · /api/export/json
        │   Basic Auth + Bearer-Token + Security-Header + Rate-Limit
        ▼
  [nginx :443]  selbstsigniertes HTTPS  ──>  Flask :8080 (localhost)
        │
        ▼
  [Dashboard]   Leaflet-Karte · Chart.js · Live-Feed · Analyse · Suche
```
 
---
 
## Projekt Status
 
| Week | Topic | Status |
|------|-------|--------|
| 1 | VPS · Cowrie · Firewall | Fertig —> Honeypot live |
| 2 | Log Parser · SQLite · GeoIP | Deployed —> Parser läuft live auf dem Server |
| 3 | Flask API · Auth · Security Headers | Fertig —> 18 Tests grün, deployed |
| 4 | Dashboard · World Map · Charts | Fertig —> Live mit echten Angriffen |
| 5 | Analysis · HIBP · Botnet Detection | Fertig —> RESEARCH.md mit echten Funden |
| 6 | HTTPS · Hardening · Documentation | Configs/Skripte fertig, Server-Deploy offen |

---

## Dokumentation
- **[`docs/API.md`](docs/API.md)** — alle API-Endpoints, Auth (Basic + Token), Beispiele
- **[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)** — Schritt-für-Schritt Server-Runbook
- **[`SECURITY.md`](SECURITY.md)** — Threat-Model, Härtung, Datenschutz (DSG)
- **[`RESEARCH.md`](RESEARCH.md)** — Auswertung & Interpretation der echten Angriffe

---
 
## Lokal starten (Quickstart)

> Voraussetzungen: Python 3.11+ und git. Der Honeypot-Sensor selbst läuft auf dem
> Server — lokal nimmst du die ganze Pipeline (Parser, API und Dashboard) in Betrieb.

```bash
git clone https://github.com/MaximilianNoethe/M183.git
cd M183/honeypot-dashboard

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # Werte anpassen: DASHBOARD_USER/PASSWORD, SECRET_KEY
```

**Tests laufen lassen** — beweist, dass Parser + GeoIP lokal funktionieren:

```bash
pytest tests/ -v              # 28 Tests (Parser, API, Analyse)
```

**Parser lokal ausprobieren** — schreibt die 20 Beispiel-Events des Fixtures in eine
lokale SQLite-DB (optional, macht echte GeoIP-Abfragen → ~30s beim ersten Mal):

```bash
COWRIE_LOG_PATH=tests/fixtures/sample_cowrie.json DATABASE_PATH=local.db \
  python3 -m parser.log_parser
sqlite3 local.db "SELECT COUNT(*) FROM attacks;"
```

**Dashboard lokal ansehen** — API gegen die eben gefüllte `local.db` starten:

```bash
DATABASE_PATH=local.db python3 -m api.app    # Flask auf http://localhost:8080
```

Dann `http://localhost:8080` im Browser öffnen und mit `DASHBOARD_USER` /
`DASHBOARD_PASSWORD` aus deiner `.env` einloggen (Default: `admin` / `changeme`).
Sichtbar: Statistik-Karten, Charts (Top-Passwörter, Angriffe/Stunde), Live-Feed,
der Analyse-Bereich (Befehle, HIBP, Botnet, Provider) und die Suche. Die **Weltkarte**
bleibt mit den Test-IPs leer (RFC-5737-Adressen haben keine Geo-Position) — auf dem
Server zeigt sie die echten Angriffe.

Auf dem Server läuft der Parser nicht manuell, sondern automatisch via systemd-Timer
gegen die echten Cowrie-Logs (alle 5 Min).

---

## Journal
 
> Dieses Journal tracked was ich geplant habe vs. was ich wirklich erreicht habe in dieser Woche

> Das Journal wird nach jedem Arbeitsblock geupdated
 
---
 
### Week 1 — Infrastructure & Honeypot Sensor
 
**Period:** `08.06.2026 – 15.06.2026`  
**Status:** Honeypot live —> fängt echte Angriffe aus dem Internet
 
#### Geplant
- Kamatera VPS bestellen, Ubuntu 22.04
- Echten SSH auf Port 2222 verschieben
- UFW Firewall konfigurieren (Ports 22, 23, 2222, 2223, 2224, 8080)
- Cowrie installieren und konfigurieren (JSON-Logs, Fake-Hostname)
- iptables NAT: Port 22/23 -> Cowrie 2223/2224
- Ersten Log-Eintrag in cowrie.json bestätigen
#### Erledigt
- Kamatera VPS bestellt & läuft: Frankfurt, Ubuntu 22.04, Type B, 1 vCPU / 2 GB RAM / 30 GB SSD, öffentliche WAN-IP. <img width="2500" height="548" alt="image" src="https://github.com/user-attachments/assets/57a92b28-a10d-4243-a96b-57c165949ff4" />

- SSH-Key erstellt: auf dem Mac.
- Kompletter 1. Woche Code geschrieben: (lokal, noch nicht auf dem Server ausgeführt):
  - parser/db.py -> DB-Schema + Testss
  - scripts/setup_server.sh -> SSH Hardening, UFW, iptables NAT
  - scripts/setup_cowrie.sh —> Cowrie Install + JSON Logging
  - systemd/ —> Units für Cowrie, Parser Timer und API
- Projektgerüst: für alle 6 Wochen + .gitignore, requirements.txt, .env.example.

**Deployment am 15.06.2026 —> Honeypot ist live gegangen:**
- Admin User max mit SSH-Key + sudo angelegt, Root- und Passwort-Login deaktiviert, echter SSH auf Port 2222.
- setup_server.sh ausgeführt: UFW aktiv, iptables NAT (öffentlich 22/23 → Cowrie 2223/2224).
- setup_cowrie.sh ausgeführt: Cowrie als User cowrie im eigenen venv, JSON Logging, Fake Hostname srv-prod-01.
- systemd Service honeypot cowrie läuft und startet automatisch beim Boot.
- Erster Angriff bestätigt —> eigener SSH-Test und bereits echte Bots aus dem Internet.

Live-Log (cowrie.json) mit echten Verbindungen:

![Cowrie Live-Log](docs/screenshots/week1-cowrie-live-log.png)

Eigener SSH-Test —> gelandet in der Cowrie-Fake-Shell root@srv-prod-01:

![SSH-Test gegen den Honeypot](docs/screenshots/week1-attack-test.png)

**Woran man sieht, dass nicht nur ich angegriffen habe:**
- Meine eigene IP ist 194.209.11.12, das ist mein SSH-Test (Protokoll ssh auf Port 2223 endet mit cowrie.login.success für root/admin1233).
- Die IPs 128.199.8.54 und 213.5.70.12 habe ich nicht ausgelöst, das sind fremde Bots die von selbst auf den Telnett Port 2224 verbunden haben ("protocol":"telnet", mehrere cowrie.session.connect). 128.199.8.54 gehört zu DigitalOcean — typische Scanner-Infrastruktur.
- Faustregel fürs Log: jede src_ip, die nicht 194.209.11.12 ist, ist ein fremder Angreifer. Schon in den ersten paar Minuten mehrere fremde Sessions.

#### Probleme & Notizen
- Hetzner → Kamatera gewechselt um den 30-Tage-Gratis-Trial zu nutzen.
- Reminder: Server vor Trial-Ende (30 Tage) löschen, sonst wird abgezahlt.
---
 
### Week 2 — Log Parser & Database Pipeline
 
**Period:** `15.06.2026`  
**Status:** Code fertig & getestet; am 22.06.2026 auf dem Server deployed —> echte Angriffe landen in SQLite
 
#### Geplant
- SQLite Schema erstellen (attacks + ip_cache Tabellen, Indizes)
- parser/log_parser.py schreiben — Cowrie JSON → DB
- parser/geoip.py, ip-api.com Integration mit Cache
- Deduplizierung: Parser merkt sich letzten verarbeiteten Log-Offset
- Cron-Job einrichten: alle 5 Minuten
- DB mit echten Daten bestätigen (`SELECT COUNT(*) FROM attacks`)
#### Erledigt
- DB Helfer in parser/db.py ergänzt: insert_attack, get_offset / set_offset cache_get/cache_set.
- parser/geoip.py -> GeoIP über ip-api.com immer erst ip_cache prüfen, auf 45 req pro min herunter geschalten.
- parser/log_parser.py — liest cowrie.json ab gespeichertem Offset, filtert relevante Events, reichert mit GeoIP an, schreibt parametrisiert in SQLite.
- Tests: 11 grün (5 DB + 6 neue für Parser & GeoIP), laufen gegen das Fixture mit RFC-5737-IPs.

**Deployment am 22.06.2026 (heute) —> Parser läuft auf dem Server:**
- Repo auf dem Server aktualisiert, Data-Dir `/var/lib/honeypot` angelegt (cowrie:cowrie).
- Eigenes Projekt-venv `/opt/honeypot/.venv` + requirements installiert (getrennt von Cowries venv).
- `.env` gesetzt (DATABASE_PATH, COWRIE_LOG_PATH, Dashboard-Login), Rechte 640 root:cowrie.
- Erster echter Parser-Lauf: 88 unterschiedliche Angreifer-IPs im Log, GeoIP-Anreicherung läuft, Angriffe landen in SQLite.
- systemd-Timer aktiviert (`honeypot-parser.timer`, alle 5 Min) → läuft seither vollautomatisch. Erster Backfill: **9540 Angriffe**, dann pro Auto-Lauf neue dazu (Offset-Dedup bestätigt: +319 im ersten 5-Min-Lauf).
- Erste Auswertung direkt per SQL auf dem Server — so sah es VOR dem Dashboard aus:

![SQLite-Auswertung auf dem Server](docs/screenshots/week2-sqlite-stats.png)
#### Probleme & Notizen
- Cron durch systemd Timer ersetzt (honeypot-parser.timer, alle 5 Min) so ist est sauberer als Crontab.
- Parser-Code war fertig & getestet; das Live-Schalten haben wir am 22.06. gemacht.

**Aufwand & Blockaden 22.06.2026 (Deployment-Session, ~1.5 h bisher):**
- ~0.5 h: README-Quickstart geschrieben (Reaktion auf Reviewer-Feedback, Note 4.5).
- git "dubious ownership" auf `/opt/M183` (Repo gehört root) → `safe.directory` + pull mit sudo (~10 min weg).
- nano: nicht mehr rausgekommen (`Ctrl+O` vs `Ctrl+0`), Terminal geschlossen, `.env` nochmal gemacht (~15 min weg).
- Parser-Lauf wirkte „hängend" → war die GeoIP-Drossel (1,4 s pro neuer IP, ~2 Min bei 88 IPs). Einmal aus Versehen mit Ctrl+C abgebrochen (committet erst am Ende → nichts gespeichert), dann durchlaufen lassen.
- Wo Zeit verloren geht: Server-Bedienung (nano/Rechte/sudo/Ownership) + Warten auf GeoIP. Idee für später: ip-api Batch-Endpoint (100 IPs pro Anfrage).
---
 
### Week 3 — Flask REST API
 
**Period:** `22.06.2026`  
**Status:** Fertig —> API läuft, 18 Tests grün, auf dem Server deployed
 
#### Geplant
- [x] Flask App Factory in `api/app.py`
- [x] `GET /api/attacks` — Kartendaten (IP-Cluster mit lat/lon/count)
- [x] `GET /api/stats` — Aggregierte Statistiken
- [x] `GET /api/recent` — Live-Feed letzte 50 Events
- [x] HTTP Basic Auth Decorator (`api/auth.py`)
- [x] Security Headers Middleware (CSP, X-Frame-Options, etc.)
- [x] Rate Limiting via `flask-limiter` (60 req/min)
- [x] Alle SQL-Queries: nur Parameterized Statements
#### Erledigt
- App-Factory `api/app.py` baut Flask, registriert Blueprints + Middleware, liefert das Dashboard unter `/`.
- Endpoints: `/api/attacks` (Kartendaten), `/api/stats` (Totals + Top-10 Usernames/Passwörter/Länder + Angriffe pro Stunde), `/api/recent` (letzte 50), `/api/search` (parametrisierte Filter).
- Basic Auth (`hmac.compare_digest`) auf allen `/api/*` und auf der Dashboard-Seite. Security-Header (CSP, X-Frame-Options, nosniff) auf jeder Antwort, Rate-Limit 60/min.
- Liest die DB über `parser.db.get_connection` (kein doppelter Code), alle Queries parametrisiert.
- 7 neue API-Tests, insgesamt **18 grün**; lokal per `curl` verifiziert (401 ohne Login, JSON mit Login).
- In 3 kleinen Commits gebaut, dann auf dem Server deployed (`honeypot-api.service`).
#### Probleme & Notizen
- Beim Server-Deploy lief der Service in einen Crash-Loop (`NotImplementedError`): der `git pull` auf dem Server war nicht durchgelaufen → noch die Stub-Version. Fix: Service stoppen, `sudo git -C /opt/honeypot pull`, neu starten.
- API lauscht bewusst nur auf `127.0.0.1:8080` (nginx + HTTPS folgen in Woche 6) → Zugriff vorerst per SSH-Tunnel.
---
 
### Week 4 — Dashboard Frontend
 
**Period:** `22.06.2026`  
**Status:** Fertig —> Live-Dashboard zeigt echte Angriffe (11'652 zum Zeitpunkt des Screenshots)
 
#### Geplant
- [x] Leaflet.js Weltkarte mit CartoDB Dark Theme
- [x] Circle Markers skaliert nach `log(count)`, Popups mit Details
- [x] Stat-Karten: Total Angriffe, Unique IPs, Länder
- [x] Chart.js: Top 10 Passwörter (Bar), Angriffe pro Stunde (Line)
- [x] Live-Feed Tabelle: letzte 50 Angriffe
- [x] Auto-Refresh alle 30 Sekunden (kein Full-Page-Reload)
- [x] Design: Terminal-Ästhetik (#0a0a0a bg, #00ff41 text, Monospace)
- [x] Alles via `textContent` rendern — kein `innerHTML`
#### Erledigt
- Single-Page-Dashboard (`frontend/templates/dashboard.html`) mit Leaflet-Weltkarte (CARTO Dark), Chart.js und Live-Feed, Terminal-Optik.
- Karte: ein grüner Kreis pro Angreifer-IP, Grösse nach `log(count)`, Popup mit IP/Land/Anzahl.
- Stat-Karten (Total / Unique IPs / Länder), Top-10-Passwörter (Balken), Angriffe pro Stunde (Linie), Live-Feed der letzten 50.
- Auto-Refresh alle 30s, alles über `textContent` gerendert (kein `innerHTML`, XSS-sicher).
- Dashboard-Seite hinter Login → der Browser nutzt den Login automatisch für die API-Abrufe.

Live mit echten Daten (11'652 Angriffe, 98 IPs, 30 Länder):

![Dashboard — Weltkarte](docs/screenshots/week4-dashboard-map.png)

![Dashboard — Charts & Live-Feed](docs/screenshots/week4-dashboard-charts.png)
#### Probleme & Notizen
- SSH-Tunnel nötig (`ssh -p 2222 -L 8080:127.0.0.1:8080 …`), weil die API nur auf localhost lauscht. Das „Connection refused" im Tunnel hiess: der Service lief noch nicht (siehe Crash-Loop in Woche 3).
- Erkenntnisse aus den echten Daten: Niederlande massiv überrepräsentiert (Hosting-Infrastruktur, nicht Standort der Angreifer); klarer Angriffs-Peak um ~04:00 und ~15:00 Uhr; `alpine`/`pi` deuten auf gezielte IoT-Angriffe.
---
 
### Week 5 — Analysis & Advanced Features
 
**Period:** `22.06.2026`  
**Status:** Fertig —> Analyse-Features live, `RESEARCH.md` mit echten Funden
 
#### Geplant
- [x] `analysis/hibp_check.py` — k-Anonymity SHA1-Prefix Check
- [x] `analysis/botnet_detector.py` — koordinierte Angriffe erkennen
- [x] `GET /api/analysis/passwords` — Top Passwörter + HIBP Treffer
- [x] `GET /api/analysis/botnet` — verdächtige Angriffswellen
- [x] `GET /api/export/csv` — Auth-geschützter Daten-Export
- [x] Analyse-Bereich im Dashboard (statt Tab)
#### Erledigt
- `hibp_check.py` — HaveIBeenPwned über k-Anonymity (nur 5 SHA1-Zeichen verlassen den Server).
- `botnet_detector.py` — findet Minuten mit ≥5 verschiedenen IPs (koordinierte Wellen).
- API: `/api/analysis/passwords` (Top-PW + Leak-Treffer), `/api/analysis/botnet`, `/api/analysis/commands` (Top-Befehle der Angreifer), `/api/export/csv`.
- Dashboard: neuer Analyse-Bereich (Top-Befehle, HIBP-Leak-Treffer, Botnet-Wellen) + CSV-Export-Button.
- 6 neue Tests (insgesamt **24 grün**), auf dem Server deployed.
- **`RESEARCH.md` geschrieben** mit echten Zahlen + Interpretation (über die ganze Woche: **70'020 Angriffe, 1'242 IPs, 75 Länder**).
#### Erkenntnisse (Highlights, Details in `RESEARCH.md`)
- **100 % der Top-Passwörter** stehen in HIBP — `123456` allein in **210 Mio** Leaks. Die Bots fahren reine Leak-Listen ab.
- **~60 % des Traffics aus nur 26 IPs** zweier Offshore-Hoster (Pfcloud UG, Offshore LC) — die ASN-Sicht ist schärfer als die Länder-Statistik.
- Häufigster Befehl: `uname -s -v -n -r -m` (17'828×, OS-Fingerprinting). Der Befehl `cat /etc/shadow /etc/passwd` (82×) zeigt gezielten **Passwort-Hash-Klau**.
- Recon-Skripte prüfen RAM/CPU/GPU (`nvidia`) → Eignung fürs **Krypto-Mining**; dazu `sudo -S` mit Leak-Passwörtern (Privilege Escalation).
- `login.success` >> `login.failed` ist ein **Cowrie-Artefakt** (freizügige Fake-Auth), kein erratenes Passwort.
#### Probleme & Notizen
- Datenfenster ist ein Log-Tag (~16,5 h), weil Cowrie die JSON-Logs täglich rotiert und der Parser nur `cowrie.json` liest → mögliche Erweiterung: rotierte Logs mitlesen.
- HIBP-Treffer werden serverseitig gecacht, damit das Dashboard nicht bei jedem Refresh erneut abfragt.
---
 
### Week 6 — HTTPS, Hardening & Documentation
 
**Period:** `22.06.2026`  
**Status:** Configs/Skripte + Doku fertig; nginx/Fail2Ban-Deploy auf dem Server offen
 
#### Geplant
- [x] nginx Reverse Proxy vor Flask
- [x] HTTPS-Zertifikat (selbstsigniert, da keine Domain — Let's Encrypt bräuchte eine)
- [x] HSTS Header in nginx
- [x] Fail2Ban: echter Admin-SSH Port 2222 (Honeypot-Ports bleiben offen)
- [x] Alle Secrets in `.env` — keine Hardcoded Values
- [x] `RESEARCH.md` schreiben (Findings, Statistiken, Erkenntnisse)
- [x] README finalisieren mit Screenshots + Architektur-Diagramm
#### Erledigt
- `nginx/honeypot.conf` — Reverse Proxy auf Flask `127.0.0.1:8080`, HTTP→HTTPS-Redirect, HSTS.
- `scripts/setup_https.sh` — installiert nginx, generiert selbstsigniertes Zertifikat, aktiviert die Config, öffnet UFW 80/443.
- `scripts/setup_fail2ban.sh` — Jail nur für den echten Admin-SSH `:2222` (die Cowrie-Ports bleiben bewusst offen).
- README mit erweitertem Architektur-Diagramm (NAT, GeoIP+ASN, Analyse-API, nginx/HTTPS) + CI-Badge.
- `RESEARCH.md` inkl. „Schutzmassnahmen"-Abschnitt aus den echten Funden.
- Secrets-Check: alles über `os.getenv()`/`.env` (gitignored), keine Hardcoded-Werte im Code.
#### Probleme & Notizen
- Let's Encrypt braucht einen Domainnamen → für die blanke IP selbstsigniertes Zertifikat (Browser-Warnung ist hier ok, Research-Setup).
- Honeypot-Ports (2223/2224) dürfen NICHT von Fail2Ban geblockt werden — die sollen ja Angriffe fangen. Jail nur auf `:2222`.
---
 
## Research Findings

> Echte Daten vom Honeypot. Volle Auswertung + Interpretation in **[`RESEARCH.md`](RESEARCH.md)**.
> Zeitraum: 15.–22.06.2026 (~7 Tage, 8 Logdateien zusammengeführt).

| Metric | Value |
|--------|-------|
| Angriffs-Events total | 70'020 |
| Unique attacker IPs | 1'242 |
| Countries represented | 75 |
| Events pro Stunde (Schnitt) | ~408 |
| Häufigster Username | `root` (5'171×) |
| Häufigstes Passwort | `123456` (1'473×) |
| `123456` in HIBP-Leaks | 210'318'957 |
| Top-Passwörter in HIBP | 100 % |
| Grösster Hosting-Provider | Pfcloud UG (25'941 Events / 11 IPs) |
| Häufigster Angreifer-Befehl | `uname -s -v -n -r -m` (17'828×) |
 
