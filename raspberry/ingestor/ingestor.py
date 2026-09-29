"""
Ingestor: se suscribe a los uplinks de ChirpStack (MQTT, QoS 1, sesión persistente)
y los guarda en TimescaleDB. Si el ingestor se para, Mosquitto guarda los mensajes
y se insertan al volver. Los duplicados se descartan por dedup_id.
"""
import json
import logging
import os
import time

import paho.mqtt.client as mqtt
import psycopg

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingestor")

MQTT_HOST = os.environ.get("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER")          # vacío: broker interno sin usuario
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "application/+/device/+/event/up")
PG_DSN = os.environ["PG_DSN"]

SQL_MEDIDA = """
INSERT INTO medidas (tiempo, dedup_id, dev_eui, fcnt, temperatura_c, oxigeno_mgl, ph,
                     conductividad_uscm, nivel_mm, bateria_v, caudal_lmin, agua_presente, bomba_sin_caudal, flags,
                     rssi_dbm, snr_db, gateway_id, spreading_factor)
VALUES (%(tiempo)s, %(dedup_id)s, %(dev_eui)s, %(fcnt)s, %(temperatura_c)s, %(oxigeno_mgl)s, %(ph)s,
        %(conductividad_uscm)s, %(nivel_mm)s, %(bateria_v)s, %(caudal_lmin)s, %(agua_presente)s,
        %(bomba_sin_caudal)s, %(flags)s,
        %(rssi_dbm)s, %(snr_db)s, %(gateway_id)s, %(spreading_factor)s)
ON CONFLICT DO NOTHING
"""
SQL_RAW = "INSERT INTO uplinks_raw (dedup_id, tiempo, mensaje) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
SQL_NODO = "INSERT INTO nodos (dev_eui, nombre) VALUES (%s, %s) ON CONFLICT (dev_eui) DO NOTHING"


def conectar_bd():
    while True:
        try:
            conn = psycopg.connect(PG_DSN, autocommit=True)
            log.info("Conectado a la base de datos")
            return conn
        except psycopg.OperationalError as e:
            log.warning("BD no disponible (%s), reintento en 5 s", e)
            time.sleep(5)


conn = conectar_bd()


def mejor_gateway(rx_info):
    """Devuelve la recepción con mejor SNR (si hay varios gateways)."""
    if not rx_info:
        return {}
    return max(rx_info, key=lambda r: r.get("snr", -99))


def procesar(evento: dict):
    global conn
    info = evento.get("deviceInfo", {})
    obj = evento.get("object") or {}
    rx = mejor_gateway(evento.get("rxInfo", []))
    lora = evento.get("txInfo", {}).get("modulation", {}).get("lora", {})

    fila = {
        "tiempo": evento["time"],
        "dedup_id": evento["deduplicationId"],
        "dev_eui": info.get("devEui"),
        "fcnt": evento.get("fCnt"),
        "temperatura_c": obj.get("temperatura_c"),
        "oxigeno_mgl": obj.get("oxigeno_mgl"),
        "ph": obj.get("ph"),
        "conductividad_uscm": obj.get("conductividad_uscm"),
        "nivel_mm": obj.get("nivel_mm"),
        "bateria_v": obj.get("bateria_v"),
        "caudal_lmin": obj.get("caudal_lmin"),
        "agua_presente": obj.get("agua_presente"),
        "bomba_sin_caudal": obj.get("bomba_sin_caudal"),
        "flags": obj.get("flags"),
        "rssi_dbm": rx.get("rssi"),
        "snr_db": rx.get("snr"),
        "gateway_id": rx.get("gatewayId"),
        "spreading_factor": lora.get("spreadingFactor"),
    }
    for intento in range(2):
        try:
            with conn.transaction():
                conn.execute(SQL_NODO, (fila["dev_eui"], info.get("deviceName")))
                conn.execute(SQL_RAW, (fila["dedup_id"], fila["tiempo"], json.dumps(evento)))
                conn.execute(SQL_MEDIDA, fila)
            log.info("Guardado %s fcnt=%s", fila["dev_eui"], fila["fcnt"])
            return
        except psycopg.OperationalError:
            log.warning("Conexión con la BD perdida, reconectando")
            conn = conectar_bd()
    raise RuntimeError("No se pudo guardar el mensaje")


def al_conectar(cliente, userdata, flags, codigo, propiedades):
    if codigo == 0:
        log.info("Conectado a MQTT %s:%s", MQTT_HOST, MQTT_PORT)
        cliente.subscribe(MQTT_TOPIC, qos=1)
    else:
        log.error("Fallo de conexión MQTT: %s", codigo)


def al_mensaje(cliente, userdata, msg):
    try:
        procesar(json.loads(msg.payload))
    except Exception:
        log.exception("Error procesando mensaje de %s", msg.topic)


cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="ingestor-agua",   # id fijo + clean_session False = cola persistente en el broker
    clean_session=False,
)
if MQTT_USER:
    cliente.username_pw_set(MQTT_USER, MQTT_PASSWORD)
cliente.on_connect = al_conectar
cliente.on_message = al_mensaje
cliente.reconnect_delay_set(min_delay=1, max_delay=60)

while True:
    try:
        cliente.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        break
    except OSError as e:
        log.warning("Broker no disponible (%s), reintento en 5 s", e)
        time.sleep(5)

cliente.loop_forever(retry_first_connection=True)
