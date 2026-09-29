#!/bin/bash
# Firewall de la Raspberry.
# - ufw protege los servicios del propio sistema (SSH, NTP...).
# - Los puertos que publica Docker se saltan ufw, así que el UDP 1700 del Gateway Bridge
#   se bloquea desde la red del instituto en la cadena DOCKER-USER (servicio docker-user-reglas).
set -euo pipefail
IF_LORA=${IF_LORA:-eth0}
IF_INSTITUTO=${IF_INSTITUTO:-eth1}

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw default allow routed                    # NAT de la red privada hacia Internet
sudo ufw allow in on "$IF_LORA"                  # wAP y equipos de la red privada
sudo ufw allow in on tailscale0                  # el equipo, por Tailscale (SSH, ChirpStack)
sudo ufw allow in on "$IF_INSTITUTO" to any port 80,443 proto tcp   # la web
sudo ufw --force enable

# Regla para los puertos de Docker (se vuelve a poner en cada arranque)
sudo tee /etc/systemd/system/docker-user-reglas.service >/dev/null <<UNIT
[Unit]
Description=Bloquear el Gateway Bridge (UDP 1700) desde la red del instituto
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/sh -c 'iptables -C DOCKER-USER -i $IF_INSTITUTO -p udp --dport 1700 -j DROP 2>/dev/null || iptables -I DOCKER-USER -i $IF_INSTITUTO -p udp --dport 1700 -j DROP'

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now docker-user-reglas.service
sudo ufw status verbose
sudo iptables -L DOCKER-USER -n
