#!/usr/bin/env python3
"""Manda comandos al modo calibración de la LILYGO por el puerto serie y enseña la respuesta.

Sirve para calibrar sin escribir a mano en el monitor serie (por ejemplo, desde un script o desde Claude Code).
La LILYGO tiene que estar con el puente de calibración (IO15 a GND) y el firmware lilygo_t3_simple.
Usa pyserial, que viene instalado con PlatformIO.

Ejemplos (Windows, LILYGO en COM7):
    python calibrar.py COM7 leer
    python calibrar.py COM7 mv leer
    python calibrar.py COM7 ph7          (con la sonda en el tampón 7)
    python calibrar.py COM7 --sin-reset sal

Por defecto el script reinicia la placa (línea RTS del USB, como esptool) y espera el menú y los 60 s de calentamiento.
Con --sin-reset no la reinicia ni espera (vale si la placa ya está en el menú).
"""
import argparse
import sys
import time

import serial  # pyserial

ESPERA_MENU_S = 90      # 60 s de calentamiento del firmware + arranque, con margen
ESPERA_RESPUESTA_S = 8  # cada comando hace una medida completa (15 muestras por sensor + Modbus)


def leer_hasta(puerto, texto, limite_s):
    """Lee líneas y las enseña hasta que aparezca `texto` o pase el tiempo. Devuelve True si apareció."""
    fin = time.time() + limite_s
    while time.time() < fin:
        linea = puerto.readline().decode(errors="replace").rstrip()
        if linea:
            print(linea)
            if texto in linea:
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Comandos del modo calibración de la LILYGO")
    ap.add_argument("puerto", help="COM7 en Windows, /dev/ttyUSB0 o /dev/ttyACM0 en Linux")
    ap.add_argument("comandos", nargs="+", help="leer, mv, ph7, ph4, nivel0, sal, sal0, o2_100, o2_cero, ver, reset")
    ap.add_argument("--sin-reset", action="store_true", help="no reiniciar la placa al abrir el puerto")
    args = ap.parse_args()

    puerto = serial.Serial()
    puerto.port = args.puerto
    puerto.baudrate = 115200
    puerto.timeout = 1
    puerto.dtr = False   # DTR suelto = IO0 alto (arranque normal, no modo de grabación)
    puerto.rts = False
    puerto.open()

    if not args.sin_reset:
        # Reinicio como lo hace esptool: RTS activo baja EN un momento
        puerto.rts = True
        time.sleep(0.2)
        puerto.rts = False
        print(f"Esperando el menú de calibración (hasta {ESPERA_MENU_S} s)...")
        if not leer_hasta(puerto, "Comandos:", ESPERA_MENU_S):
            print("No sale el menú: ¿está el puente IO15-GND puesto y grabado lilygo_t3_simple?")
            return 1
        # Después del menú el firmware espera 60 s a que se calienten los sensores
        leer_hasta(puerto, "@@nunca@@", 62)

    for c in args.comandos:
        print(f"> {c}")
        puerto.write((c + "\n").encode())
        leer_hasta(puerto, "@@nunca@@", ESPERA_RESPUESTA_S)
    puerto.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
