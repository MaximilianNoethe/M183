# Security & Datenschutz

Dieses Projekt sammelt absichtlich echte Angriffe — die Absicherung der eigenen
Infrastruktur und der Umgang mit den Daten sind deshalb zentral.

## Threat-Model
| Asset | Bedrohung | Massnahme |
|---|---|---|
| Admin-Zugang (SSH :2222) | Brute-Force | Key-only, Root-/Passwort-Login aus, Fail2Ban auf :2222 |
| Honeypot (Cowrie :2223/2224) | soll angegriffen werden | bewusst exponiert, läuft isoliert als User `cowrie` |
| Dashboard / API | unbefugter Zugriff auf Angriffsdaten | Basic-Auth + Token, nur `127.0.0.1`, nginx-HTTPS davor |
| API | XSS, Injection, Scraping | `textContent` statt `innerHTML`, parametrisiertes SQL, Rate-Limit, CSP |
| SQLite-DB | Datenabfluss (IPs = Personendaten) | DB bleibt privat, nie im Repo, Rechte 640 |
| Secrets | Leak über Git | alles via `.env` (gitignored), nichts hardcoded |

## Härtung der eigenen Anwendung
- **Auth:** alle `/api/*` und die Dashboard-Seite hinter Auth (`hmac.compare_digest`,
  timing-safe). Token-Alternative für Skripte.
- **Security-Header** auf jeder Antwort: CSP (nur Self + die genutzten CDNs),
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`,
  `Permissions-Policy`. HSTS terminiert in nginx.
- **Rate-Limit:** 60 req/min pro IP (`flask-limiter`).
- **SQL:** ausschliesslich Platzhalter (`?`), nie String-Konkatenation. Sucheingaben
  zusätzlich längenbegrenzt.
- **XSS:** das Frontend rendert API-Daten nur über `textContent`/`createElement`.
- **Transport:** Flask lauscht nur auf `127.0.0.1:8080`; nginx macht TLS (selbstsigniert,
  da keine Domain) und leitet weiter.

## Umgang mit den Honeypot-Daten
- **Beobachtung only.** Keine Gegenangriffe, kein Kontakt zu Angreifer-Systemen, keine
  aktiven Scans zurück.
- **Passwörter** werden so gespeichert, wie sie probiert wurden — nur zur Analyse,
  niemals gegen echte Systeme getestet.
- **HIBP-Abgleich** über k-Anonymity: nur die ersten 5 SHA1-Zeichen verlassen den
  Server, das rohe Passwort nie.

## Rechtliches (Schweizer DSG)
IP-Adressen gelten als Personendaten. Erhebung erfolgt zum legitimen Zweck der
Sicherheitsforschung, Auswertung nur aggregiert (Geo/ASN/Muster). Die Datenbank ist
nicht öffentlich, das Dashboard liegt hinter Login + HTTPS. Es werden keine Daten an
Dritte weitergegeben (ausser dem anonymisierten HIBP-Prefix-Lookup).

## Eine Schwachstelle melden
Privates Forschungsprojekt — Hinweise bitte direkt an den Repo-Owner.
