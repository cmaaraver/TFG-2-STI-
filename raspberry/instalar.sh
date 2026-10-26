#!/bin/bash
# =====================================================================
#  Instalación completa de la Raspberry Pi 5 del TFG (calidad del agua)
#
#  Se ejecuta UNA vez después de grabar Raspberry Pi OS Lite (64 bits) en la microSD:
#    sudo apt update && sudo apt install -y git
#    git clone https://github.com/cmaaraver/TFG-2-STI-.git
#    cd TFG-2-STI-/raspberry
#    ./instalar.sh
#
#  Deja listo: sistema actualizado, cuidado de la microSD, reloj RTC, Docker, la red con IP fija
#  en la VLAN 500 del instituto (red/red.env), NTP para el wAP, contraseñas generadas, todos los
#  contenedores (ChirpStack, MQTT, base de datos, web), firewall, copia de seguridad diaria y
#  Tailscale (acceso del equipo y web pública con HTTPS por Tailscale Funnel, sin abrir puertos).
#
#  Se puede volver a ejecutar sin miedo: lo que ya está hecho se salta.
#  Antes, leer docs/09-acceso-internet.md y tener a mano la cuenta de Tailscale del equipo.
#
#  La IP fija, la puerta de enlace y el DNS están en red/red.env. Se pueden cambiar ahí o al ejecutar:
#    IF_RED=eth0 IP_RASPBERRY=172.16.50.3 DNS=172.16.50.1 ./instalar.sh
# =====================================================================
set -euo pipefail

CARPETA="$(cd "$(dirname "$0")" && pwd)"
cd "$CARPETA"
USUARIO="$(id -un)"

# ---------- Utilidades ----------
verde()    { printf '\033[1;32m%s\033[0m\n' "$*"; }
amarillo() { printf '\033[1;33m%s\033[0m\n' "$*"; }
rojo()     { printf '\033[1;31m%s\033[0m\n' "$*"; }
paso()     { echo; verde "==> $*"; }
fallo()    { rojo "ERROR: $*"; exit 1; }
# pregunta "texto" "s|n"  → devuelve 0 si la respuesta es sí
pregunta() {
  local r defecto="$2" opciones="[s/N]"
  [ "$defecto" = "s" ] && opciones="[S/n]"
  read -r -p "$1 $opciones " r || true
  r="${r:-$defecto}"
  [[ "$r" =~ ^[sSyY] ]]
}
# Contraseña aleatoria solo con letras y números (sin / ni + que rompen las URLs de conexión)
contrasena() { openssl rand -hex "${1:-16}"; }

# ---------- 0. Comprobaciones ----------
paso "0. Comprobaciones previas"
[ "$(id -u)" -ne 0 ] || fallo "ejecútalo con tu usuario normal (sin sudo); el script pide sudo cuando lo necesita."
[ "$(uname -m)" = "aarch64" ] || fallo "hace falta Raspberry Pi OS de 64 bits (uname -m = $(uname -m))."
command -v nmcli >/dev/null || fallo "no está NetworkManager (nmcli). Usa Raspberry Pi OS Bookworm o posterior."
sudo -v

# Red: un solo interfaz (eth0) con IP fija en la VLAN 500. Ya no hace falta adaptador USB.
# shellcheck disable=SC1091
source red/red.env
ip link show "$IF_RED" >/dev/null 2>&1 || fallo "no existe la interfaz $IF_RED."
echo "Red del instituto (VLAN 500): $IF_RED → $IP_RASPBERRY/$PREFIJO, puerta de enlace $PUERTA_ENLACE, DNS $DNS"
echo "Gateway LoRa (wAP LR8):       $IP_WAP"

# Si entramos por SSH con la IP del DHCP, al poner la IP fija nos quedaríamos fuera (CLAUDE.md, regla 8).
# En ese caso se prepara la red, se reinicia y se vuelve a ejecutar el script entrando por la IP fija.
CAMBIO_IP_PENDIENTE=n
ip_actual="$(ip -4 -o addr show "$IF_RED" | awk '{print $4}' | cut -d/ -f1 | head -n1)"
if [ -n "${SSH_CONNECTION:-}" ] && [ -n "$ip_actual" ] && [ "$ip_actual" != "$IP_RASPBERRY" ]; then
  amarillo "Estás por SSH con la IP $ip_actual. La IP fija $IP_RASPBERRY se aplicará al reiniciar;"
  amarillo "el script se para después de configurar la red para que no se corte a medias."
  CAMBIO_IP_PENDIENTE=s
fi

# ---------- 1. Datos que hay que preguntar ----------
paso "1. Contraseñas (.env)"
if [ ! -f .env ]; then
  umask 077
  cat > .env <<EOF
# Generado por instalar.sh el $(date -u +%F). NO se sube a git. Guardar una copia en lugar seguro.
POSTGRES_DB=calidad_agua
POSTGRES_USER=agua_admin
POSTGRES_PASSWORD=$(contrasena)
CHIRPSTACK_DB_PASSWORD=$(contrasena)
WEB_DB_PASSWORD=$(contrasena)
CHIRPSTACK_API_SECRET=$(contrasena 32)
EOF
  umask 022
  verde ".env creado con contraseñas aleatorias."
else
  amarillo ".env ya existe: se deja como está."
fi
# Datos del alta automática en ChirpStack. Se añaden también a un .env antiguo que no los tenga.
anadir_si_falta() { grep -q "^$1=" .env || echo "$1=$2" >> .env; }
anadir_si_falta CHIRPSTACK_ADMIN_PASSWORD "$(contrasena)"
anadir_si_falta NODO_DEV_EUI "$(openssl rand -hex 8)"
anadir_si_falta NODO_JOIN_EUI 0000000000000000
anadir_si_falta NODO_APP_KEY "$(openssl rand -hex 16)"
anadir_si_falta NODO_NWK_KEY "$(openssl rand -hex 16)"
if ! grep -q "^GATEWAY_EUI=." .env; then
  amarillo "EUI del wAP LR8 (16 cifras hex; en RouterOS: /iot lora print). Enter para darlo de alta más tarde."
  read -r -p "GATEWAY_EUI: " eui || true
  sed -i '/^GATEWAY_EUI=/d' .env
  echo "GATEWAY_EUI=${eui:-}" >> .env
fi
# shellcheck disable=SC1091
source .env
grep -q "cambiar_esto\|pegar_aqui" .env && fallo ".env tiene valores de ejemplo sin cambiar."

PONER_RTC=n
pregunta "¿Tiene puesta la batería RTC OFICIAL recargable de Raspberry Pi? (activa su carga; NO con pilas normales)" n && PONER_RTC=s

# ---------- 2. Sistema ----------
paso "2. Actualizando el sistema (tarda unos minutos)"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get -y full-upgrade
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install chrony ufw git curl openssl ca-certificates cron

# ---------- 3. Cuidar la microSD ----------
paso "3. Menos escrituras en la microSD"
sudo mkdir -p /etc/systemd/journald.conf.d
printf '[Journal]\nSystemMaxUse=100M\n' | sudo tee /etc/systemd/journald.conf.d/10-tfg.conf >/dev/null
sudo systemctl restart systemd-journald
echo "Diario del sistema limitado a 100 MB (los contenedores ya van limitados en docker-compose.yml)."

# ---------- 4. Reloj RTC ----------
paso "4. Reloj"
sudo timedatectl set-timezone Europe/Madrid
if [ "$PONER_RTC" = "s" ]; then
  if ! grep -q '^dtparam=rtc_bbat_vchg=' /boot/firmware/config.txt; then
    echo 'dtparam=rtc_bbat_vchg=3000000' | sudo tee -a /boot/firmware/config.txt >/dev/null
    amarillo "Carga de la batería RTC activada (tendrá efecto tras reiniciar)."
  fi
fi

# ---------- 5. Docker ----------
paso "5. Docker"
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
fi
sudo usermod -aG docker "$USUARIO"
sudo systemctl enable --now docker

# ---------- 6. Red ----------
paso "6. Red: $IF_RED → $IP_RASPBERRY/$PREFIJO (VLAN 500), puerta de enlace $PUERTA_ENLACE"
./red/configurar-red.sh
# chrony sirve la hora al wAP (la IP del wAP sale de red/red.env)
sed "s|^allow .*|allow $IP_WAP|" red/chrony.conf | sudo tee /etc/chrony/chrony.conf >/dev/null
sudo systemctl restart chrony
if [ "$CAMBIO_IP_PENDIENTE" = "s" ]; then
  verde "Red preparada. Ahora: sudo reboot, entra con  ssh $USUARIO@$IP_RASPBERRY  y vuelve a ejecutar ./instalar.sh"
  exit 0
fi
echo "Esperando salida a Internet..."
for _ in $(seq 1 30); do ping -c1 -W2 1.1.1.1 >/dev/null 2>&1 && break; sleep 2; done
ping -c1 -W2 1.1.1.1 >/dev/null 2>&1 || fallo "sin Internet por $IF_RED. Revisa el cable, que el puerto del switch esté en la VLAN 500 y la puerta de enlace $PUERTA_ENLACE."

# ---------- 7. Contenedores ----------
paso "7. Arrancando todos los servicios (la primera vez descarga las imágenes: unos minutos)"
sudo docker compose up -d --build
echo "Esperando a que la web responda..."
for _ in $(seq 1 60); do
  curl -fsS http://127.0.0.1/api/salud >/dev/null 2>&1 && break; sleep 5
done
curl -fsS http://127.0.0.1/api/salud >/dev/null 2>&1 || { sudo docker compose ps; fallo "la web no responde. Mira: sudo docker compose logs web caddy"; }
verde "Web funcionando."

# ---------- 7b. Alta en ChirpStack ----------
paso "7b. Alta automática en ChirpStack (gateway, perfil con decoder.js, aplicación y nodo)"
sudo docker compose run --rm --build provisionar || fallo "falló el alta en ChirpStack. Mira el mensaje de arriba."
sudo chown "$USUARIO:" ../firmware/nodo-agua/include/secrets.h

# ---------- 8. Firewall ----------
paso "8. Firewall"
./red/firewall.sh

# ---------- 9. Copia de seguridad diaria ----------
paso "9. Copia de seguridad diaria (03:00)"
linea_cron="0 3 * * * $CARPETA/backup.sh >> $HOME/backup-agua.log 2>&1"
cron_actual="$(crontab -l 2>/dev/null | grep -vF "$CARPETA/backup.sh" || true)"
printf '%s\n%s\n' "$cron_actual" "$linea_cron" | sed '/^$/d' | crontab -
crontab -l | grep backup.sh

# ---------- 10. Tailscale ----------
# El instituto no puede abrir puertos (decisión de 2026-10-26): todo lo de fuera entra por Tailscale,
# que solo hace conexiones de salida. Comandos sacados de la documentación oficial:
#   https://tailscale.com/kb/1223/funnel  y  https://tailscale.com/kb/1311/tailscale-funnel
#   Funnel solo admite los puertos 443, 8443 y 10000; Serve y Funnel no pueden compartir puerto.
paso "10. Tailscale (acceso del equipo y web pública)"
command -v tailscale >/dev/null || curl -fsSL https://tailscale.com/install.sh | sudo sh
if ! sudo tailscale status >/dev/null 2>&1; then
  amarillo "Abre el enlace que sale a continuación e inicia sesión con la cuenta del equipo:"
  sudo tailscale up
fi
# ChirpStack: solo para los equipos del tailnet (puerto 8443)
sudo tailscale serve --bg --https=8443 http://127.0.0.1:8080
# Web: pública en Internet con HTTPS (puerto 443 de Tailscale → Caddy en el 80)
amarillo "Si sale un enlace para activar HTTPS y Funnel en el tailnet, ábrelo con la cuenta del equipo y acepta (MagicDNS tiene que estar activado)."
sudo tailscale funnel --bg --https=443 http://127.0.0.1:80

# ---------- Resumen ----------
ip_instituto="$IP_RASPBERRY"
echo
verde "=================== INSTALACIÓN TERMINADA ==================="
echo "Web en el instituto:   http://$ip_instituto"
nombre_ts="$(sudo tailscale status --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))')"
echo "Web desde Internet:    https://$nombre_ts  (Tailscale Funnel)"
echo "ChirpStack (equipo):   https://$nombre_ts:8443  (solo desde equipos con Tailscale)"
echo "Pedir al coordinador TIC: dejar $IP_RASPBERRY y $IP_WAP fuera del DHCP de la VLAN 500 (no hay que abrir ningún puerto)."
echo
echo "ChirpStack: usuario admin, contraseña CHIRPSTACK_ADMIN_PASSWORD del fichero .env"
echo
amarillo "Queda a mano (docs/08-guia-instalacion.md, pasos 5 y 6):"
echo "  1. Configurar el wAP LR8 (IP $IP_WAP/$PREFIJO, puerta de enlace $PUERTA_ENLACE, NTP y servidor LoRa $IP_RASPBERRY:1700)."
if ! grep -q "^GATEWAY_EUI=." .env; then
  echo "     Después poner su EUI en GATEWAY_EUI del .env y ejecutar: sudo docker compose run --rm provisionar"
fi
echo "  2. Copiar firmware/nodo-agua/include/secrets.h (claves del nodo, ya generadas) al PC donde se graba la LILYGO."
echo "  3. Guardar una copia del fichero .env fuera de la Raspberry (tiene todas las contraseñas)."
echo "  4. Reiniciar una vez (sudo reboot) y comprobar que todo vuelve solo: sudo docker compose ps"
