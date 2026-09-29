#!/bin/sh
# Prueba de punta a punta del formato del mensaje, sin hardware:
#   payload.h del firmware (C++) → decoder.js de ChirpStack (Node) → campos del ingestor
# Necesita g++ y node. Uso: sh pruebas/payload/probar.sh
set -e
cd "$(dirname "$0")"
FW=../../firmware/nodo-agua/include
# config.h pide elegir placa; para esta prueba solo hace falta BATERIA_BAJA_MV
g++ -std=c++17 -Wall -I stub -I "$FW" -DPLACA_LILYGO_T3_V1_6_1 -o /tmp/generar_payload generar.cpp
/tmp/generar_payload | node comprobar.js
