#!/bin/bash
# Configura las dos redes de la Raspberry con NetworkManager (Raspberry Pi OS Bookworm o posterior).
#   IF_LORA:      puerto integrado, va al inyector PoE del wAP LR8 → red privada 192.168.50.0/24
#   IF_INSTITUTO: adaptador USB-Ethernet, va a la red del instituto (192.168.155.x por DHCP)
# Comprobar los nombres con "ip link" antes de ejecutar. Si se hace por SSH, entrar por el
# adaptador USB (IF_INSTITUTO), nunca por IF_LORA: al cambiarla te quedas fuera (CLAUDE.md, regla 8).
# Se puede ejecutar varias veces: si los perfiles ya existen, se modifican en vez de duplicarse.
set -euo pipefail
IF_LORA=${IF_LORA:-eth0}
IF_INSTITUTO=${IF_INSTITUTO:-eth1}

# crear_o_modificar <nombre> <interfaz> <opciones de nmcli...>
crear_o_modificar() {
  local nombre="$1" interfaz="$2"; shift 2
  if nmcli -t -f NAME con show | grep -qx "$nombre"; then
    sudo nmcli con modify "$nombre" connection.interface-name "$interfaz" "$@"
  else
    sudo nmcli con add type ethernet ifname "$interfaz" con-name "$nombre" "$@"
  fi
}

# Red privada del gateway: IP fija + DHCP + NAT automáticos (modo "shared")
crear_o_modificar red-lora "$IF_LORA" \
  ipv4.method shared ipv4.addresses 192.168.50.1/24 ipv6.method disabled \
  connection.autoconnect yes connection.autoconnect-priority 20

# Red del instituto por DHCP. Se pide al coordinador TIC que reserve la IP para la MAC
# del adaptador (se ve con "ip link show $IF_INSTITUTO"), así el reenvío de puertos no se rompe.
crear_o_modificar red-instituto "$IF_INSTITUTO" \
  ipv4.method auto ipv6.method auto \
  connection.autoconnect yes connection.autoconnect-priority 10

sudo nmcli con up red-lora
# Si el adaptador del instituto ya tiene IP (por ejemplo, estamos entrando por él con SSH) no se
# reinicia ahora para no cortar la sesión: el perfil nuevo se usa solo en el siguiente arranque.
if ip -4 addr show "$IF_INSTITUTO" | grep -q "inet "; then
  echo "$IF_INSTITUTO ya tiene IP: el perfil red-instituto se aplicará al reiniciar."
else
  sudo nmcli con up red-instituto
fi
ip -4 addr show "$IF_LORA"
ip -4 addr show "$IF_INSTITUTO"
