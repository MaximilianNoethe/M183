#!/usr/bin/env bash
# Fail2Ban for the REAL admin SSH on port 2222 only — the honeypot ports stay open.
set -euo pipefail

apt-get update -qq
apt-get install -y fail2ban

cat > /etc/fail2ban/jail.d/honeypot-admin-ssh.local <<'EOF'
[sshd]
enabled  = true
port     = 2222
maxretry = 4
findtime = 10m
bantime  = 1h
EOF

systemctl enable --now fail2ban
systemctl restart fail2ban
fail2ban-client status sshd || true
echo "fail2ban active on admin SSH :2222"
