#!/usr/bin/env bash
#
# setup_server.sh — Week 1 VPS hardening for the honeypot host.
#
# Run as root on a fresh Hetzner CX22 / Ubuntu 22.04 box, ONCE, after you have
# already added your SSH public key to the server.
#
# What it does:
#   1. Moves real admin SSH to port 2222, key-only, root login disabled
#   2. Configures UFW: allow 22 + 23 (Cowrie), 2222 (real SSH), 8080 (dashboard)
#   3. Redirects public port 22 -> Cowrie's 2222 via iptables NAT (Cowrie listens
#      on an unprivileged port; this NAT comes AFTER real SSH has moved off 22)
#   4. Installs base packages
#
# IMPORTANT — read before running:
#   - Keep your current SSH session OPEN until you've confirmed you can log in
#     on the NEW port 2222. A mistake here can lock you out.
#   - This script is idempotent-ish but assumes a fresh box. Review every step.
#
# Usage:  sudo bash setup_server.sh

set -euo pipefail

REAL_SSH_PORT=2222
DASHBOARD_PORT=8080
SSHD_CONFIG="/etc/ssh/sshd_config"

log()  { printf '\033[0;32m[setup]\033[0m %s\n' "$*"; }
warn() { printf '\033[0;33m[warn]\033[0m %s\n' "$*"; }

require_root() {
    if [[ "${EUID}" -ne 0 ]]; then
        echo "Must run as root (use sudo)." >&2
        exit 1
    fi
}

confirm_key_present() {
    # Refuse to disable password auth if no authorized_keys exists — that would
    # lock the operator out.
    local user_home
    user_home="$(eval echo "~${SUDO_USER:-root}")"
    if [[ ! -s "${user_home}/.ssh/authorized_keys" ]] && [[ ! -s /root/.ssh/authorized_keys ]]; then
        echo "No authorized_keys found. Add your SSH public key BEFORE running this." >&2
        exit 1
    fi
}

install_packages() {
    log "Installing base packages..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y ufw iptables-persistent fail2ban python3-venv python3-pip git curl
}

harden_ssh() {
    log "Hardening SSH -> port ${REAL_SSH_PORT}, key-only, no root login..."
    cp "${SSHD_CONFIG}" "${SSHD_CONFIG}.bak.$(date +%s 2>/dev/null || echo backup)"

    # Apply settings idempotently: replace if present, else append.
    set_sshd() {
        local key="$1" val="$2"
        if grep -qE "^\s*#?\s*${key}\b" "${SSHD_CONFIG}"; then
            sed -i "s|^\s*#\?\s*${key}\b.*|${key} ${val}|" "${SSHD_CONFIG}"
        else
            echo "${key} ${val}" >> "${SSHD_CONFIG}"
        fi
    }

    set_sshd Port "${REAL_SSH_PORT}"
    set_sshd PermitRootLogin no
    set_sshd PasswordAuthentication no
    set_sshd PubkeyAuthentication yes
    set_sshd ChallengeResponseAuthentication no
    set_sshd X11Forwarding no

    warn "SSH will restart on port ${REAL_SSH_PORT}. Keep this session open and"
    warn "test 'ssh -p ${REAL_SSH_PORT} user@host' in a NEW terminal before closing."
    systemctl restart ssh
}

configure_firewall() {
    log "Configuring UFW..."
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp    comment 'Cowrie SSH honeypot'
    ufw allow 23/tcp    comment 'Cowrie Telnet honeypot'
    ufw allow "${REAL_SSH_PORT}/tcp" comment 'Real admin SSH'
    ufw allow "${DASHBOARD_PORT}/tcp" comment 'Dashboard (pre-HTTPS)'
    ufw --force enable
    ufw status verbose
}

redirect_to_cowrie() {
    # Cowrie listens on 2223 (SSH) / 2224 (Telnet) as an unprivileged service.
    # Public 22/23 are NAT-redirected to those ports. Real admin SSH is on 2222
    # and is NOT touched here.
    log "Setting up iptables NAT: 22 -> 2223, 23 -> 2224 (Cowrie)..."
    iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2223
    iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2224
    netfilter-persistent save
    log "NAT rules saved."
}

main() {
    require_root
    confirm_key_present
    install_packages
    harden_ssh
    configure_firewall
    redirect_to_cowrie
    log "Server hardening complete. Next: run setup_cowrie.sh"
    warn "Confirm SSH on port ${REAL_SSH_PORT} works in a NEW session before logging out!"
}

main "$@"
