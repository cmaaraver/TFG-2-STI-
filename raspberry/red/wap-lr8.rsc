# Configuración del gateway MikroTik wAP LR8 (RouterOS 7) para el TFG.
# Se pega en la terminal del wAP (WinBox → New Terminal, o SSH). Datos de red: raspberry/red/red.env.
#
# Fuentes (documentación oficial de MikroTik, consultada el 2026-10-29):
#   - Guía ChirpStack:   https://manual.mikrotik.com/docs/internet-of-things/lora/user-guides/chirpstack/
#     (desactivar la interfaz, añadir el servidor, asignarlo, activar y mirar el log "forwarder is ready")
#   - Propiedades LoRa:  https://help.mikrotik.com/docs/spaces/ROS/pages/16351619/General+Properties
#     (/iot lora servers: address, name, protocol=UDP, up-port=1700, down-port=1700;
#      /iot lora: channel-plan=eu-868 y network=public son los valores por defecto)
#   - Hace falta el paquete "iot" instalado (/system package print) para que exista /iot lora.
#
# ANTES: la configuración de fábrica (defconf) mete ether1 y wlan1 en bridgeLocal, así que la IP va en
#        bridgeLocal y no en ether1 (comprobado el 2026-11-12). Gateway-id de nuestro wAP: 04F41CFFFFC15CEB.

# --- 1. Red: IP fija en la VLAN 500 (la toma del switch entrega la VLAN sin etiquetar) ---
/ip dhcp-client remove [find]
/ip address add address=172.16.50.2/24 interface=bridgeLocal comment="VLAN 500 instituto"
/ip route add dst-address=0.0.0.0/0 gateway=172.16.50.1
# 172.16.50.1 no hace de DNS (comprobado el 2026-10-29): mismos DNS que la Raspberry
/ip dns set servers=1.1.1.1,192.168.2.1
/system identity set name=wap-lr8-tfg

# --- 2. Hora: NTP de la Raspberry (chrony solo deja pedir hora a 172.16.50.2) ---
/system ntp client set enabled=yes servers=172.16.50.3

# --- 3. LoRa: reenviar a ChirpStack Gateway Bridge (UDP 1700 en la Raspberry) ---
/iot lora disable [find]
/iot lora servers add name=chirpstack address=172.16.50.3 protocol=UDP up-port=1700 down-port=1700
# Sin esta pausa el set da "failure: Device is busy" (la tarjeta aún se está parando; visto el 2026-11-12)
:delay 5s
# network=public: la LILYGO (RadioLib) usa la palabra de sincronización pública de LoRaWAN; de fábrica venía private.
# forward solo con crc-validation: reenvía todo lo que llega bien y ChirpStack decide (de fábrica llevaba también dev-addr-validation)
/iot lora set [find] servers=chirpstack channel-plan=eu-868 network=public forward=crc-validation
/iot lora enable [find]

# --- 4. Comprobar ---
# /iot lora print detail            → anotar gateway-id (EUI de 16 cifras) para GATEWAY_EUI del .env
#                                     (en WinBox: IoT → LoRa → Devices → Gateway ID)
# /log print where topics~"lora"    → tiene que salir "forwarder is ready"
# /ping 172.16.50.3 count=3
#
# --- 5. Seguridad (está en una VLAN compartida) ---
# Poner contraseña al usuario admin:  /user set admin password=...   (no se guarda en este fichero)
# Si no se usa la WiFi del wAP, desactivarla desde WinBox (Wireless/WiFi → Disable).
