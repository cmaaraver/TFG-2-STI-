# Arquitectura de red

## Direcciones

| Equipo | Interfaz | IP | Notas |
|---|---|---|---|
| Raspberry Pi 5 | eth0 (integrada) | 192.168.50.1/24 | Puerta de enlace, DHCP, DNS y NTP de la LAN privada |
| Raspberry Pi 5 | eth1 (USB-Ethernet) | DHCP del instituto | Salida a Internet |
| Raspberry Pi 5 | tailscale0 | 100.x.y.z | Acceso remoto |
| MikroTik wAP LR8 | ether1 (PoE) | 192.168.50.2/24 estática | Gateway 192.168.50.1 |
| PC de datos | eth0 | 192.168.50.5/24 estática | Gateway 192.168.50.1 |

La Raspberry hace de **router con NAT** (no de puente): así la red de sensores queda aislada de la red
del instituto y el centro solo ve un equipo (la Raspberry). Si se hiciera un puente, el wAP y el PC
quedarían expuestos en la red del instituto.

## Configuración en la Raspberry (NetworkManager, Raspberry Pi OS Bookworm)

```bash
# LAN privada: modo "shared" = IP fija + DHCP + NAT automáticos
sudo nmcli con add type ethernet ifname eth0 con-name lan-privada \
  ipv4.method shared ipv4.addresses 192.168.50.1/24 ipv6.method disabled
# Red del instituto por el adaptador USB
sudo nmcli con add type ethernet ifname eth1 con-name red-instituto ipv4.method auto
```
Comprobar el nombre real del adaptador USB con `ip link` (puede no ser `eth1`).

## Firewall (ufw)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw default allow routed
sudo ufw allow in on eth0
sudo ufw allow in on tailscale0
sudo ufw enable
```
Por eth1 (red del instituto) no entra nada. Ojo: Docker publica puertos saltándose ufw, así que
se publican solo en la IP de la LAN, p. ej. `"192.168.50.1:8080:8080"`.

## Hora (NTP)
- La Raspberry Pi 5 tiene RTC integrado; con la batería oficial mantiene la hora apagada.
- `raspberry/red/chrony.conf`: sincroniza con Internet cuando hay conexión y sirve la hora a 192.168.50.0/24.
- wAP y PC usan 192.168.50.1 como servidor NTP.
- La BD guarda la hora del servidor LoRaWAN (`time` del uplink) en UTC.

## Acceso desde fuera: por qué no DNS dinámico
No controlamos el router del instituto, así que no se pueden abrir puertos, y probablemente hay NAT
por encima. Un DNS dinámico no serviría. La solución es un túnel saliente:

- **Tailscale** (recomendado): VPN que sale hacia fuera por HTTPS, no necesita abrir puertos.
  - Raspberry como *subnet router*: `sudo tailscale up --advertise-routes=192.168.50.0/24`
  - El equipo entra a `http://192.168.50.5:3000` (Grafana) y `http://192.168.50.1:8080` (ChirpStack)
    desde cualquier sitio con la app de Tailscale.
  - Cada equipo tiene nombre DNS propio (MagicDNS), p. ej. `http://pc-datos:3000`.
- **Tailscale Funnel** (opcional): URL pública HTTPS `https://pc-datos.<red>.ts.net` para enseñar
  el panel al tribunal sin instalar nada. Solo exponer Grafana en modo lectura.
- Alternativa: Cloudflare Tunnel, si el centro tiene un dominio propio.

**Antes de conectar nada a la red del instituto hay que pedir permiso al coordinador TIC.**

## MQTT
- Listener interno 1883 (red Docker, ChirpStack y Gateway Bridge).
- Listener 1884 en la LAN con usuario/contraseña para el ingestor del PC.
- Persistencia activada y cola grande: si el PC está apagado, los mensajes esperan en la Raspberry.
- ChirpStack debe publicar los eventos con QoS 1 (si publica en QoS 0 el broker no los guarda en cola).

## Seguridad
- LoRaWAN 1.1 OTAA: claves AES-128 únicas por nodo.
- SSH solo con clave pública; sin contraseña.
- Contraseñas de ChirpStack, Grafana, MQTT y BD cambiadas y guardadas fuera del repositorio.
- WiFi del wAP desactivada (no se necesita) o con WPA2 y sin acceso a la LAN.
