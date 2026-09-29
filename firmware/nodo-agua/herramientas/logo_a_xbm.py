#!/usr/bin/env python3
"""Convierte el logo de Los Viveros (PNG) en include/logo.h para la pantalla OLED.

Uso:
  pip install pillow
  curl -O https://cpifplosviveros.es/wp-content/uploads/2022/06/logo_losviveros.png
  python3 herramientas/logo_a_xbm.py logo_losviveros.png > include/logo.h

El logo se escala a 128 px de ancho (el ancho de la pantalla) y se pasa a blanco y negro:
un píxel se enciende si no es transparente y es oscuro (en la OLED el fondo es negro,
así que lo que en la web es tinta, en la pantalla se ve encendido).
"""
import sys
from PIL import Image

ANCHO = 128
UMBRAL_ALFA = 110   # por debajo, el píxel se considera transparente
UMBRAL_LUZ = 215    # por encima, el píxel se considera fondo blanco

img = Image.open(sys.argv[1]).convert("RGBA")
alto = round(img.height * ANCHO / img.width)
img = img.resize((ANCHO, alto), Image.LANCZOS)

bytes_xbm = []
for y in range(alto):
    for x0 in range(0, ANCHO, 8):
        byte = 0
        for bit in range(8):          # XBM: el bit menos significativo es el píxel de la izquierda
            r, g, b, a = img.getpixel((x0 + bit, y))
            luz = 0.299 * r + 0.587 * g + 0.114 * b
            if a > UMBRAL_ALFA and luz < UMBRAL_LUZ:
                byte |= 1 << bit
        bytes_xbm.append(byte)

print("#pragma once")
print(f"// Logo del CPIFP Los Viveros para la pantalla OLED ({ANCHO}x{alto} píxeles, formato XBM para U8g2).")
print("// Generado a partir de https://cpifplosviveros.es/wp-content/uploads/2022/06/logo_losviveros.png")
print("// con herramientas/logo_a_xbm.py (escalado a 128 px de ancho y pasado a blanco y negro).")
print("#include <Arduino.h>")
print()
print(f"#define LOGO_ANCHO {ANCHO}")
print(f"#define LOGO_ALTO  {alto}")
print()
print("static const unsigned char LOGO_VIVEROS[] PROGMEM = {")
for i in range(0, len(bytes_xbm), 16):
    print("  " + ", ".join(f"0x{v:02x}" for v in bytes_xbm[i:i + 16]) + ",")
print("};")
