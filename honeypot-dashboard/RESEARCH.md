# Research Findings — Honeypot Live Attack Data

Auswertung der echten Angriffe, die mein Cowrie-Honeypot (Kamatera-VPS, Frankfurt,
öffentliche IP) aus dem Internet eingefangen hat. Alle Zahlen stammen aus der
SQLite-DB, die der Parser aus Cowries JSON-Logs füllt (inkl. der täglich rotierten
Logs der ganzen Laufzeit).

## Messzeitraum & Datenbasis
- **Zeitfenster:** 15.06.2026 14:39 – 22.06.2026 18:24 UTC (~7 Tage / ~172 h).
- Quelle: `cowrie.json` + 7 rotierte Tagesdateien, vom Parser zusammengeführt.

## Kernzahlen
| Metrik | Wert |
|---|---|
| Angriffs-Events total | **70'020** |
| Unique Angreifer-IPs | **1'242** |
| Vertretene Länder | **75** |
| Events pro Stunde (Schnitt) | **~408** (~9'800/Tag) |
| Events pro IP (Schnitt) | ~56 |
| Zeit bis zum 1. Angriff | wenige Minuten nach Live-Schaltung |

## Geografische Verteilung
| Land | Events |
|---|---|
| Niederlande | 47'768 (**68 %**) |
| Bulgarien | 6'147 |
| USA | 6'133 |
| China | 1'783 |
| Polen | 1'563 |
| Singapur | 1'152 |
| Pakistan | 1'097 |
| Belgien | 1'005 |
| Deutschland | 909 |
| UK | 859 |

**Interpretation:** Die Niederlande machen allein **68 %** aus — das ist **nicht** der
Standort der Angreifer, sondern wo billige (teils „bulletproof") Hosting-Infrastruktur
steht. GeoIP zeigt die **Maschine**, nicht den Menschen.

## Hosting-Provider (ASN) — die schärfste Sicht
| Provider (ASN) | Events | IPs |
|---|---|---|
| AS51396 Pfcloud UG | 25'941 | 11 |
| AS214472 Offshore LC | 15'766 | 15 |
| AS14061 DigitalOcean | 4'672 | 35 |
| AS209630 VASH KREDIT BANK | 4'576 | 3 |
| AS44382 Fiba Cloud | 2'282 | 1 |
| AS47890 UNMANAGED LTD | 1'268 | 10 |
| AS396982 Google | 1'065 | 90 |
| AS37963 Alibaba | 771 | 17 |

**Interpretation:** Zwei „Offshore"/bulletproof-Hoster — **Pfcloud UG (11 IPs)** und
**Offshore LC (15 IPs)** — verursachen zusammen **~60 % des gesamten Traffics aus nur
26 IPs**. Die Namen (`Offshore`, `UNMANAGED`) sprechen für sich. Im Gegensatz dazu
**Google (90 IPs, nur 1'065 Events)**: breit gestreutes, niedrigfrequentes Scanning —
ein ganz anderes Muster (verteilte Aufklärung statt Dauerbeschuss). Die ASN-Sicht
trennt also „Brute-Force-Bienenstöcke" von „verteilten Scannern" — das sieht man in
der reinen Länder-Statistik nicht.

## Event-Verteilung
| Event | Anzahl |
|---|---|
| `cowrie.session.connect` | 29'410 |
| `cowrie.login.success` | 20'163 |
| `cowrie.command.input` | 20'118 |
| `cowrie.login.failed` | 217 |
| `cowrie.session.file_download` | 112 |

**Einordnung:** „success" ≫ „failed" (20'163 vs 217) heisst **nicht**, dass die Bots gute
Passwörter erraten haben — Cowrie ist als Honeypot bewusst freizügig bei der Fake-Anmeldung,
um zu beobachten, was die Angreifer *danach* tun. Die **20'118 Befehle** und **112
Datei-Downloads** (echte Malware-Nachladeversuche) sind der eigentliche Forschungswert.

## Credentials
**Top-Usernames:** `root` (5'171), `admin` (850), `user`, `ubuntu`, `deploy`, `test`,
`claude`, `pi` (Raspberry Pi), `dev`, **`minecraft`** (185 — Gameserver-Ziel!), `guest`.
→ Bots zielen auf Cloud-Server (`ubuntu`/`deploy`), IoT (`pi`) **und** Gameserver (`minecraft`).

**Top-Passwörter + Abgleich mit HaveIBeenPwned** (k-Anonymity — das echte Passwort
verlässt den Server nie, nur die ersten 5 SHA1-Zeichen). Die HIBP-Zahl ist die *globale*
Anzahl an Leaks, in denen das Passwort vorkommt:

| Passwort | Versuche | In bekannten Daten-Leaks (HIBP) |
|---|---|---|
| `123456` | 1'473 | **210'318'957** |
| `123` | 829 | 15'155'838 |
| `1234` | 666 | 30'330'441 |
| `alpine` | 632 | 132'980 |
| `1` | 545 | 3'459'449 |
| `root` | 495 | 2'260'564 |
| `12345678` | 484 | 70'550'619 |
| `password` | 440 | 52'343'151 |
| `12345` | 412 | 31'084'566 |
| `123456789` | 316 | 81'075'150 |
| `admin` | 255 | 42'154'643 |
| `abc123` | 216 | 12'990'806 |

**Interpretation:** **100 % der Top-Passwörter** stehen in HIBP — oft in zwei- bis
dreistelligen Millionenzahlen (`123456` allein 210 Mio). Die Angreifer raten nicht
kreativ, sie spielen **bekannte Leak-/Standard-Listen** durch.

## Was die Angreifer TUN (nach dem „Login")
1. **System-Fingerprinting** — mit Abstand am häufigsten: `uname -s -v -n -r -m` (17'828×,
   plus Varianten). Erster Schritt: OS + Architektur bestimmen, um das **passende
   Malware-Binary** zu wählen.
2. **Diebstahl der Passwort-Hashes** — der Befehl
   `uname -a; id; cat /etc/shadow /etc/passwd; lscpu; …` (82×) liest gezielt **`/etc/shadow`**
   (die Passwort-Hashes) und `/etc/passwd` aus → Credential-Harvesting.
3. **Hardware-Recon fürs Krypto-Mining** — Skripte lesen `MemTotal` aus `/proc/meminfo`,
   prüfen `> 1 GB` RAM, CPU-Modell, `nproc` und GPU (`lspci | grep nvidia`). Übersetzt:
   „Lohnt sich die Maschine zum Schürfen?"
4. **Malware-Nachladen** — 112 `file_download`-Events: Bots holen per `wget`/`curl`
   Payloads von externen Servern.

Man sieht **live** die feste Pipeline automatisierter SSH-Botnetze: *einloggen → System
& Hardware profilen → Credentials/Hashes abgreifen → Malware nachladen*.

## Botnet-Wellen (koordinierte Angriffe)
**39 Minuten-Fenster** mit ≥5 verschiedenen IPs, die gleichzeitig zuschlugen
(`botnet_detector.py`). Mehrere IPs, die im selben Minutenfenster mit demselben Muster
feuern, deuten auf **koordinierte Botnetz-Aktivität** hin (gemeinsame Steuerung / geteilte Listen).

## Fazit
- Ein frisch ans Internet gehängter Server wird **innerhalb von Minuten** und danach
  **dauerhaft (~400 Events/h)** automatisiert angegriffen.
- Der Beschuss ist hochkonzentriert: **~60 % aus 26 IPs zweier Offshore-Hoster.**
- Angreifer nutzen ausschliesslich **bekannte, geleakte Standard-Passwörter** (100 %
  HIBP-Treffer) — starke/zufällige Passwörter + Key-only-SSH hätten alles abgewehrt.
- Nach dem Zugang folgt eine **automatisierte Pipeline**: Fingerprinting, `/etc/shadow`-Klau,
  Mining-Recon, Malware-Download — nicht zielgerichtetes Hacking.

## Schutzmassnahmen (Defense Recommendations)
Was die Daten konkret für die Absicherung eines Servers bedeuten:
1. **SSH key-only + Root-Login aus.** 100 % der probierten Passwörter stehen in HIBP —
   jede Passwort-Anmeldung ist gegen genau diese Listen verwundbar. Mein Admin-Zugang
   ist deshalb key-only auf Port 2222, Root- und Passwort-Login deaktiviert.
2. **Keine geleakten Passwörter.** Vor der Vergabe gegen HaveIBeenPwned prüfen
   (k-Anonymity) — die Bots fahren exakt diese Korpora ab.
3. **Standard-User/Port meiden.** `root`, `admin`, `ubuntu`, `pi` werden zuerst probiert;
   SSH weg von Port 22 reduziert den Lärm massiv.
4. **Fail2Ban auf dem echten Admin-Port** verlangsamt Brute-Force (`scripts/setup_fail2ban.sh`).
5. **Patchen + minimale Angriffsfläche.** Die Recon-Skripte suchen gezielt nach lohnenden
   Zielen (RAM/GPU fürs Mining) — ein schlankes, gepatchtes System ist weniger wert.
6. **Ausgehenden Traffic einschränken.** Nach dem Zugang laden Bots Payloads per
   `wget`/`curl` nach — strikte Egress-Regeln stoppen das.

## Methodik & Grenzen
- **Methodik:** Cowrie (SSH/Telnet-Emulation) → JSON-Log → Python-Parser (rotierte Logs,
  Offset-Dedup, GeoIP+ASN via ip-api.com mit Cache) → SQLite → Flask-API → Dashboard/Analyse.
- **Grenzen:** „login.success" ist ein Cowrie-Artefakt (freizügige Fake-Auth), kein Beweis
  erratener Passwörter. GeoIP ist auf Hosting-Standort verzerrt (Länder ≠ Täter-Herkunft);
  die ASN-Sicht ist hier aussagekräftiger.

## Ethik & Rechtliches
Reiner Beobachtungs-Honeypot — **keine** Gegenangriffe, **kein** Kontakt zu
Angreifer-Systemen. IPs nur für Geolokalisierung/Mustererkennung. HIBP-Abgleich über
k-Anonymity (das rohe Passwort verlässt den Server nie). Nach Schweizer DSG sind IPs
Personendaten → die Datenbank bleibt privat (Dashboard hinter Login + HTTPS).
