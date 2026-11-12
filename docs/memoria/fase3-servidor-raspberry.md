# Fase 3 — Puesta en marcha del servidor en la Raspberry Pi 5

Fecha: 29 de octubre de 2026. Lugar: aula, Raspberry conectada a una toma del switch en la VLAN 500.

## 1. Punto de partida

- Raspberry Pi 5 con Raspberry Pi OS Lite 64 bits (Debian 13 *trixie*), nombre `rpi-lora`, usuario `charlie`.
- La Raspberry había cogido por DHCP la IP **172.16.50.27**. El nombre `rpi-lora.local` no se resolvía desde el PC,
  así que la encontramos en la tabla ARP del PC por el prefijo de la MAC (`2c:cf:67`, de Raspberry Pi Ltd):

  ```
  arp -a
  ```

- El repositorio se copió a la Raspberry en `/home/charlie/TFG`.

## 2. IP fija con NetworkManager

Se usó el script del repositorio, que lee los datos de `raspberry/red/red.env`:

```
cd ~/TFG/raspberry
./red/configurar-red.sh
```

Como estábamos conectados por SSH a la IP del DHCP, el script solo deja preparado el perfil `red-vlan500`
(172.16.50.3/24, puerta de enlace 172.16.50.1) y desactiva el arranque automático del perfil antiguo
`netplan-eth0`. Para aplicarlo sin reiniciar, y sin que se cortara a medias, se programó para 5 segundos después:

```
sudo systemd-run --unit=cambio-ip --on-active=5 nmcli con up red-vlan500
```

Después se entró por `ssh charlie@172.16.50.3` y se comprobó:

```
ip -4 -br addr show eth0      → 172.16.50.3/24
ip route                      → default via 172.16.50.1
ping -c3 1.1.1.1              → 0 % de pérdida
ping -c3 google.com           → 0 % de pérdida
```

Antes de cambiar nada se comprobó que nadie usaba la 172.16.50.3 (`ping` sin respuesta e `ip neigh` en `INCOMPLETE`).
Para no quedarnos fuera (regla 8) teníamos teclado y monitor a mano: con `sudo nmcli con up netplan-eth0`
se volvía a la IP del DHCP.

## 3. Instalación completa con `instalar.sh`

```
cd ~/TFG/raspberry
./instalar.sh
```

El script se ejecuta con el usuario normal (sin `sudo`) y hace todo: actualiza el sistema, limita el diario,
pone la zona horaria, instala Docker, configura la red y chrony, genera el `.env` con contraseñas aleatorias,
arranca los contenedores, da de alta la aplicación y el nodo en ChirpStack (deja `secrets.h` escrito), pone el
firewall, programa la copia diaria e instala Tailscale con la web pública.

Respuestas que se dieron:
- EUI del wAP: vacío (todavía no está conectado; se da de alta después).
- Batería RTC oficial: **no** (activar la carga con una pila normal la puede estropear).

En Tailscale hubo que abrir dos enlaces con la cuenta del equipo: uno para dar de alta la Raspberry y otro para
activar *Serve* en el tailnet. Después se desactivó el *key expiry* de `rpi-lora` en la consola
(Machines → `rpi-lora` → *Disable key expiry*).

## 4. Problemas encontrados

| Problema | Qué se veía | Causa | Solución |
|---|---|---|---|
| No se podía hacer SSH desde el PC | `connect to host … port 22: Permission denied` y el ping daba `fallo general` | La VPN WireGuard del PC tenía activado el *kill-switch*, que bloquea la red local | En WireGuard, desmarcar "Block untunneled traffic (kill-switch)" |
| El DNS de la VLAN no funciona | `docker build` fallaba con `lookup … on 172.16.50.1:53: connection refused` | 172.16.50.1 es la puerta de enlace pero no hace de servidor DNS | DNS = `1.1.1.1,192.168.2.1` en `red.env` y en el perfil (192.168.2.1 es el que da el DHCP) |
| apt fallaba a ratos | `Unable to connect to deb.debian.org` unas veces sí y otras no | La red del centro no deja llegar a algunas IPs de la CDN de Debian (Fastly) ni a varios mirrors | Mirror `http://ftp.de.debian.org/debian/` y seguridad en `security.debian.org` |
| `instalar.sh` se paraba en Docker | `Could not get lock /var/lib/dpkg/lock-frontend` | Se lanzó otro `apt install` a mano a la vez | Esperar y volver a lanzar el script (se salta lo que ya está hecho) |
| `sudo` pidió contraseña al final | `sudo: a password is required` en el paso 10 | La instalación tardó más que los 15 min que `sudo` recuerda la contraseña | Lanzar a mano los dos últimos comandos (`tailscale serve` y `tailscale funnel`) |

Comprobación de DNS que se hizo (consulta directa a cada servidor):

| Servidor | Responde |
|---|---|
| 172.16.50.1 | No |
| 8.8.8.8 | No |
| 1.1.1.1 | Sí |
| 192.168.2.1 | Sí |

Mirrors de Debian probados desde la VLAN 500: solo `ftp.de.debian.org` respondió las tres veces; `ftp.fr`, `ftp.nl`,
`ftp.uk`, `ftp.pt`, `ftp.cica.es` y `ftp.caliu.cat` no respondían, y `ftp.udc.es` respondía pero le faltaban índices.
`ghcr.io` tampoco se alcanza (no nos afecta: todas las imágenes salen de Docker Hub).

## 5. Resultado

Comprobado después de reiniciar la Raspberry (`sudo systemctl reboot`), sin tocar nada:

```
sudo docker compose ps
caddy            Up (healthy)
chirpstack       Up (healthy)
db               Up (healthy)
gateway-bridge   Up
ingestor         Up
mosquitto        Up (healthy)
redis            Up (healthy)
web              Up (healthy)

curl http://127.0.0.1/api/salud            → {"estado":"ok"}
timedatectl                                → Europe/Madrid, System clock synchronized: yes
sudo ufw status                            → activo (SSH solo desde 172.16.50.0/24, NTP solo desde el wAP)
crontab -l                                 → copia de seguridad a las 03:00
```

- Web en el instituto: `http://172.16.50.3`
- Web desde Internet (Tailscale Funnel): `https://rpi-lora.tailc40e5c.ts.net` — comprobada desde fuera del instituto.
- ChirpStack: `https://rpi-lora.tailc40e5c.ts.net:8443`, solo desde equipos con Tailscale (desde Internet no se ve).

## 6. Pruebas sin el nodo (desde casa, por Tailscale)

Con Tailscale instalado en el PC se entra a la Raspberry desde fuera del instituto (`ssh charlie@rpi-lora`).
Se usó el `dev_eui` de pruebas `0000000000000001` del `raspberry/README.md` y al final se borraron sus datos.

| Prueba | Cómo | Resultado |
|---|---|---|
| Tiempo real de punta a punta | Uplink simulado con `mosquitto_pub` mientras se escuchaba `/api/eventos` en la web **pública** | La medida llega a la BD (hora en UTC) y a la web al momento, sin recargar |
| Cola persistente | `docker compose stop ingestor`, 2 uplinks, `docker compose start ingestor` | Con el ingestor parado: 1 fila; al arrancarlo: 3 filas. No se pierde nada |
| Copia de seguridad | `./backup.sh` con el usuario normal, igual que el cron | Crea `agua_*.dump` (25 KB) y `chirpstack_*.dump` (69 KB) |
| Restauración | `pg_restore` de la copia en una BD temporal `prueba_restauracion` | Salen las tablas `medidas`, `nodos` y `uplinks_raw` con sus filas; después se borró la BD temporal |
| ChirpStack desde Internet | Abrir `https://rpi-lora.tailc40e5c.ts.net:8443` sin Tailscale | No conecta (bien: solo es para el equipo) |

Para restaurar una base TimescaleDB hay que crear la extensión y llamar a `timescaledb_pre_restore()` antes
del `pg_restore`, y a `timescaledb_post_restore()` después.

## 7. Pendiente

- ~~Conectar y configurar el wAP LR8~~ (hecho el 2026-11-12, apartado 9). Falta poner su EUI (`04F41CFFFFC15CEB`)
  en `GATEWAY_EUI` del `.env` y lanzar `sudo docker compose run --rm provisionar` cuando la Raspberry vuelva a la red.
- ~~Hablar con el coordinador TIC~~ (hecho el 2026-10-29: IPs fuera del DHCP y DNS en 1.1.1.1 y 192.168.2.1).
- Volver a tener la Raspberry en la VLAN 500: desde el 2026-10-29 a las 20:21 no aparece en Tailscale ni en la red
  (apartado 9.4).
- Batería RTC.
- Primer uplink real del nodo para dar por cerrada la fase.

## 8. Capturas pendientes

- [ ] Salida de `ip -4 -br addr` y `ip route` con la IP fija.
- [ ] `sudo docker compose ps` con todos los servicios en marcha.
- [ ] Consola de Tailscale con `rpi-lora` (*Connected*, *Funnel*, *Expiry disabled*).
- [ ] La web abierta desde un móvil con datos móviles.
- [ ] ChirpStack: aplicación `calidad-agua` y dispositivo `nodo-agua` dados de alta.
- [ ] WinBox: `/iot lora print detail` con `status="Active"`, `servers=chirpstack` y `network=public`.
- [ ] WinBox: log con `forwarder is ready`.
- [ ] Monitor serie de la LILYGO con `Fallo de join: -1116` (antes de la Raspberry) y `Join OK` (después).

## 9. Gateway wAP LR8 y LILYGO en el banco (2026-11-12)

### 9.1 Acceso desde el PC sin perder la VPN

En la red del instituto el PC tiene que ir con la VPN de WireGuard (túnel "portatil") por la WiFi
`Andared_Corporativo`, porque el firewall y el proxy del centro cortan otras herramientas. Al enchufar el cable de la
VLAN 500, Windows le daba más prioridad al cable (métrica 5) que a la WiFi (35), la VPN pasaba a salir por la VLAN 500
y se cortaba. La solución fue bajar la prioridad del cable en una PowerShell de administrador:

```powershell
Set-NetIPInterface -InterfaceAlias Ethernet -InterfaceMetric 500
# para deshacerlo:
Set-NetIPInterface -InterfaceAlias Ethernet -AutomaticMetric Enabled
```

Así Internet y la VPN siguen por la WiFi y el cable solo se usa para 172.16.50.x (wAP y Raspberry). También hay que
tener desmarcado el *kill-switch* del túnel ("Bloquear tráfico fuera del túnel"), porque si no Windows bloquea la red
local aunque el cable esté bien.

### 9.2 Configuración del wAP LR8

El wAP ya tenía la IP 172.16.50.2 (la pusimos a mano antes). Datos que salieron:

| Dato | Valor |
|---|---|
| RouterOS | 7.20.7 |
| Gateway-id (EUI) | `04F41CFFFFC15CEB` |
| Tarjeta LoRa | firmware 1.4.4, banda 863-870, antena uFL |
| Configuración de fábrica | ether1 y wlan1 dentro de `bridgeLocal` |

Comandos pegados en WinBox → New Terminal (guardados en `raspberry/red/wap-lr8.rsc`):

```
/system identity set name=wap-lr8-tfg
:if ([:len [/ip route find dst-address="0.0.0.0/0"]] = 0) do={ /ip route add dst-address=0.0.0.0/0 gateway=172.16.50.1 }
/ip dns set servers=1.1.1.1,192.168.2.1
/system ntp client set enabled=yes servers=172.16.50.3
/iot lora disable [find]
/iot lora servers add name=chirpstack address=172.16.50.3 protocol=UDP up-port=1700 down-port=1700
:delay 5s
/iot lora set [find] servers=chirpstack channel-plan=eu-868 network=public forward=crc-validation
/iot lora enable [find]
/ip address set [find address="172.16.50.2/24"] interface=bridgeLocal
```

Resultado: `status="Active"`, `servers=chirpstack`, `channel-plan=eu-868`, `network=public` y en el log
`forwarder is ready`. Sale también `[UDP] Keepalive timed out`, que es normal mientras la Raspberry no esté en la red.

Problemas con el wAP:

| Problema | Causa | Solución |
|---|---|---|
| `failure: Device is busy` al hacer `/iot lora set` | La tarjeta aún se estaba parando tras el `disable` | Esperar unos segundos (`:delay 5s`) y repetir |
| Venía con `network=private` | Valor de fábrica | `network=public`: la LILYGO (RadioLib) usa la palabra de sincronización pública de LoRaWAN |
| `forward` con `dev-addr-validation` | Valor de fábrica | Solo `crc-validation`: reenvía todo lo que llega bien y ChirpStack decide |
| IP puesta en `wlan1` (marca `S`, puerto del bridge) | Se puso a mano en la interfaz equivocada | Moverla a `bridgeLocal` |

### 9.3 LILYGO en el banco, sin placa base

Con la LILYGO suelta, GPIO36 (`PIN_MODO_CAL`) queda al aire. No tiene resistencia interna, se lee LOW y el nodo
entra siempre en `MODO CALIBRACION`. Para no tener que puentear el pin se añadió un entorno de compilación solo para
el banco:

- `platformio.ini`: entorno `lilygo_t3_banco` (igual que `lilygo_t3_v1_6_1` más `-DSIN_PIN_MODO_CAL`).
- `src/main.cpp`: la comprobación del pin va dentro de `#ifndef SIN_PIN_MODO_CAL`.

El firmware de la maqueta no cambia. Grabar el de banco y el definitivo:

```
pio run -e lilygo_t3_banco -t upload        (banco, LILYGO suelta)
pio run -e lilygo_t3_v1_6_1 -t upload       (maqueta, con placa base)
```

Resultado en el monitor serie: `Fallo de join: -1116` (en RadioLib, el join request sale pero no llega el join accept,
lo normal sin la Raspberry) y `Durmiendo 300 s`. No sale `Error de radio`, así que la radio funciona.

Prueba de radio LILYGO → wAP (`/iot lora print detail` y `/iot lora traffic print` en el wAP):

```
rx-packets=2  tx-packets=0
0  2026-11-12 08:58:38  04F41CFFFFC15CEB  Join-request  LoRaWAN R1  Ok   Rx
1  2026-11-12 09:02:56  04F41CFFFFC15CEB  Join-request  LoRaWAN R1  Ok   Rx
```

Los dos join request de la LILYGO llegan al wAP con el CRC bien, a la misma hora que en el monitor serie
(el reloj del wAP va unos segundos desfasado hasta que tenga NTP de la Raspberry). `tx-packets=0` porque todavía
nadie contesta con el join accept. **La parte de radio funciona.**

### 9.4 Raspberry fuera de la red

Desde el 2026-10-29 a las 20:21 (hora de España) la Raspberry no aparece en Tailscale. Con el PC en la VLAN 500 se
hizo un barrido de 172.16.50.0/24 (ping, ARP y puerto 22): responden la puerta de enlace (.1), el wAP (.2), el PC y
otro equipo (.24), pero ningún equipo con MAC de Raspberry Pi. O sea, el problema no es Tailscale sino que la
Raspberry no tiene red (cable, toma o configuración). En Tailscale aparece además un equipo `localhost` visto por
última vez el 2026-11-07, que hay que revisar.

Comprobación con teclado y monitor:

```
hostname
ip -br a
nmcli con show
sudo nmcli con up red-vlan500
ping -c3 172.16.50.1
sudo tailscale up
```

### 9.5 Lo que queda para el primer uplink real

1. Raspberry de vuelta en la VLAN 500 con 172.16.50.3 y Tailscale *online*.
2. `GATEWAY_EUI=04F41CFFFFC15CEB` en `raspberry/.env` y `sudo docker compose run --rm provisionar`.
3. En el wAP, que salga `forwarder is ready` sin `Keepalive timed out` y que `rx-packets` suba.
4. En la LILYGO, `Join OK` y el primer uplink en ChirpStack, en la BD y en la web.
