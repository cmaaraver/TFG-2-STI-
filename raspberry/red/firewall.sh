#!/bin/bash
# Firewall de la Raspberry.
# Ahora el wAP y la Raspberry comparten la VLAN 500 con el resto de equipos del instituto,
# así que se filtra por IP de origen en vez de por interfaz:
# - ufw protege los servicios del propio sistema (SSH, NTP...).
# - Los puertos que publica Docker se saltan ufw, así que el UDP 1700 del Gateway Bridge se
#   limita al wAP en la cadena DOCKER-USER (servicio docker-user-reglas).
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source ./red.env
RED="$(python3 -c "import ipaddress; print(ipaddress.ip_interface('$IP_RASPBERRY/$PREFIJO').network)")"

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow in on tailscale0                                 # el equipo, por Tailscale (SSH, ChirpStack)
sudo ufw allow 80,443/tcp                                       # la web (instituto e Internet)
sudo ufw allow from "$RED" to any port 22 proto tcp             # SSH desde la VLAN (solo con clave)
sudo ufw allow from "$IP_WAP" to any port 123 proto udp         # NTP para el wAP
sudo ufw --force enable

# Regla para los puertos de Docker (se vuelve a poner en cada arranque)
sudo tee /etc/systemd/system/docker-user-reglas.service >/dev/null <<UNIT
[Unit]
Description=Gateway Bridge (UDP 1700) solo desde el wAP LR8 ($IP_WAP)
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/sh -c 'iptables -C DOCKER-USER -i $IF_RED -p udp --dport 1700 ! -s $IP_WAP -j DROP 2>/dev/null || iptables -I DOCKER-USER -i $IF_RED -p udp --dport 1700 ! -s $IP_WAP -j DROP'

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable docker-user-reglas.service
sudo systemctl restart docker-user-reglas.service
sudo ufw status verbose
sudo iptables -L DOCKER-USER -n
