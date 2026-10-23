# Guía de DuckDNS: la web accesible desde Internet

DuckDNS es un servicio gratuito que da un nombre fijo (`algo.duckdns.org`) que apunta a la IP pública
del instituto aunque esta cambie. Con ese nombre, Caddy saca un certificado HTTPS de Let's Encrypt y la web
queda en `https://<nombre>.duckdns.org`.

Hay tres partes: crear el nombre (5 minutos, lo hacemos nosotros), instalar la Raspberry (lo hace
`raspberry/instalar.sh`) y abrir el puerto 443 (lo tiene que hacer el coordinador TIC).

```
 móvil con datos ──► calidad-agua-viveros.duckdns.org ──► IP pública del instituto
                                                             │ router del centro: TCP 443 → Raspberry
                                                             ▼
                                                      Raspberry (Caddy, HTTPS) ──► web
```

## 1. Crear la cuenta y el subdominio

1. Entrar en **https://www.duckdns.org** e iniciar sesión con la cuenta del equipo. Deja entrar con
   GitHub, Google, Reddit o Twitter; mejor una cuenta que tengan los dos miembros del grupo.
2. En **sub domain** escribir el nombre, por ejemplo `calidad-agua-viveros`, y pulsar **add domain**.
   Solo minúsculas, números y guiones. Si ya está cogido, probar otro.
3. Arriba de la página aparece el **token** (formato `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
   Es la contraseña del dominio: **no se pega en ningún documento ni se sube a git**. Solo se escribe
   cuando lo pide `instalar.sh`, que lo guarda en `raspberry/.env`.
4. Apuntar el subdominio elegido; se necesita en el paso siguiente.

## 2. Instalar la Raspberry

Con el subdominio y el token a mano, se ejecuta el script (ver `raspberry/README.md`):

```bash
cd TFG-2-STI-/raspberry
./instalar.sh
```

El script comprueba el token con DuckDNS antes de seguir (si está mal, lo dice y para). Después:
- El contenedor `duckdns` actualiza cada 5 minutos la IP pública del instituto en DuckDNS.
- El contenedor `caddy` pide el certificado HTTPS **por DNS** (reto DNS-01 usando el token), así que lo
  consigue aunque el instituto todavía no haya abierto ningún puerto.

**Comprobación** (en la Raspberry):

| Qué | Comando | Resultado esperado |
|---|---|---|
| IP pública del instituto | `curl -s ifconfig.me` | Una IP, por ejemplo `212.x.x.x` |
| DuckDNS apunta a ella | `nslookup calidad-agua-viveros.duckdns.org 1.1.1.1` | La misma IP |
| Certificado conseguido | `sudo docker compose logs caddy \| grep -i "certificate obtained"` | `certificate obtained successfully` |
| La web por dentro | `curl -s http://localhost/api/salud` | `{"estado":"ok"}` |

Si la IP de `nslookup` no coincide o es del tipo `100.64.x.x` a `100.127.x.x`, el centro sale a Internet
por una red compartida del operador (CGNAT) y **no se puede abrir un puerto**: pasar directamente al plan B.

## 3. Lo que hay que pedir al coordinador TIC

Trabajamos en la **VLAN 500** del instituto con IP fija: la Raspberry es `172.16.50.3` y el gateway LoRa
(wAP LR8) `172.16.50.2`, con puerta de enlace `172.16.50.1`. Como ya tiene IP fija, no hace falta reservar
nada por MAC. Se le pide:

1. **Permiso** para conectar la Raspberry y el wAP a la VLAN 500 (si no se ha pedido ya), y que las dos
   tomas del switch estén en esa VLAN **sin etiquetar** (modo acceso).
2. Que **172.16.50.2 y 172.16.50.3 queden fuera del rango del DHCP** de la VLAN 500, para que no se las
   den a otro equipo.
3. Confirmar la **máscara** (suponemos /24) y el **DNS** (suponemos 172.16.50.1).
4. **Reenviar el puerto TCP 443** de la IP pública del centro a `172.16.50.3`.
   El 80 no hace falta: el certificado se saca por DNS.

Texto para mandárselo:

> Hola. Para el proyecto final de 2º de STI (monitorización de la calidad del agua con LoRaWAN) tenemos
> una Raspberry Pi con IP fija `172.16.50.3` y un gateway LoRa MikroTik con IP fija `172.16.50.2`, los dos
> en la VLAN 500 con puerta de enlace `172.16.50.1`. Necesitaríamos, si es posible:
> 1. Que esas dos IP queden fuera del rango del DHCP de la VLAN 500, y que las tomas donde los conectemos
>    estén en la VLAN 500 sin etiquetar. ¿La máscara es /24 y el DNS 172.16.50.1?
> 2. Reenviar el puerto TCP 443 de la IP pública del centro a `172.16.50.3:443`.
>
> Por ese puerto solo se publica una página web de consulta con HTTPS (certificado de Let's Encrypt);
> no hay escritorio remoto ni SSH abiertos a Internet. La Raspberry tiene firewall y el resto de servicios
> solo los usamos nosotros (el puerto del gateway LoRa solo acepta tráfico del MikroTik). Si no se puede abrir el puerto, usaremos Tailscale Funnel,
> que no necesita tocar el router. Gracias.
> Carlos Maraver y Rubén Trillo

## 4. Probar desde fuera

- Con un **móvil con datos móviles** (WiFi apagada): abrir `https://calidad-agua-viveros.duckdns.org`.
  Tiene que salir la web con el candado y los datos al momento.
- **Desde dentro del instituto puede no funcionar el nombre** aunque desde fuera sí (muchos routers no
  dejan entrar a la IP pública desde la red interna). Dentro del centro se usa `http://172.16.50.3`.

## 5. Plan B: sin abrir puertos (Tailscale Funnel)

Si el centro no puede reenviar el 443 o tiene CGNAT, la web se publica a través de Tailscale, que solo
necesita salir a Internet:

```bash
sudo tailscale funnel --bg 80
sudo tailscale funnel status        # muestra la dirección pública
```

La web queda en `https://<nombre-raspberry>.<red>.ts.net`, con HTTPS y accesible desde cualquier sitio.
El dominio de DuckDNS no se usaría en ese caso (el contenedor `duckdns` puede seguir funcionando sin molestar).

## 6. Problemas típicos

| Síntoma | Causa | Solución |
|---|---|---|
| `instalar.sh` dice que DuckDNS rechaza el token | Token o subdominio mal copiados | Copiarlos otra vez de la web de DuckDNS |
| Caddy no saca el certificado | Token mal en `.env` o sin Internet | `sudo docker compose logs caddy`; corregir `.env` y `sudo docker compose up -d` |
| Desde el móvil no carga (tiempo agotado) | El 443 no está reenviado a 172.16.50.3 | Revisar con el TIC el reenvío |
| Desde el móvil carga, desde el aula no | El router no permite entrar a la IP pública desde dentro | Normal: dentro, usar `http://172.16.50.3` |
| DuckDNS apunta a una IP antigua | Contenedor `duckdns` parado | `sudo docker compose ps duckdns` y `sudo docker compose logs duckdns` |
| La Raspberry no sale a Internet | Toma del switch fuera de la VLAN 500, IP repetida o DNS distinto | `ping 172.16.50.1`, `ip -br a`; si falla el nombre pero no la IP, cambiar `DNS` en `raspberry/red/red.env` |
