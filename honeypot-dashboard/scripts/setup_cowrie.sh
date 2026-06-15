#!/usr/bin/env bash
#
# setup_cowrie.sh — Week 1 Cowrie honeypot install + config.
#
# Run as root AFTER setup_server.sh, on the VPS. Installs Cowrie under a
# dedicated unprivileged user, into a Python venv, with JSON logging enabled
# and SSH/Telnet listeners on the unprivileged ports that the iptables NAT
# (from setup_server.sh) redirects public 22/23 to.
#
# Cowrie listens on:  SSH 2223, Telnet 2224   (public 22/23 -> these via NAT)
#
# Usage:  sudo bash setup_cowrie.sh

set -euo pipefail

COWRIE_USER="cowrie"
COWRIE_HOME="/opt/honeypot/cowrie"
COWRIE_REPO="https://github.com/cowrie/cowrie.git"
FAKE_HOSTNAME="srv-prod-01"

log()  { printf '\033[0;32m[cowrie]\033[0m %s\n' "$*"; }
warn() { printf '\033[0;33m[warn]\033[0m %s\n' "$*"; }

require_root() {
    if [[ "${EUID}" -ne 0 ]]; then
        echo "Must run as root (use sudo)." >&2
        exit 1
    fi
}

create_user() {
    if ! id "${COWRIE_USER}" &>/dev/null; then
        log "Creating unprivileged user '${COWRIE_USER}'..."
        adduser --disabled-password --gecos "" "${COWRIE_USER}"
    else
        log "User '${COWRIE_USER}' already exists."
    fi
    # Create the install dir itself and hand it to cowrie. (chown -R on the
    # parent doesn't follow the /opt/honeypot symlink, so target it directly.)
    mkdir -p "${COWRIE_HOME}"
    chown -R "${COWRIE_USER}:${COWRIE_USER}" "${COWRIE_HOME}"
}

install_deps() {
    log "Installing Cowrie system dependencies..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y git python3-venv python3-pip python3-dev libssl-dev libffi-dev build-essential
}

clone_and_build() {
    log "Cloning Cowrie and building venv (as ${COWRIE_USER})..."
    sudo -u "${COWRIE_USER}" bash <<EOF
set -euo pipefail
if [[ ! -d "${COWRIE_HOME}/.git" ]]; then
    git clone "${COWRIE_REPO}" "${COWRIE_HOME}"
fi
cd "${COWRIE_HOME}"
python3 -m venv cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .   # installs cowrie itself + the twistd plugin / launcher
EOF
}

write_config() {
    log "Writing cowrie.cfg (JSON logging, fake hostname '${FAKE_HOSTNAME}', ports 2223/2224)..."
    sudo -u "${COWRIE_USER}" tee "${COWRIE_HOME}/etc/cowrie.cfg" >/dev/null <<EOF
[honeypot]
hostname = ${FAKE_HOSTNAME}
log_path = var/log/cowrie
download_path = var/lib/cowrie/downloads
ttylog = true

[ssh]
enabled = true
listen_endpoints = tcp:2223:interface=0.0.0.0

[telnet]
enabled = true
listen_endpoints = tcp:2224:interface=0.0.0.0

# JSON output — this is what the Week 2 parser reads.
[output_jsonlog]
enabled = true
logfile = \${honeypot:log_path}/cowrie.json
epoch_timestamp = false
EOF
}

install_service() {
    # Installs the systemd unit shipped in this repo (copied to the box).
    log "Installing systemd service for Cowrie..."
    if [[ -f /opt/honeypot/systemd/honeypot-cowrie.service ]]; then
        cp /opt/honeypot/systemd/honeypot-cowrie.service /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable --now honeypot-cowrie.service
        systemctl status honeypot-cowrie.service --no-pager || true
    else
        warn "honeypot-cowrie.service not found under /opt/honeypot/systemd/."
        warn "Copy the repo's systemd/ dir to the box, then re-run this step."
    fi
}

main() {
    require_root
    install_deps
    create_user
    clone_and_build
    write_config
    install_service
    log "Cowrie install complete."
    log "Verify within ~60 min:  tail -f ${COWRIE_HOME}/var/log/cowrie/cowrie.json"
    log "Look for 'cowrie.login.failed' events from real attackers."
}

main "$@"
