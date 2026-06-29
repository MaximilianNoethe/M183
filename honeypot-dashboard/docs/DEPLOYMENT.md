# Deployment-Runbook (Server)

Schritt-für-Schritt, wie der Stack auf dem Kamatera-VPS läuft. Lokales Setup steht im
README-Quickstart; das hier ist der echte Server.

> Repo liegt unter `/opt/M183`, Symlink `/opt/honeypot → /opt/M183/honeypot-dashboard`.
> Das Repo gehört `root` → Git-Befehle auf dem Server immer mit `sudo`.
> Admin-SSH: `ssh -p 2222 max@<SERVER_IP>` (key-only).

## 1. Honeypot (Woche 1)
```bash
sudo bash /opt/honeypot/scripts/setup_server.sh   # SSH→2222, UFW, iptables NAT 22/23→2223/2224
sudo bash /opt/honeypot/scripts/setup_cowrie.sh   # Cowrie im eigenen venv, JSON-Logs
sudo cp /opt/honeypot/systemd/honeypot-cowrie.service /etc/systemd/system/
sudo systemctl enable --now honeypot-cowrie.service
```

## 2. Parser + DB (Woche 2)
```bash
sudo mkdir -p /var/lib/honeypot && sudo chown cowrie:cowrie /var/lib/honeypot
sudo python3 -m venv /opt/honeypot/.venv
sudo /opt/honeypot/.venv/bin/pip install -r /opt/honeypot/requirements.txt
sudo cp /opt/honeypot/.env.example /opt/honeypot/.env   # DATABASE_PATH=/var/lib/honeypot/honeypot.db etc.
sudo chown root:cowrie /opt/honeypot/.env && sudo chmod 640 /opt/honeypot/.env

# Timer alle 5 Min
sudo cp /opt/honeypot/systemd/honeypot-parser.{service,timer} /etc/systemd/system/
sudo systemctl enable --now honeypot-parser.timer
```
Prüfen: `sudo -u cowrie sqlite3 /var/lib/honeypot/honeypot.db "SELECT COUNT(*) FROM attacks;"`

## 3. API + Dashboard (Woche 3/4)
```bash
sudo cp /opt/honeypot/systemd/honeypot-api.service /etc/systemd/system/
sudo systemctl enable --now honeypot-api.service     # lauscht 127.0.0.1:8080
```
Ansehen per SSH-Tunnel: `ssh -p 2222 -L 8080:127.0.0.1:8080 max@<SERVER_IP>` → http://localhost:8080
Health-Check: `curl -s http://127.0.0.1:8080/api/health`

## 4. HTTPS + Fail2Ban (Woche 6)
```bash
sudo bash /opt/honeypot/scripts/setup_https.sh       # nginx + selbstsigniertes Zertifikat, :443
sudo bash /opt/honeypot/scripts/setup_fail2ban.sh    # Jail nur auf Admin-SSH :2222
```

## Code aktualisieren
```bash
sudo git -C /opt/honeypot pull
sudo systemctl restart honeypot-api.service
# bei Parser-Änderungen greift der Timer beim nächsten Lauf automatisch
```

## Logs / Debugging
```bash
sudo systemctl status honeypot-api.service
sudo journalctl -u honeypot-api.service -n 50
sudo systemctl list-timers | grep honeypot
```

## ⚠️ Kamatera-Trial
Server vor Trial-Ende (~30 Tage nach Bestellung) **löschen**, sonst wird abgerechnet.
