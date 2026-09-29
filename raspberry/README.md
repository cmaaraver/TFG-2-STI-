# Puesta en marcha de la Raspberry Pi 5 y del wAP LR8

Orden recomendado. Cada paso tiene su comprobación; no pasar al siguiente sin que funcione.

## 1. Sistema
1. Raspberry Pi Imager → Raspberry Pi OS Lite (64-bit) → grabar en el SSD NVMe (con el M.2 HAT+).
   Opciones: hostname `rpi-lora`, usuario propio, SSH con clave pública, zona horaria Europe/Madrid.
2. `sudo apt update && sudo apt full-upgrade -y && sudo apt install -y chrony ufw git`
3. Docker: `curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER`
4. Batería RTC oficial (recargable): añadir `dtparam=rtc_bbat_vchg=3000000` a `/boot/firmware/config.txt`
   para que se cargue. Comprobar: `timedatectl` y `sudo hwclock -r`.

## 2. Red (ver docs/02-arquitectura-red.md)
- `nmcli` para `lan-privada` (eth0, modo shared) y `red-instituto` (adaptador USB).
- Copiar `red/chrony.conf` a `/etc/chrony/chrony.conf` y `sudo systemctl restart chrony`.
- Firewall ufw.
- Comprobar: `ip a`, `ping 8.8.8.8` desde la Raspberry y desde el PC (a través del NAT), `chronyc clients`.

## 3. ChirpStack (servidor LoRaWAN)
1. `git clone https://github.com/chirpstack/chirpstack-docker.git ~/chirpstack && cd ~/chirpstack`
2. Región: activar solo `eu868` en la configuración de ChirpStack y del Gateway Bridge (según el README del repo).
3. Integración MQTT con **QoS 1** en `configuration/chirpstack/chirpstack.toml` (TODO VERIFICAR el nombre
   exacto de la opción en la documentación de ChirpStack v4).
4. Sustituir la configuración de Mosquitto por `raspberry/mosquitto/mosquitto.conf`, crear `passwd`
   (`mosquitto_passwd`) y `acl`, y publicar el puerto 1884 solo en `192.168.50.1`.
5. Publicar la web de ChirpStack (8080) y el UDP 1700 solo en `192.168.50.1`.
6. `docker compose up -d` y entrar a `http://192.168.50.1:8080`; cambiar la contraseña de admin.
7. Crear: perfil de dispositivo (EU868, LoRaWAN 1.1.0, OTAA, clase A, codec = `codec/decoder.js`),
   aplicación "calidad-agua", gateway (EUI del wAP) y dispositivo (DevEUI + claves → `secrets.h`).

## 4. MikroTik wAP LR8 (RouterOS, WinBox o WebFig)
- IP estática 192.168.50.2/24, gateway 192.168.50.1, DNS 192.168.50.1.
- NTP cliente → 192.168.50.1.
- Actualizar RouterOS e instalar el paquete `iot`/`lora` si falta.
- Servidor LoRa: `/iot lora servers add name=chirpstack address=192.168.50.1 up-port=1700 down-port=1700`
  y asignarlo al dispositivo LoRa, red "Public", y activarlo (TODO VERIFICAR comandos en la versión de RouterOS instalada).
- Anotar el Gateway EUI (`/iot lora print`) para darlo de alta en ChirpStack.
- Desactivar la WiFi si no se usa.
- Comprobar: el gateway aparece "online" en ChirpStack y se ven tramas en "LoRaWAN frames".

## 5. Node-RED (fase 7)
- Contenedor `nodered/node-red` en el mismo compose, puerto 1880 publicado en 192.168.50.1.
- Flujo: suscripción a `application/+/device/+/event/up` → umbrales → downlink al DFR1120
  publicando en `application/<id>/device/<devEui>/command/down`.

## 6. Tailscale
- `curl -fsSL https://tailscale.com/install.sh | sh`
- `sudo tailscale up --advertise-routes=192.168.50.0/24` y aprobar la ruta en la consola de Tailscale.
- Activar IP forwarding (el modo shared de NetworkManager ya lo activa; comprobar `sysctl net.ipv4.ip_forward`).
