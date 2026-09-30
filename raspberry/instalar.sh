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
#  Deja listo: sistema actualizado, cuidado de la microSD, reloj RTC, Docker, las dos redes
#  (wAP y red del instituto), NTP para el wAP, contraseñas generadas, DuckDNS, todos los
#  contenedores (ChirpStack, MQTT, base de datos, web, HTTPS), firewall, copia de seguridad
#  diaria y, si se quiere, Tailscale.
#
#  Se puede volver a ejecutar sin miedo: lo que ya está hecho se salta.
#  Antes, leer docs/09-guia-duckdns.md y tener a mano el subdominio y el token de DuckDNS.
#
#  Opciones (variables de entorno):
#    IF_LORA=eth0 IF_INSTITUTO=eth1 ./instalar.sh     # si las interfaces se llaman distinto
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

# Interfaces: eth0 (integrada) va al wAP; el adaptador USB va a la red del instituto
IF_LORA="${IF_LORA:-eth0}"
if [ -z "${IF_INSTITUTO:-}" ]; then
  for i in /sys/class/net/*; do
    n="$(basename "$i")"
    [ "$n" = "$IF_LORA" ] && continue
    [ -e "$i/device" ] || continue                 # solo interfaces físicas
    [ -d "$i/wireless" ] && continue               # sin WiFi
    [ "$(cat "$i/type")" = "1" ] || continue       # Ethernet
    IF_INSTITUTO="$n"; break
  done
fi
[ -n "${IF_INSTITUTO:-}" ] || fallo "no encuentro el adaptador USB-Ethernet. Conéctalo (con el cable del instituto) y repite."
ip link show "$IF_LORA" >/dev/null 2>&1 || fallo "no existe la interfaz $IF_LORA."
echo "Red del wAP (LoRa):     $IF_LORA  → 192.168.50.1/24"
echo "Red del instituto:      $IF_INSTITUTO  → DHCP"

# Si entramos por SSH justo por la interfaz que va a cambiar, nos quedaríamos fuera (CLAUDE.md, regla 8)
if [ -n "${SSH_CONNECTION:-}" ]; then
  ip_cliente="$(echo "$SSH_CONNECTION" | awk '{print $1}')"
  if_ssh="$(ip route get "$ip_cliente" 2>/dev/null | grep -o 'dev [^ ]*' | awk '{print $2}')"
  if [ "$if_ssh" = "$IF_LORA" ] && ! nmcli -t -f NAME con show --active | grep -qx red-lora; then
    rojo "Estás conectado por SSH a través de $IF_LORA, que va a pasar a ser la red del wAP."
    rojo "Conecta el cable del instituto al adaptador USB ($IF_INSTITUTO), entra por esa IP"
    rojo "o usa teclado y monitor, y vuelve a ejecutar el script."
    exit 1
  fi
fi

# ---------- 1. Datos que hay que preguntar ----------
paso "1. Datos de DuckDNS (ver docs/09-guia-duckdns.md)"
if [ ! -f .env ]; then
  read -r -p "Subdominio de DuckDNS (solo el nombre, sin .duckdns.org): " dominio
  read -r -p "Token de DuckDNS: " token
  dominio="${dominio%.duckdns.org}"
  [[ "$dominio" =~ ^[a-z0-9-]+$ ]] || fallo "el subdominio solo puede tener minúsculas, números y guiones."
  [[ "$token" =~ ^[0-9a-f-]{36}$ ]] || fallo "el token de DuckDNS tiene el formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."
  # Comprobar el token contra DuckDNS antes de seguir (actualiza la IP una vez)
  respuesta="$(curl -fsS "https://www.duckdns.org/update?domains=$dominio&token=$token" || true)"
  [ "$respuesta" = "OK" ] || fallo "DuckDNS rechaza el subdominio o el token (respuesta: '$respuesta')."
  umask 077
  cat > .env <<EOF
# Generado por instalar.sh el $(date -u +%F). NO se sube a git. Guardar una copia en lugar seguro.
POSTGRES_DB=calidad_agua
POSTGRES_USER=agua_admin
POSTGRES_PASSWORD=$(contrasena)
CHIRPSTACK_DB_PASSWORD=$(contrasena)
WEB_DB_PASSWORD=$(contrasena)
CHIRPSTACK_API_SECRET=$(contrasena 32)
DUCKDNS_DOMINIO=$dominio
DUCKDNS_TOKEN=$token
EOF
  umask 022
  verde ".env creado con contraseñas aleatorias."
else
  amarillo ".env ya existe: se deja como está."
fi
# shellcheck disable=SC1091
source .env
grep -q "cambiar_esto\|pegar_aqui" .env && fallo ".env tiene valores de ejemplo sin cambiar."

INSTALAR_TAILSCALE=n
pregunta "¿Instalar Tailscale (acceso del equipo a SSH y ChirpStack desde fuera)?" s && INSTALAR_TAILSCALE=s
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
paso "6. Red: $IF_LORA → wAP (192.168.50.1) y $IF_INSTITUTO → instituto (DHCP)"
IF_LORA="$IF_LORA" IF_INSTITUTO="$IF_INSTITUTO" ./red/configurar-red.sh
sudo cp red/chrony.conf /etc/chrony/chrony.conf
sudo systemctl restart chrony
echo "Esperando salida a Internet..."
for _ in $(seq 1 30); do ping -c1 -W2 1.1.1.1 >/dev/null 2>&1 && break; sleep 2; done
ping -c1 -W2 1.1.1.1 >/dev/null 2>&1 || fallo "sin Internet por $IF_INSTITUTO. Revisa el cable y vuelve a ejecutar."

# ---------- 7. Contenedores ----------
paso "7. Arrancando todos los servicios (la primera vez compila Caddy: 5-15 min)"
sudo docker compose up -d --build
echo "Esperando a que la web responda..."
for _ in $(seq 1 60); do
  curl -fsS http://127.0.0.1/api/salud >/dev/null 2>&1 && break; sleep 5
done
curl -fsS http://127.0.0.1/api/salud >/dev/null 2>&1 || { sudo docker compose ps; fallo "la web no responde. Mira: sudo docker compose logs web caddy"; }
verde "Web funcionando."

# ---------- 8. Firewall ----------
paso "8. Firewall"
IF_LORA="$IF_LORA" IF_INSTITUTO="$IF_INSTITUTO" ./red/firewall.sh

# ---------- 9. Copia de seguridad diaria ----------
paso "9. Copia de seguridad diaria (03:00)"
linea_cron="0 3 * * * $CARPETA/backup.sh >> $HOME/backup-agua.log 2>&1"
cron_actual="$(crontab -l 2>/dev/null | grep -vF "$CARPETA/backup.sh" || true)"
printf '%s\n%s\n' "$cron_actual" "$linea_cron" | sed '/^$/d' | crontab -
crontab -l | grep backup.sh

# ---------- 10. Tailscale ----------
if [ "$INSTALAR_TAILSCALE" = "s" ]; then
  paso "10. Tailscale"
  command -v tailscale >/dev/null || curl -fsSL https://tailscale.com/install.sh | sudo sh
  amarillo "Abre el enlace que sale a continuación e inicia sesión con la cuenta del equipo:"
  sudo tailscale up
  sudo tailscale serve --bg --https=8443 http://127.0.0.1:8080
fi

# ---------- Resumen ----------
ip_instituto="$(ip -4 -o addr show "$IF_INSTITUTO" | awk '{print $4}' | cut -d/ -f1)"
mac_instituto="$(cat "/sys/class/net/$IF_INSTITUTO/address" 2>/dev/null || echo "(ver ip link)")"
echo
verde "=================== INSTALACIÓN TERMINADA ==================="
echo "Web en el instituto:   http://$ip_instituto"
echo "Web desde Internet:    https://$DUCKDNS_DOMINIO.duckdns.org  (cuando el TIC abra el 443, ver docs/09)"
echo "Pedir al coordinador TIC: reservar $ip_instituto para la MAC $mac_instituto y reenviar TCP 443."
if [ "$INSTALAR_TAILSCALE" = "s" ]; then
  echo "ChirpStack:            la dirección https://...ts.net:8443 que sale en: sudo tailscale serve status"
else
  echo "ChirpStack:            ssh -L 8080:127.0.0.1:8080 $USUARIO@$ip_instituto  → http://localhost:8080"
fi
echo
amarillo "Queda a mano (docs/08-guia-instalacion.md, pasos 5 y 6):"
echo "  1. Configurar el wAP LR8 (IP 192.168.50.2, servidor LoRa 192.168.50.1:1700)."
echo "  2. ChirpStack: cambiar la contraseña de admin/admin, dar de alta el gateway, el perfil con"
echo "     codec/decoder.js y el dispositivo; copiar sus claves a firmware/nodo-agua/include/secrets.h."
echo "  3. Guardar una copia del fichero .env fuera de la Raspberry (tiene todas las contraseñas)."
echo "  4. Reiniciar una vez (sudo reboot) y comprobar que todo vuelve solo: sudo docker compose ps"
