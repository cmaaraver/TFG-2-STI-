# Arquitectura de red

Todo el servidor está en la **Raspberry Pi 5**: servidor LoRaWAN, MQTT, base de datos y web.
Ya no hay PC de datos.

El centro nos deja trabajar en la **VLAN 500** del instituto (decisión de 2026-10-23). El gateway LoRa
(MikroTik wAP LR8) y la Raspberry están los dos en esa VLAN con IP fija, así que se hablan
directamente: la Raspberry ya no hace de router ni de NAT y **no hace falta adaptador USB-Ethernet**.

```
 [Nodo LILYGO] ~~~ LoRaWAN EU868 ~~~ [wAP LR8]  172.16.50.2 (fija)
                                         │ PoE (inyector)
                                         │
                           ┌─────────────┴──────────────┐
                           │ switch del instituto        │  puertos en VLAN 500 sin etiquetar (acceso)
                           └──────┬───────────────┬──────┘
                                  │               │
             Raspberry Pi 5  172.16.50.3 (fija)   │ puerta de enlace 172.16.50.1
             Docker: ChirpStack, Mosquitto,       │ (router del instituto, NAT a Internet)
             TimescaleDB, ingestor, web,          │  reenvío TCP 443 (y 80) → 172.16.50.3
             Caddy, DuckDNS                       ▼
                                               Internet
                                                  │
            https://<nombre>.duckdns.org  ←  cualquier navegador o móvil
```

## Direcciones

| Equipo | Interfaz | IP | Notas |
|---|---|---|---|
| Router del instituto | VLAN 500 | 172.16.50.1 | Puerta de enlace y (en principio) DNS |
| MikroTik wAP LR8 | ether1 (PoE) | 172.16.50.2/24 fija | Puerta de enlace 172.16.50.1, NTP 172.16.50.3, servidor LoRa 172.16.50.3:1700 |
| Raspberry Pi 5 | eth0 (integrada) | 172.16.50.3/24 fija | Puerta de enlace 172.16.50.1, DNS 172.16.50.1 |
| Raspberry Pi 5 | tailscale0 | 100.x.y.z | Acceso del equipo a SSH y ChirpStack |

Supuestos que hay que confirmar con el coordinador TIC (**TODO VERIFICAR**):
- Máscara **/24** (255.255.255.0).
- Los puertos del switch donde van la Raspberry y el inyector del wAP entregan la VLAN 500
  **sin etiquetar** (modo acceso). Así ni la Raspberry ni el wAP tienen que configurar VLANs.
  Si el puerto fuera troncal (VLAN etiquetada), habría que crear en la Raspberry un interfaz
  `eth0.500` con `nmcli con add type vlan dev eth0 id 500 ...` y en el wAP una interfaz VLAN 500.
- El **DNS** es la propia puerta de enlace (172.16.50.1). Si el TIC da otro, se cambia en
  `raspberry/red/red.env` (variable `DNS`).
- Las IP **172.16.50.2 y 172.16.50.3 quedan fuera del rango del DHCP** de la VLAN 500, para que
  ningún otro equipo las coja.

Configuración: los datos están en un único fichero, `raspberry/red/red.env`, que leen
`raspberry/red/configurar-red.sh` (NetworkManager), `raspberry/red/firewall.sh` e `instalar.sh`.

Con la VLAN ya no hace falta cable directo de la Raspberry al wAP: cada uno va a un puerto del switch
(el wAP a través de su inyector PoE, que viene en el kit). Si el switch del instituto diera un PoE
compatible con el wAP se podría quitar el inyector, pero eso hay que mirarlo en la ficha de MikroTik
(**TODO VERIFICAR**); mientras tanto se usa el inyector.

## Servicios y puertos

| Servicio | Puerto | Desde dónde se llega |
|---|---|---|
| Web (Caddy → web) | TCP 443 HTTPS, TCP 80 | Internet (DuckDNS), red del instituto, Tailscale |
| Gateway Bridge | UDP 1700 | Solo desde el wAP (172.16.50.2). Bloqueado para el resto de la VLAN |
| ChirpStack (web de administración) | TCP 8080 | Solo `127.0.0.1`; el equipo entra con `tailscale serve` |
| Mosquitto (MQTT) | 1883 | Solo dentro de Docker, no se publica |
| TimescaleDB | 5432 | Solo dentro de Docker, no se publica |
| NTP (chrony) | UDP 123 | Solo el wAP (172.16.50.2) |
| SSH | TCP 22 | VLAN 500 (solo con clave) y Tailscale. Nunca desde Internet |

## DuckDNS y acceso desde Internet

1. Crear la cuenta en https://www.duckdns.org (con la cuenta de Google o GitHub del equipo),
   elegir el subdominio (p. ej. `calidad-agua-viveros`) y copiar el **token** al `.env`.
2. El contenedor `duckdns` actualiza cada 5 minutos la IP pública con la que sale el instituto.
   DuckDNS apunta a la IP pública del centro, no a la 172.16.50.3.
3. El contenedor `caddy` saca el certificado HTTPS de Let's Encrypt **por DNS** (reto DNS-01 con el
   token de DuckDNS), así que funciona aunque el puerto 80 esté cerrado.
4. **Para entrar desde fuera hace falta que el coordinador TIC**:
   - deje **172.16.50.2 y 172.16.50.3 fuera del DHCP** de la VLAN 500 (la Raspberry ya tiene IP fija,
     así que el reenvío de puertos siempre apunta a ella);
   - **reenvíe el puerto TCP 443** (y el 80 si quiere) de la IP pública del centro a `172.16.50.3`.
   - Si el centro sale a Internet por CGNAT o por la red de la Junta sin IP pública propia,
     el reenvío es imposible. Entonces se usa el **plan B**.
5. **Dentro del instituto** muchas veces el router no deja entrar a la IP pública desde dentro
   (NAT loopback). Para verlo desde el aula: `http://172.16.50.3` (desde un equipo con acceso a la VLAN 500).

### Plan B sin abrir puertos: Tailscale Funnel
Si no se puede abrir el 443, la web se publica con Tailscale, que sale hacia fuera:
```bash
sudo tailscale funnel --bg 80
```
La web queda en `https://<nombre-raspberry>.<red>.ts.net`, con HTTPS y sin tocar el router.
El dominio DuckDNS no se usaría en ese caso.

## Acceso del equipo (administración)
- Tailscale en la Raspberry y en los portátiles o móviles del equipo: `sudo tailscale up`.
- ChirpStack solo para el tailnet: `sudo tailscale serve --bg --https=8443 http://127.0.0.1:8080`
  → `https://<nombre-raspberry>.<red>.ts.net:8443`.
- SSH por la IP de Tailscale (100.x.y.z).

## Hora (NTP)
- La Raspberry Pi 5 tiene RTC; con la batería oficial mantiene la hora apagada.
- `raspberry/red/chrony.conf`: coge la hora de Internet y se la sirve al wAP (172.16.50.2).
  Si el TIC tiene un servidor NTP propio (a veces la misma 172.16.50.1), se puede añadir como fuente.
- La base de datos guarda todo en UTC; la web lo enseña en hora de Madrid.

## Firewall
`raspberry/red/firewall.sh`:
Como la Raspberry comparte la VLAN con otros equipos del instituto, se filtra por **IP de origen**:
- ufw: se deniega todo lo entrante salvo Tailscale, 80/443 (la web), SSH desde la VLAN 500
  y NTP solo desde el wAP.
- Docker publica puertos saltándose ufw. Por eso el UDP 1700 se limita al wAP (172.16.50.2) con una
  regla en la cadena `DOCKER-USER` (servicio `docker-user-reglas`), y ChirpStack solo escucha en `127.0.0.1`.

## Seguridad
- LoRaWAN 1.1 OTAA: claves AES-128 únicas por nodo.
- SSH solo con clave pública, sin contraseña, y no expuesto a Internet.
- La web es de solo lectura: entra a la base de datos con el usuario `web_lector`, que no puede
  modificar nada.
- Contraseñas y token de DuckDNS en `raspberry/.env`, que no se sube a git.
- WiFi del wAP desactivada y su administración (WinBox/web) protegida con contraseña, porque ahora
  está en una VLAN compartida.
- **Antes de conectar nada a la red del instituto hay que pedir permiso al coordinador TIC.**
