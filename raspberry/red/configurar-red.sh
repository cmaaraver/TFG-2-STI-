#!/bin/bash
# Configura las dos redes de la Raspberry con NetworkManager (Raspberry Pi OS Bookworm).
#   IF_LORA:      puerto integrado, va al inyector PoE del wAP LR8 → red privada 192.168.50.0/24
#   IF_INSTITUTO: adaptador USB-Ethernet, va a la red del instituto (192.168.155.x por DHCP)
# Comprobar los nombres con "ip link" antes de ejecutar. Hacerlo con teclado y monitor
# conectados (CLAUDE.md, regla 8): si algo falla por SSH, te quedas fuera.
set -euo pipefail
IF_LORA=${IF_LORA:-eth0}
IF_INSTITUTO=${IF_INSTITUTO:-eth1}

# Red privada del gateway: IP fija + DHCP + NAT automáticos (modo "shared")
sudo nmcli con add type ethernet ifname "$IF_LORA" con-name red-lora \
  ipv4.method shared ipv4.addresses 192.168.50.1/24 ipv6.method disabled

# Red del instituto por DHCP. Se pide al coordinador TIC que reserve la IP para la MAC
# del adaptador (se ve con "ip link show $IF_INSTITUTO"), así el reenvío de puertos no se rompe.
sudo nmcli con add type ethernet ifname "$IF_INSTITUTO" con-name red-instituto \
  ipv4.method auto ipv6.method auto connection.autoconnect-priority 10

sudo nmcli con up red-lora
sudo nmcli con up red-instituto
ip -4 addr show "$IF_LORA"
ip -4 addr show "$IF_INSTITUTO"
