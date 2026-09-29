# Puesta en marcha de la Raspberry Pi 5 y del wAP LR8

La Raspberry lo hace todo: router de la red del gateway, servidor LoRaWAN (ChirpStack), MQTT,
base de datos (TimescaleDB), la web y el HTTPS con DuckDNS. Red explicada en `docs/02-arquitectura-red.md`.

Orden recomendado. Cada paso tiene su comprobación; no pasar al siguiente sin que funcione.

## 1. Sistema
1. Raspberry Pi Imager → Raspberry Pi OS Lite (64-bit) → grabar en la **microSD de 64 GB** (mejor una de marca A1/A2
   o de tipo *High Endurance*, que aguantan más escrituras).
   Opciones: hostname `rpi-lora`, usuario propio, SSH con clave pública, zona horaria Europe/Madrid.
2. `sudo apt update && sudo apt full-upgrade -y && sudo apt install -y chrony ufw git`
3. Docker: `curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER` (cerrar sesión y volver a entrar).
4. Cuidar la microSD (lo que más la estropea son las escrituras continuas):
   - Limitar el diario del sistema: en `/etc/systemd/journald.conf` poner `SystemMaxUse=100M` y
     `sudo systemctl restart systemd-journald`.
   - Los registros de los contenedores ya están limitados en `docker-compose.yml` (3 × 10 MB cada uno).
   - Los datos ocupan poco: unos 100 mensajes al día son pocos MB al año, así que no hace falta borrar medidas.
   - Lo importante es tener copia **fuera de la tarjeta** (apartado 8) por si la SD falla.
5. Batería RTC oficial (recargable): añadir `dtparam=rtc_bbat_vchg=3000000` a `/boot/firmware/config.txt`.
   Comprobar: `timedatectl` y `sudo hwclock -r`.
6. `git clone https://github.com/cmaaraver/TFG-2-STI-.git && cd TFG-2-STI-/raspberry`

## 2. Red (con teclado y monitor conectados)
```bash
ip link                                   # ver cómo se llaman las interfaces
IF_LORA=eth0 IF_INSTITUTO=eth1 ./red/configurar-red.sh
sudo cp red/chrony.conf /etc/chrony/chrony.conf && sudo systemctl restart chrony
```
Comprobar: `ip a` (192.168.50.1 en eth0 y una 192.168.155.x en eth1), `ping -c3 8.8.8.8`, `chronyc tracking`.
El firewall se pone al final (paso 6), cuando Docker ya está funcionando.

## 3. Arrancar todo
```bash
cp .env.example .env
nano .env                                  # cambiar TODAS las contraseñas y poner el token de DuckDNS
docker compose up -d --build               # la primera vez tarda (compila Caddy con el módulo de DuckDNS)
docker compose ps                          # todo "running"/"healthy"
```
Comprobar:
- `docker compose logs -f caddy` → "certificate obtained successfully" para `<dominio>.duckdns.org`.
- `curl http://localhost/api/salud` → `{"estado":"ok"}`.
- Desde el aula: `http://<ip-192.168.155.x-de-la-raspberry>` → sale la web (sin datos todavía).

## 4. MikroTik wAP LR8 (RouterOS, WinBox o WebFig)
- IP estática 192.168.50.2/24, gateway 192.168.50.1, DNS 192.168.50.1.
- NTP cliente → 192.168.50.1.
- Actualizar RouterOS e instalar el paquete `iot`/`lora` si falta.
- Servidor LoRa: `/iot lora servers add name=chirpstack address=192.168.50.1 up-port=1700 down-port=1700`
  y asignarlo al dispositivo LoRa, red "Public", y activarlo (TODO VERIFICAR comandos en la versión de RouterOS instalada).
- Anotar el Gateway EUI (`/iot lora print`) para darlo de alta en ChirpStack.
- Desactivar la WiFi si no se usa.

## 5. ChirpStack
1. Tailscale: `curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`
2. Publicar ChirpStack solo para el equipo: `sudo tailscale serve --bg --https=8443 http://127.0.0.1:8080`
   y entrar a `https://rpi-lora.<red>.ts.net:8443` (o con un túnel SSH: `ssh -L 8080:127.0.0.1:8080 rpi-lora`).
3. Usuario `admin` / contraseña `admin` → **cambiarla nada más entrar**.
4. Crear:
   - Gateway con el EUI del wAP → debe salir "online".
   - Perfil de dispositivo: EU868, LoRaWAN 1.1.0, OTAA, clase A, codec JavaScript = contenido de `codec/decoder.js`.
   - Aplicación "calidad-agua" y dispositivo (DevEUI + claves → `firmware/nodo-agua/include/secrets.h`).
5. Comprobar: el nodo hace join, los uplinks salen decodificados en ChirpStack, `docker compose logs ingestor`
   dice "Guardado ..." y la web enseña los valores al momento.

## 6. Firewall
```bash
IF_LORA=eth0 IF_INSTITUTO=eth1 ./red/firewall.sh
```
Comprobar desde otro equipo del instituto que la web sigue entrando y que `nc -u -z <ip> 1700` no llega.

## 7. Acceso desde Internet
Pedir al coordinador TIC la reserva de IP y el reenvío del puerto 443 (ver `docs/02-arquitectura-red.md`).
Probar desde un móvil con datos: `https://<dominio>.duckdns.org`. Si no se puede abrir el puerto:
`sudo tailscale funnel --bg 80` (plan B).

## 8. Copias de seguridad
`crontab -e` → `0 3 * * * $HOME/TFG-2-STI-/raspberry/backup.sh >> $HOME/backup-agua.log 2>&1`
Guarda las dos bases de datos (medidas y ChirpStack, que tiene las claves de los nodos).
Como todo va en la microSD, las copias hay que sacarlas de la Raspberry: por ejemplo, una vez a la semana
`scp -r rpi-lora:TFG-2-STI-/raspberry/backups/ .` desde un PC, o a un pendrive. Si la tarjeta muere, se graba otra,
se repiten los pasos 1-3 y se restauran las dos copias.
Probar la restauración una vez:
`docker compose exec -T db pg_restore -U agua_admin -d calidad_agua --clean < backups/agua_XXXX.dump`

## Prueba de robustez (para la memoria)
1. `docker compose stop ingestor`
2. Esperar a que el nodo envíe 2 mensajes.
3. `docker compose start ingestor` → en los logs aparecen los 2 mensajes guardados (cola persistente de Mosquitto, QoS 1).
4. `docker compose exec db psql -U agua_admin -d calidad_agua -c "SELECT count(*) FROM medidas;"` antes y después.

## Probar la web sin el nodo (datos simulados)
Publicar un uplink falso con el mismo formato que ChirpStack:
```bash
docker compose exec -T mosquitto mosquitto_pub -q 1 -t application/1/device/0000000000000001/event/up -m \
'{"deduplicationId":"'$(cat /proc/sys/kernel/random/uuid)'","time":"'$(date -u +%FT%TZ)'",
  "deviceInfo":{"devEui":"0000000000000001","deviceName":"prueba"},"fCnt":1,
  "object":{"temperatura_c":21.5,"oxigeno_mgl":8.1,"ph":7.3,"nivel_mm":600,"bateria_v":13.1,"caudal_lmin":4.5,"agua_presente":true},
  "rxInfo":[{"gatewayId":"0016c001ff000001","rssi":-85,"snr":7.5}],"txInfo":{"modulation":{"lora":{"spreadingFactor":7}}}}'
```
Borrar después los datos de prueba: `DELETE FROM medidas WHERE dev_eui='0000000000000001';` (y en `nodos` y `uplinks_raw`).

## La web

![Web con datos simulados](../docs/img/web-datos-simulados.png)

(Captura con **datos simulados** de 7 días, no son medidas reales. En el móvil: `docs/img/web-movil-datos-simulados.png`.)

- `web/app.py`: API (FastAPI). `/api/historico` agrupa en medias automáticamente si hay más de 1500 puntos.
- `web/static/`: la página (HTML + CSS + JavaScript con ECharts, sin depender de Internet).
- Tiempo real: el ingestor inserta → un trigger de la base de datos hace `NOTIFY` → la web lo manda al
  navegador por Server-Sent Events. No hay que recargar la página.
- Los rangos de color de las tarjetas (verde/naranja/rojo) están al principio de `web/static/app.js`.
