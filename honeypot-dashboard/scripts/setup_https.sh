#!/usr/bin/env bash
# nginx as HTTPS reverse proxy in front of the dashboard (self-signed cert, no domain).
set -euo pipefail

apt-get update -qq
apt-get install -y nginx openssl

mkdir -p /etc/nginx/ssl
if [ ! -f /etc/nginx/ssl/honeypot.crt ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/honeypot.key \
        -out /etc/nginx/ssl/honeypot.crt \
        -subj "/CN=honeypot"
fi

cp /opt/honeypot/nginx/honeypot.conf /etc/nginx/sites-available/honeypot
ln -sf /etc/nginx/sites-available/honeypot /etc/nginx/sites-enabled/honeypot
rm -f /etc/nginx/sites-enabled/default

if command -v ufw >/dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

nginx -t
systemctl restart nginx
echo "nginx HTTPS reverse proxy active on :443 (self-signed)"
