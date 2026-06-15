#!/usr/bin/env bash
# VPS hardening: admin SSH -> 2222 (key-only), UFW, NAT 22/23 -> Cowrie.
# Run as root once. Keep your session open and test port 2222 before logout.

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
    # NAT rewrites 22/23 -> 2223/2224 before filtering, so allow those too
    ufw allow 2223/tcp  comment 'Cowrie SSH (NAT target)'
    ufw allow 2224/tcp  comment 'Cowrie Telnet (NAT target)'
    ufw allow "${REAL_SSH_PORT}/tcp" comment 'Real admin SSH'
    ufw allow "${DASHBOARD_PORT}/tcp" comment 'Dashboard (pre-HTTPS)'
    ufw --force enable
    ufw status verbose
}

redirect_to_cowrie() {
    # public 22/23 -> Cowrie's 2223/2224; real admin SSH (2222) untouched
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
