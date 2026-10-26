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
             TimescaleDB, ingestor, web,          │  (sin reenvío de puertos)
             Caddy, Tailscale ──── salida ───────▼
                                               Internet ── Tailscale Funnel
                                                  │
            https://rpi-lora.<red>.ts.net  ←  cualquier navegador o móvil
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

## Gateway en el mástil de la azotea

Decisión de 2026-10-26: el wAP LR8 va en el **mástil de la azotea** del instituto. Desde arriba ve la maqueta
sin paredes en medio y LoRa llega mucho mejor que desde dentro del edificio. La IP y la configuración no cambian.

Datos del wAP LR8 kit (ficha de MikroTik, https://mikrotik.com/product/wap_lr8_kit): caja de exterior IP54,
de −40 a +60 °C, antena interna de 2 dBi (admite antena externa), alimentación por PoE pasivo de 9 a 30 V
(el kit trae fuente de 24 V e inyector) y 7 W como máximo.

```
  mástil (azotea)                            dentro del edificio
  ┌────────────┐
  │  wAP LR8   │  conector hacia ABAJO
  └─────┬──────┘
        │ cable Cat6 FTP de exterior (con bucle de goteo)          fuente 24 V
        └──────── bajante protegida (tubo o canaleta) ──────► [inyector PoE] ──► switch (VLAN 500)
```

Cómo se monta:
1. **Antes de subir**: configurar y probar el wAP abajo, en la mesa (`raspberry/README.md`, apartado 4). En la
   azotea solo se fija y se conecta.
2. **Posición**: en lo alto del mástil, vertical (como viene, la antena interna es vertical) y por encima del
   pretil para que nada tape la vista hacia la maqueta. Con el **conector Ethernet hacia abajo**.
3. **Sujeción**: el kit trae herrajes de pared; en el mástil se fija con abrazaderas o bridas de acero inoxidable
   (**TODO VERIFICAR** si el kit trae soporte de mástil).
4. **Cable**: Cat6 **FTP de exterior** (resistente al sol), con un bucle de goteo antes del conector para que
   el agua no entre por el cable. Bajante por tubo o canaleta. El tramo entero, del switch al wAP pasando por el
   inyector, **no puede pasar de 100 m** (límite de Ethernet).
5. **El inyector PoE y la fuente de 24 V van dentro**, junto al switch: no son de exterior.
6. **Tierra**: el mástil tiene que estar unido a la tierra o al pararrayos del edificio. Si se puede, poner un
   protector de sobretensiones para Ethernet entre el cable de la azotea y el inyector. Antes de subir, pedir
   permiso al coordinador TIC y al centro para acceder a la azotea y usar el mástil.
7. **Prueba**: con el nodo encendido en la maqueta, mirar en ChirpStack el RSSI y la SNR de varios uplinks.
   Con SNR positiva y RSSI mejor que −110 dBm hay margen de sobra.

Con la VLAN ya no hace falta cable directo de la Raspberry al wAP: cada uno va a un puerto del switch
(el wAP a través de su inyector PoE, que viene en el kit). Si el switch del instituto diera un PoE
compatible con el wAP se podría quitar el inyector, pero eso hay que mirarlo en la ficha de MikroTik
(**TODO VERIFICAR**); mientras tanto se usa el inyector.

## Servicios y puertos

| Servicio | Puerto | Desde dónde se llega |
|---|---|---|
| Web (Caddy → web) | TCP 80 | Red del instituto y Tailscale. Desde Internet, por Tailscale Funnel (HTTPS en la red de Tailscale, no en el router del centro) |
| Gateway Bridge | UDP 1700 | Solo desde el wAP (172.16.50.2). Bloqueado para el resto de la VLAN |
| ChirpStack (web de administración) | TCP 8080 | Solo `127.0.0.1`; el equipo entra con `tailscale serve` |
| Mosquitto (MQTT) | 1883 | Solo dentro de Docker, no se publica |
| TimescaleDB | 5432 | Solo dentro de Docker, no se publica |
| NTP (chrony) | UDP 123 | Solo el wAP (172.16.50.2) |
| SSH | TCP 22 | VLAN 500 (solo con clave) y Tailscale. Nunca desde Internet |

## Acceso desde Internet: Tailscale Funnel

El instituto **no puede abrir puertos** en su router (decisión de 2026-10-26), así que no se usa DuckDNS
ni reenvío del 443. La web se publica con **Tailscale Funnel**:

1. La Raspberry tiene Tailscale y abre una conexión **de salida** hacia sus servidores; no entra nada
   por el router del centro.
2. `sudo tailscale funnel --bg --https=443 http://127.0.0.1:80` publica la web (Caddy en el puerto 80) en
   `https://rpi-lora.<red>.ts.net`, con HTTPS y certificado de Let's Encrypt que gestiona Tailscale.
3. Cualquiera con el enlace la ve desde fuera (el móvil no necesita Tailscale). ChirpStack, en cambio, solo
   se publica dentro del tailnet con `tailscale serve`.
4. **Dentro del instituto** también se entra por `http://172.16.50.3` (desde un equipo con acceso a la VLAN 500).

Paso a paso, comprobaciones y qué pedir al coordinador TIC: `docs/09-acceso-internet.md`.

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
- ufw: se deniega todo lo entrante salvo Tailscale, el 80 (la web), SSH desde la VLAN 500
  y NTP solo desde el wAP.
- Docker publica puertos saltándose ufw. Por eso el UDP 1700 se limita al wAP (172.16.50.2) con una
  regla en la cadena `DOCKER-USER` (servicio `docker-user-reglas`), y ChirpStack solo escucha en `127.0.0.1`.

## Seguridad
- LoRaWAN 1.1 OTAA: claves AES-128 únicas por nodo.
- SSH solo con clave pública, sin contraseña, y no expuesto a Internet.
- La web es de solo lectura: entra a la base de datos con el usuario `web_lector`, que no puede
  modificar nada.
- Contraseñas en `raspberry/.env`, que no se sube a git.
- Ningún puerto abierto a Internet: lo público entra solo por Tailscale Funnel, y solo la web.
- WiFi del wAP desactivada y su administración (WinBox/web) protegida con contraseña, porque ahora
  está en una VLAN compartida.
- **Antes de conectar nada a la red del instituto hay que pedir permiso al coordinador TIC.**
