#!/bin/bash
# Configura la red de la Raspberry con NetworkManager (Raspberry Pi OS Bookworm o posterior).
# La Raspberry y el wAP LR8 están los dos en la VLAN 500 del instituto, así que basta con UN
# interfaz (eth0, el integrado) con IP fija. Ya no hay red privada, ni NAT, ni adaptador USB.
# Los datos (IP, máscara, puerta de enlace, DNS) están en red.env.
#
# OJO (CLAUDE.md, regla 8): si se ejecuta por SSH y la Raspberry todavía tiene otra IP (la que le
# dio el DHCP), al aplicar la IP fija se corta la sesión. Por eso, en ese caso, el perfil se deja
# preparado y se aplica al reiniciar; después se entra por SSH a la IP fija.
# Se puede ejecutar varias veces: si el perfil ya existe, se modifica en vez de duplicarse.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source ./red.env

NOMBRE=red-vlan500
if nmcli -t -f NAME con show | grep -qx "$NOMBRE"; then
  sudo nmcli con modify "$NOMBRE" connection.interface-name "$IF_RED"
else
  sudo nmcli con add type ethernet ifname "$IF_RED" con-name "$NOMBRE"
fi
sudo nmcli con modify "$NOMBRE" \
  ipv4.method manual ipv4.addresses "$IP_RASPBERRY/$PREFIJO" \
  ipv4.gateway "$PUERTA_ENLACE" ipv4.dns "$DNS" ipv4.ignore-auto-dns yes \
  ipv6.method disabled \
  connection.autoconnect yes connection.autoconnect-priority 20

# El perfil que crea Raspberry Pi OS por defecto (DHCP) se deja sin arranque automático
# para que no compita con el nuestro en el mismo puerto.
nmcli -t -f NAME,DEVICE con show | awk -F: -v n="$NOMBRE" -v d="$IF_RED" '$1!=n && $2==d {print $1}' |
  while read -r otro; do sudo nmcli con modify "$otro" connection.autoconnect no; done

ip_actual="$(ip -4 -o addr show "$IF_RED" | awk '{print $4}' | cut -d/ -f1 | head -n1)"
if [ -n "${SSH_CONNECTION:-}" ] && [ -n "$ip_actual" ] && [ "$ip_actual" != "$IP_RASPBERRY" ]; then
  echo "Estás por SSH con la IP $ip_actual: el perfil $NOMBRE se aplicará al reiniciar."
  echo "Después: ssh $(id -un)@$IP_RASPBERRY"
  exit 0
fi
sudo nmcli con up "$NOMBRE"
ip -4 addr show "$IF_RED"
ip route | grep default
