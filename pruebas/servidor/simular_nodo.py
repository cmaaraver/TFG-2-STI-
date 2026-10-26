"""
Simula el wAP LR8 y el nodo LILYGO contra el servidor de la Raspberry, sin hardware.

Hace lo mismo que harían los equipos de verdad: el "gateway" se conecta al Gateway Bridge por UDP 1700
(protocolo Semtech), el "nodo" hace el join OTAA con LoRaWAN 1.1 usando las claves del .env
y luego manda un uplink con el formato v2 (docs/04-formato-payload.md). Si todo está bien,
la medida acaba en la base de datos y en la web.

Uso (con el servidor arrancado y provisionar ya ejecutado):
    python3 pruebas/servidor/simular_nodo.py raspberry/.env

Necesita el paquete "cryptography" (pip install cryptography).
Referencias: especificación LoRaWAN 1.1 (apartados 4.4, 6.2.2 y 6.2.3) y protocolo UDP de Semtech
(https://github.com/Lora-net/packet_forwarder/blob/master/PROTOCOL.TXT).
"""
import base64
import json
import os
import socket
import struct
import sys
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.cmac import CMAC

SERVIDOR = ("127.0.0.1", 1700)


def leer_env(ruta):
    datos = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                datos[clave] = valor
    return datos


def aes(clave, bloque):
    cifrador = Cipher(algorithms.AES(clave), modes.ECB()).encryptor()
    return cifrador.update(bloque) + cifrador.finalize()


def cmac(clave, datos):
    c = CMAC(algorithms.AES(clave))
    c.update(datos)
    return c.finalize()


def al_reves(texto_hex):
    # En el aire los EUI van al revés (LSB primero) de como se leen en ChirpStack
    return bytes.fromhex(texto_hex)[::-1]


def payload_v2():
    # 21,50 °C, 8,30 mg/L, pH 7,20, sin conductividad, 600 mm, 12,0 V, 3,50 L/min, hay agua
    return struct.pack(">BBhHHHHHH", 2, 0x01, 2150, 830, 720, 0xFFFF, 600, 12000, 350)


class Gateway:
    """Lo mínimo del packet forwarder de Semtech: PULL_DATA, PUSH_DATA y TX_ACK."""

    def __init__(self, eui):
        self.eui = bytes.fromhex(eui)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)

    def enviar(self, tipo, json_datos=None):
        trama = bytes([2]) + os.urandom(2) + bytes([tipo]) + self.eui
        if json_datos is not None:
            trama += json.dumps(json_datos).encode()
        self.sock.sendto(trama, SERVIDOR)

    def conectar(self):
        self.enviar(0x02)                               # PULL_DATA: "estoy aquí, mándame los downlinks"
        respuesta, _ = self.sock.recvfrom(1024)
        assert respuesta[3] == 0x04, "no llega PULL_ACK del Gateway Bridge"

    def recibir_por_radio(self, phy):
        # Uplink en 868,1 MHz, SF7 BW125 (= DR5, canal 0 en EU868)
        rxpk = {"tmst": int(time.time() * 1e6) & 0xFFFFFFFF, "chan": 0, "rfch": 0, "freq": 868.1,
                "stat": 1, "modu": "LORA", "datr": "SF7BW125", "codr": "4/5", "rssi": -62, "lsnr": 9.5,
                "size": len(phy), "data": base64.b64encode(phy).decode()}
        self.enviar(0x00, {"rxpk": [rxpk]})             # PUSH_DATA

    def esperar_downlink(self, segundos=10):
        limite = time.time() + segundos
        while time.time() < limite:
            try:
                trama, _ = self.sock.recvfrom(4096)
            except socket.timeout:
                self.enviar(0x02)
                continue
            if trama[3] == 0x03:                        # PULL_RESP con el txpk
                self.sock.sendto(trama[:3] + bytes([0x05]) + self.eui, SERVIDOR)   # TX_ACK
                return base64.b64decode(json.loads(trama[4:])["txpk"]["data"])
        return None


def main():
    env = leer_env(sys.argv[1] if len(sys.argv) > 1 else "raspberry/.env")
    nwk_key = bytes.fromhex(env["NODO_NWK_KEY"])
    app_key = bytes.fromhex(env["NODO_APP_KEY"])
    join_eui = al_reves(env.get("NODO_JOIN_EUI", "0" * 16))
    dev_eui = al_reves(env["NODO_DEV_EUI"])

    gw = Gateway(env["GATEWAY_EUI"])
    gw.conectar()
    print("1. Gateway conectado al Gateway Bridge (UDP 1700)")

    # ---- Join request (LoRaWAN 1.1, apartado 6.2.2) ----
    # En 1.1 el DevNonce es un contador que solo sube: se usa la hora para que cada prueba lleve uno mayor
    dev_nonce = struct.pack("<H", int(time.time() / 10) & 0xFFFF)
    mensaje = bytes([0x00]) + join_eui + dev_eui + dev_nonce
    gw.recibir_por_radio(mensaje + cmac(nwk_key, mensaje)[:4])
    respuesta = gw.esperar_downlink()
    if respuesta is None:
        sys.exit("FALLO: no llega el join accept. Mira: docker compose logs chirpstack")

    # El servidor "descifra" el join accept con AES; el nodo lo recupera cifrando (apartado 6.2.3)
    claro = aes(nwk_key, respuesta[1:])
    join_nonce, dev_addr, dl_settings = claro[0:3], claro[6:10], claro[10]
    assert dl_settings & 0x80, "el servidor no ha contestado como LoRaWAN 1.1 (OptNeg a 0)"
    print(f"2. Join aceptado: DevAddr {dev_addr[::-1].hex()}")

    def clave_sesion(clave, tipo):
        return aes(clave, (bytes([tipo]) + join_nonce + join_eui + dev_nonce).ljust(16, b"\x00"))

    f_nwk_s_int = clave_sesion(nwk_key, 0x01)
    app_s = clave_sesion(app_key, 0x02)
    s_nwk_s_int = clave_sesion(nwk_key, 0x03)

    # ---- Uplink sin confirmar, FPort 1, FCnt 0 (apartado 4.3.3 y 4.4) ----
    fcnt = 0
    datos = payload_v2()
    flujo = b"".join(aes(app_s, bytes([1, 0, 0, 0, 0, 0]) + dev_addr + struct.pack("<I", fcnt) + bytes([0, i + 1]))
                     for i in range((len(datos) + 15) // 16))
    cifrado = bytes(a ^ b for a, b in zip(datos, flujo))
    mensaje = bytes([0x40]) + dev_addr + bytes([0x00]) + struct.pack("<H", fcnt) + bytes([1]) + cifrado
    b0 = bytes([0x49, 0, 0, 0, 0, 0]) + dev_addr + struct.pack("<I", fcnt) + bytes([0, len(mensaje)])
    b1 = bytes([0x49, 0, 0, 5, 0, 0]) + dev_addr + struct.pack("<I", fcnt) + bytes([0, len(mensaje)])  # DR5, canal 0
    mic = cmac(s_nwk_s_int, b1 + mensaje)[:2] + cmac(f_nwk_s_int, b0 + mensaje)[:2]
    gw.recibir_por_radio(mensaje + mic)
    print("3. Uplink enviado: 21,50 °C, 8,30 mg/L, pH 7,20, nivel 600 mm, 12,0 V, 3,50 L/min")
    print("Ahora comprobar la base de datos y la web (pruebas/README.md)")


if __name__ == "__main__":
    main()
