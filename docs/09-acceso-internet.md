# Acceso desde Internet: la web pública con Tailscale Funnel

El instituto **no puede abrir puertos** en su router (decisión de 2026-10-26), así que no se puede usar
DuckDNS con reenvío del 443, que era la idea del principio. En su lugar, la web se publica con
**Tailscale Funnel**: la Raspberry abre una conexión **de salida** hacia Tailscale y Tailscale hace de puerta
de entrada desde Internet. No hay que tocar el router del centro ni pedir ningún puerto.

```
 móvil con datos ──► https://rpi-lora.<red>.ts.net ──► servidores de Tailscale
                                                           │  (conexión que abrió la Raspberry hacia fuera)
                                                           ▼
                            Raspberry: tailscaled (HTTPS, certificado de Let's Encrypt) ──► Caddy :80 ──► web
```

- La dirección es `https://rpi-lora.<red>.ts.net`: `rpi-lora` es el nombre de la Raspberry y `<red>` el nombre
  del tailnet (algo como `tail1a2b3c`). Se puede cambiar una vez por un nombre más bonito en la consola de
  Tailscale → **DNS** → *Rename tailnet*.
- El certificado HTTPS lo saca Tailscale solo. No hace falta token ni dominio propio.
- Desde dentro del instituto también se puede entrar por `http://172.16.50.3`.

## 1. Cuenta de Tailscale

1. Crear la cuenta en **https://login.tailscale.com** con una cuenta que tengan los dos miembros del grupo
   (Google o GitHub del equipo). El plan gratuito *Personal* basta.
2. Instalar Tailscale también en los portátiles y móviles del grupo y entrar con la misma cuenta: así se llega
   a ChirpStack y por SSH a la Raspberry desde cualquier sitio (`docs/02-arquitectura-red.md`).

## 2. Instalar la Raspberry

Lo hace `raspberry/instalar.sh` (ver `raspberry/README.md`). En el paso 10:

1. `sudo tailscale up` enseña un enlace `https://login.tailscale.com/a/...`: abrirlo e iniciar sesión con la
   cuenta del equipo.
2. `sudo tailscale serve --bg --https=8443 http://127.0.0.1:8080` publica ChirpStack **solo para el tailnet**.
3. `sudo tailscale funnel --bg --https=443 http://127.0.0.1:80` publica la web **en Internet**. La primera vez sale
   otro enlace para activar HTTPS y Funnel en el tailnet: abrirlo y aceptar (crea el certificado y añade el
   permiso `funnel` a la política del tailnet). Hace falta tener **MagicDNS** activado (viene activado por defecto).
   Funnel solo puede usar los puertos 443, 8443 y 10000, y no puede compartir puerto con `serve`.

Si se hace a mano, son esos mismos tres comandos.
Documentación oficial: https://tailscale.com/kb/1223/funnel y https://tailscale.com/kb/1311/tailscale-funnel

**Comprobación** (en la Raspberry):

| Qué | Comando | Resultado esperado |
|---|---|---|
| Tailscale conectado | `tailscale status` | Sale `rpi-lora` con su IP `100.x.y.z` |
| Funnel activo | `sudo tailscale funnel status` | `https://rpi-lora.<red>.ts.net (Funnel on)` → `proxy http://127.0.0.1:80` |
| ChirpStack para el equipo | `sudo tailscale serve status` | `https://rpi-lora.<red>.ts.net:8443 (tailnet only)` |
| La web por dentro | `curl -s http://localhost/api/salud` | `{"estado":"ok"}` |

## 3. Lo que hay que pedir al coordinador TIC

Ya **no hay que abrir ningún puerto**. Solo:

1. **Permiso** para conectar la Raspberry y el wAP a la VLAN 500, con las dos tomas del switch en esa VLAN
   **sin etiquetar** (modo acceso).
2. Que **172.16.50.2 y 172.16.50.3 queden fuera del rango del DHCP** de la VLAN 500.
3. Confirmar la **máscara** (suponemos /24) y el **DNS** (suponemos 172.16.50.1).
4. **Permiso para usar Tailscale** en la Raspberry. Solo necesita salir a Internet: UDP 41641 si está
   permitido y, si no, HTTPS (TCP 443) de salida, que casi siempre está abierto.

Texto para mandárselo:

> Hola. Para el proyecto final de 2º de STI (monitorización de la calidad del agua con LoRaWAN) tenemos
> una Raspberry Pi con IP fija `172.16.50.3` y un gateway LoRa MikroTik con IP fija `172.16.50.2`, los dos
> en la VLAN 500 con puerta de enlace `172.16.50.1`. Necesitaríamos, si es posible:
> 1. Que esas dos IP queden fuera del rango del DHCP de la VLAN 500, y que las tomas donde los conectemos
>    estén en la VLAN 500 sin etiquetar. ¿La máscara es /24 y el DNS 172.16.50.1?
> 2. Permiso para usar Tailscale en la Raspberry. Con él publicamos una página web de consulta con HTTPS
>    sin abrir ningún puerto en el router del centro: solo hace conexiones de salida. No hay escritorio
>    remoto ni SSH abiertos a Internet, y la Raspberry tiene firewall.
>
> Gracias.
> Carlos Maraver y Rubén Trillo

## 4. Probar desde fuera

Con un **móvil con datos móviles** (WiFi apagada), abrir `https://rpi-lora.<red>.ts.net`. El móvil **no necesita
Tailscale**: Funnel es público. Tiene que salir la web con el candado y los datos al momento (el tiempo real va
por SSE y pasa bien por Funnel).

## 5. Problemas típicos

| Síntoma | Causa | Solución |
|---|---|---|
| `tailscale funnel` se queda esperando | Falta activar HTTPS o Funnel en el tailnet | Abrir el enlace que enseña con la cuenta del equipo y aceptar |
| `Funnel not available` o error de permisos | La política del tailnet no deja Funnel a este equipo | Consola de Tailscale → *Access controls*: tiene que estar el atributo `funnel` (viene por defecto en tailnets nuevos) |
| Desde el móvil no carga | Funnel apagado, o el nombre aún no se ha propagado | `sudo tailscale funnel status`; si está off, `sudo tailscale funnel --bg --https=443 http://127.0.0.1:80`. Los nombres públicos tardan hasta 10 min |
| Carga pero sin datos en tiempo real | Algo retiene los eventos | Comprobar que el `Caddyfile` tiene `flush_interval -1` |
| `tailscale status` dice *Logged out* | Caducó la sesión del equipo (por defecto a los 180 días) | `sudo tailscale up`, o en la consola desactivar *Key expiry* para `rpi-lora` |
| La Raspberry no sale a Internet | Toma del switch fuera de la VLAN 500, IP repetida o DNS distinto | `ping 172.16.50.1`, `ip -br a`; si falla el nombre pero no la IP, cambiar `DNS` en `raspberry/red/red.env` |

Para que la web no deje de verse a los 6 meses, lo mejor es desactivar *Key expiry* para `rpi-lora` en la consola
de Tailscale (*Machines* → `rpi-lora` → menú → *Disable key expiry*).
