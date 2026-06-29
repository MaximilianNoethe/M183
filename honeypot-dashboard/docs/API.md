# API-Referenz

Alle Endpoints liefern JSON. Bis auf `/api/health` brauchen alle eine Authentifizierung.

## Authentifizierung
Zwei Varianten (beide gegen die Werte aus `.env`):

- **HTTP Basic Auth** — `DASHBOARD_USER` / `DASHBOARD_PASSWORD`. Der Browser nutzt das
  automatisch, weil schon die Dashboard-Seite (`/`) hinter Basic Auth liegt.
- **Bearer-Token** — `Authorization: Bearer <API_TOKEN>` für Skripte/curl.

```bash
curl -u "$DASHBOARD_USER:$DASHBOARD_PASSWORD" http://localhost:8080/api/stats
curl -H "Authorization: Bearer $API_TOKEN"     http://localhost:8080/api/stats
```

Ohne gültige Credentials antworten geschützte Routen mit `401`. Jede Antwort trägt die
Security-Header (CSP, `X-Frame-Options`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`).
Rate-Limit: 60 Anfragen/Minute pro IP (`429` bei Überschreitung).

## Endpoints

### `GET /api/health` — *kein Auth*
Liveness-Check für Monitoring. `503`, falls die DB nicht erreichbar ist.
```json
{ "status": "ok", "database": true, "total_attacks": 70020, "last_attack": "2026-06-22T18:24:00Z" }
```

### `GET /api/stats`
Aggregierte Kennzahlen für die Karten und Charts.
```json
{
  "total": 70020, "unique_ips": 1242, "countries": 75,
  "first_seen": "2026-06-15T14:39:00Z", "last_seen": "2026-06-22T18:24:00Z",
  "busiest_hour": { "hour": "2026-06-18T03", "count": 612 },
  "top_usernames": [ { "value": "root", "count": 5171 } ],
  "top_passwords": [ { "value": "123456", "count": 1473 } ],
  "top_countries": [ { "value": "Netherlands", "count": 47768 } ],
  "per_hour":      [ { "hour": "2026-06-15T14", "count": 48 } ]
}
```

### `GET /api/attacks`
Kartenpunkte: ein Eintrag je IP mit Koordinaten (nur Zeilen mit `latitude`).

### `GET /api/recent`
Die letzten 50 Events, neueste zuerst.

### `GET /api/search?ip=&country=&username=`
Parametrisierte `LIKE`-Filter (Eingaben auf 64 Zeichen gekappt). Max. 100 Treffer.

### `GET /api/analysis/passwords`
Top-Passwörter inkl. HIBP-Leak-Anzahl (k-Anonymity, serverseitig gecacht).

### `GET /api/analysis/commands`
Häufigste Befehle, die Angreifer nach dem „Login" absetzen.

### `GET /api/analysis/downloads`
Befehle mit `wget`/`curl`/`http` oder `file_download`-Events (Malware-Nachladen).

### `GET /api/analysis/providers`
Top-Hosting-Provider nach ASN (Events + Anzahl IPs).

### `GET /api/analysis/attackers`
Die 15 aggressivsten IPs mit `country`, `asn`, `count`, `first_seen`, `last_seen`.

### `GET /api/analysis/botnet`
Minutenfenster mit ≥5 verschiedenen IPs (koordinierte Wellen).

### `GET /api/analysis/timeline`
Angriffe pro Tag (`day`, `count`, `ips`).

### `GET /api/export/csv` · `GET /api/export/json`
Vollständiger Datenexport aller Angriffe als Datei-Download.
