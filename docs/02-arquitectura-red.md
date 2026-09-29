# Arquitectura de red

Todo el servidor está en la **Raspberry Pi 5**: servidor LoRaWAN, MQTT, base de datos y web.
Ya no hay PC de datos.

```
 [Nodo LILYGO] ~~~ LoRaWAN EU868 ~~~ [wAP LR8]
                                         │ PoE (inyector)
                                         │ 192.168.50.2
                          ┌──────────────┴──────────────┐
                          │ eth0  192.168.50.1 (fija)   │  red privada del gateway
                          │                             │
                          │      RASPBERRY PI 5         │  Docker: ChirpStack, Mosquitto,
                          │                             │  TimescaleDB, ingestor, web, Caddy, DuckDNS
                          │ eth1  192.168.155.x (DHCP)  │  red del instituto (adaptador USB)
                          └──────────────┬──────────────┘
                                         │
                             router del instituto (NAT)
                                         │  reenvío TCP 443 (y 80) → Raspberry
                                      Internet
                                         │
            https://<nombre>.duckdns.org  ←  cualquier navegador o móvil
```

## Direcciones

| Equipo | Interfaz | IP | Notas |
|---|---|---|---|
| Raspberry Pi 5 | eth0 (integrada) | 192.168.50.1/24 fija | Puerta de enlace, DHCP y NTP de la red privada |
| Raspberry Pi 5 | eth1 (USB-Ethernet) | 192.168.155.x por DHCP | Red del instituto (**TODO VERIFICAR** la subred con el coordinador TIC) |
| Raspberry Pi 5 | tailscale0 | 100.x.y.z | Acceso del equipo a SSH y ChirpStack |
| MikroTik wAP LR8 | ether1 (PoE) | 192.168.50.2/24 fija | Gateway 192.168.50.1, NTP 192.168.50.1 |

- La Raspberry hace de **router con NAT** entre las dos redes: el instituto solo ve un equipo
  (la Raspberry) y el wAP queda aislado.
- Con solo el wAP en la red privada **no hace falta switch**: cable directo Raspberry → inyector PoE → wAP.
  Un switch solo sirve si se quiere enchufar un portátil a la red privada.
- Configuración: `raspberry/red/configurar-red.sh` (NetworkManager). Comprobar antes los nombres
  de las interfaces con `ip link`.

## Servicios y puertos

| Servicio | Puerto | Desde dónde se llega |
|---|---|---|
| Web (Caddy → web) | TCP 443 HTTPS, TCP 80 | Internet (DuckDNS), red del instituto, Tailscale |
| Gateway Bridge | UDP 1700 | Solo red privada (el wAP). Bloqueado desde el instituto |
| ChirpStack (web de administración) | TCP 8080 | Solo `127.0.0.1`; el equipo entra con `tailscale serve` |
| Mosquitto (MQTT) | 1883 | Solo dentro de Docker, no se publica |
| TimescaleDB | 5432 | Solo dentro de Docker, no se publica |
| SSH | TCP 22 | Red privada, red del instituto (solo con clave) y Tailscale. Nunca desde Internet |

## DuckDNS y acceso desde Internet

1. Crear la cuenta en https://www.duckdns.org (con la cuenta de Google o GitHub del equipo),
   elegir el subdominio (p. ej. `calidad-agua-viveros`) y copiar el **token** al `.env`.
2. El contenedor `duckdns` actualiza cada 5 minutos la IP pública con la que sale el instituto.
   Que la Raspberry tenga IP por DHCP no afecta a DuckDNS, porque DuckDNS apunta a la IP pública.
3. El contenedor `caddy` saca el certificado HTTPS de Let's Encrypt **por DNS** (reto DNS-01 con el
   token de DuckDNS), así que funciona aunque el puerto 80 esté cerrado.
4. **Para entrar desde fuera hace falta que el coordinador TIC**:
   - **reserve la IP** de la Raspberry en su DHCP (por la MAC del adaptador USB). Si la IP cambia,
     el reenvío de puertos deja de apuntar a la Raspberry. Por eso sí importa que sea siempre la misma;
   - **reenvíe el puerto TCP 443** (y el 80 si quiere) de la IP pública del centro a esa IP.
   - Si el centro sale a Internet por CGNAT o por la red de la Junta sin IP pública propia,
     el reenvío es imposible. Entonces se usa el **plan B**.
5. **Dentro del instituto** muchas veces el router no deja entrar a la IP pública desde dentro
   (NAT loopback). Para verlo desde el aula: `http://<ip-de-la-raspberry>`.

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
- `raspberry/red/chrony.conf`: coge la hora de Internet y la sirve a 192.168.50.0/24 (el wAP).
- La base de datos guarda todo en UTC; la web lo enseña en hora de Madrid.

## Firewall
`raspberry/red/firewall.sh`:
- ufw: se deniega todo lo entrante salvo red privada, Tailscale y 80/443 desde el instituto.
- Docker publica puertos saltándose ufw. Por eso el UDP 1700 se bloquea desde la red del
  instituto con una regla en la cadena `DOCKER-USER` (servicio `docker-user-reglas`), y
  ChirpStack solo escucha en `127.0.0.1`.

## Seguridad
- LoRaWAN 1.1 OTAA: claves AES-128 únicas por nodo.
- SSH solo con clave pública, sin contraseña, y no expuesto a Internet.
- La web es de solo lectura: entra a la base de datos con el usuario `web_lector`, que no puede
  modificar nada.
- Contraseñas y token de DuckDNS en `raspberry/.env`, que no se sube a git.
- WiFi del wAP desactivada.
- **Antes de conectar nada a la red del instituto hay que pedir permiso al coordinador TIC.**
