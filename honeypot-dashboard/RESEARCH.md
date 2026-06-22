# Research Findings — Honeypot Live Attack Data

Auswertung der echten Angriffe, die mein Cowrie-Honeypot (Kamatera-VPS, Frankfurt,
öffentliche IP) aus dem Internet eingefangen hat. Alle Zahlen stammen aus der
SQLite-DB, die der Parser aus Cowries JSON-Logs füllt.

## Messzeitraum & Datenbasis
- **Zeitfenster:** 22.06.2026, 00:01 – 16:36 UTC (~16,5 Stunden, ein Log-Tag).
- Cowrie rotiert die JSON-Logs täglich; ausgewertet ist hier der aktuelle Tag
  (`cowrie.json`). Ältere Tage liegen als rotierte Dateien vor → mehr Zeitraum
  wäre durch Einlesen der rotierten Logs möglich (siehe „Grenzen").

## Kernzahlen
| Metrik | Wert |
|---|---|
| Angriffs-Events total | **12'165** |
| Unique Angreifer-IPs | **102** |
| Vertretene Länder | **30** |
| Events pro Stunde (Schnitt) | **~737** |
| Zeit bis zum 1. Angriff | < 1 Minute nach „Tagesbeginn" im Log (Dauerbeschuss) |

Bei nur 102 IPs und 12'165 Events kommen im Schnitt **~120 Events pro IP** — klares
Brute-Force-/Automatisierungs-Muster, keine menschlichen Einzelzugriffe.

## Geografische Verteilung
| Land | Events |
|---|---|
| Niederlande | 6'804 |
| USA | 820 |
| China | 785 |
| Bulgarien | 540 |
| Polen | 168 |
| Pakistan | 135 |
| Belgien | 134 |
| Iran / Syrien / Venezuela | 25–30 |

**Interpretation:** Die Niederlande dominieren massiv — das ist **nicht** der Standort
der Angreifer, sondern wo billige (teils „bulletproof") VPS-/Hosting-Infrastruktur
steht. GeoIP zeigt die **Maschine**, nicht den Menschen. Angriffe aus dem Internet
kommen fast immer von gekaperten oder gemieteten Servern, nicht vom Heim-PC des Täters.

## Event-Verteilung
| Event | Anzahl |
|---|---|
| `cowrie.session.connect` | 4'779 |
| `cowrie.command.input` | 3'872 |
| `cowrie.login.success` | 3'501 |
| `cowrie.login.failed` | 13 |

**Wichtige Einordnung:** Dass „success" >> „failed" ist, heisst **nicht**, dass die
Bots gute Passwörter erraten haben. Cowrie ist als Honeypot bewusst **freizügig** bei
der Fake-Anmeldung — es lässt die Angreifer rein, um zu beobachten, was sie *danach*
tun. Die spannenden Daten sind die **3'872 abgesetzten Befehle**.

## Credentials
**Top-Usernames:** `root` (661), `admin` (111), `user`, `ubuntu`, `deploy`, `test`,
`pi` (Raspberry-Pi-Default), `dev`, `guest`. → Bots zielen gleichzeitig auf
Cloud-Server (`ubuntu`/`deploy`) **und** IoT/Bastel-Geräte (`pi`).

**Top-Passwörter + Abgleich mit HaveIBeenPwned** (k-Anonymity — das echte Passwort
verlässt den Server nie, nur die ersten 5 SHA1-Zeichen):

| Passwort | Versuche | In bekannten Daten-Leaks (HIBP) |
|---|---|---|
| `123456` | 287 | **210'318'957** |
| `123` | 143 | 15'155'838 |
| `1234` | 113 | 30'330'441 |
| `alpine` | 87 | 132'980 |
| `root` | 85 | 2'260'564 |
| `12345678` | 79 | 70'550'619 |
| `password` | 78 | 52'343'151 |
| `12345` | 74 | 31'084'566 |
| `123456789` | 56 | 81'075'150 |

**Interpretation:** **100 % der Top-Passwörter** stehen in HIBP — oft in
zwei- bis dreistelligen Millionenzahlen (`123456` allein 210 Mio). Die Angreifer
raten nicht kreativ, sie spielen **bekannte Leak-/Standard-Listen** durch. Direkte
Konsequenz für die Verteidigung: Jedes Passwort, das in HIBP auftaucht, ist faktisch
„öffentlich" — genau solche Listen fahren die Bots ab.

## Was die Angreifer TUN (nach dem „Login")
Die abgesetzten Befehle zeigen ein klares, automatisiertes Vorgehen:

1. **System-Fingerprinting** — mit Abstand am häufigsten: `uname -s -v -n -r -m`
   (3'262×). Erster Schritt jedes Bots: Betriebssystem + Architektur bestimmen, um
   das **passende Malware-Binary** auszuwählen.
2. **Hardware-Recon für Krypto-Mining** — ein wiederkehrendes Recon-Skript liest
   `MemTotal` aus `/proc/meminfo` und prüft `> 1048576` (>1 GB RAM), dazu CPU-Modell,
   `nproc` und `lspci | grep -i nvidia` (GPU!). Übersetzt: „Lohnt sich diese Maschine
   zum Schürfen?" GPU/viel RAM = lohnendes Ziel.
3. **Privilege Escalation mit Leak-Passwörtern** — `echo '123456789' | sudo -S bash -c …`
   (und `123456`, `12345`): die Bots versuchen direkt, mit denselben Standard-Passwörtern
   `sudo`-Rechte zu bekommen.

Das ist der eigentliche Forschungswert: man sieht **live**, dass automatisierte
SSH-Botnetze eine feste Pipeline fahren — *einloggen → System & Hardware profilen →
ausweiten → (Malware nachladen)*.

## Botnet-Wellen (koordinierte Angriffe)
Minuten, in denen ≥5 verschiedene IPs gleichzeitig zuschlugen (`botnet_detector.py`):

| Zeitfenster (UTC) | Distinct IPs | Versuche |
|---|---|---|
| 22.06. 01:35 | 5 | 37 |
| 22.06. 01:41 | 5 | 17 |
| 22.06. 13:44 | 5 | 13 |

Mehrere IPs, die im selben Minutenfenster mit demselben Muster feuern, deuten auf
**koordinierte Botnetz-Aktivität** hin (gemeinsame Steuerung / geteilte Listen).

## Fazit
- Ein frisch ans Internet gehängter Server wird **innerhalb von Minuten** und danach
  **dauerhaft (~700 Events/h)** automatisiert angegriffen.
- Angreifer nutzen ausschliesslich **bekannte, geleakte Standard-Passwörter** (100 %
  HIBP-Treffer) — starke/zufällige Passwörter + Key-only-SSH hätten alles abgewehrt.
- Nach dem Zugang folgt eine **automatisierte Recon-Pipeline** (OS/Hardware-Profiling
  Richtung Krypto-Mining), nicht zielgerichtetes Hacking.
- GeoIP misst **Infrastruktur**, nicht Täter-Herkunft (NL-Dominanz = Hosting).

## Methodik & Grenzen
- **Methodik:** Cowrie (SSH/Telnet-Emulation) → JSON-Log → Python-Parser (Offset-Dedup,
  GeoIP via ip-api.com mit Cache) → SQLite → Flask-API → Dashboard/Analyse.
- **Grenzen:** Snapshot eines Log-Tages (~16,5 h); für mehr Zeitraum müssten die rotierten
  Cowrie-Logs mitgelesen werden. „login.success" ist ein Cowrie-Artefakt (freizügige
  Fake-Auth), kein Beweis erratener Passwörter. GeoIP ist auf Hosting-Standort verzerrt.

## Ethik & Rechtliches
Reiner Beobachtungs-Honeypot — **keine** Gegenangriffe, **kein** Kontakt zu
Angreifer-Systemen. IPs nur für Geolokalisierung/Mustererkennung. HIBP-Abgleich über
k-Anonymity (das rohe Passwort verlässt den Server nie). Nach Schweizer DSG sind IPs
Personendaten → die Datenbank bleibt privat (Dashboard nur per SSH-Tunnel, hinter Login).
