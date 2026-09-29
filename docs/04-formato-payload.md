# Formato del mensaje LoRaWAN (versión 2)

fPort 1, 16 bytes, big-endian. Valor "sin dato": 0xFFFF (sin signo) o 0x7FFF (con signo).
El decodificador acepta también la versión 1 (14 bytes, sin caudal).

Los bytes 8-9 eran la conductividad. Al quitar esa sonda (decisión del 2026-09-29) el formato **no cambia**:
el firmware manda siempre 0xFFFF ("sin dato"), `decoder.js` lo traduce a `conductividad_uscm: null` y la base
de datos guarda NULL. Así no hay que tocar ni el decodificador ni la tabla, y el hueco queda libre por si
algún día se añade otro sensor (sería la versión 3).

| Byte | Campo | Tipo | Escala | Ejemplo |
|---|---|---|---|---|
| 0 | versión | uint8 | — | 2 |
| 1 | flags | uint8 | bit0 agua presente, bit1 fallo RS485, bit2 fallo ADS1115, bit3 batería baja, bit4 temperatura por defecto, bit5 bomba sin caudal | 0x01 |
| 2-3 | temperatura agua | int16 | ×100 °C | 2150 → 21,50 °C |
| 4-5 | oxígeno disuelto | uint16 | ×100 mg/L | 812 → 8,12 mg/L |
| 6-7 | pH | uint16 | ×100 | 734 → 7,34 |
| 8-9 | reservado | uint16 | — | siempre 0xFFFF (antes conductividad, que ya no se mide) |
| 10-11 | nivel | uint16 | mm | 1250 |
| 12-13 | batería | uint16 | mV | 13150 |
| 14-15 | caudal bomba | uint16 | ×100 L/min | 450 → 4,50 L/min |

## Downlink de configuración (fPort 10)
| Byte 0 (comando) | Datos | Acción |
|---|---|---|
| 0x01 | uint16 minutos (5-120) | Cambiar intervalo de envío |

Con envíos cada 15 min y 16 bytes a SF7-SF10, el tiempo en el aire está muy por debajo
del 1 % permitido en la sub-banda de 868 MHz.

## Prueba sin hardware

`pruebas/payload/probar.sh` compila `firmware/nodo-agua/include/payload.h` en el PC, genera tres mensajes
(normal, batería baja con temperatura negativa y todo sin dato), los pasa por `raspberry/codec/decoder.js`
y comprueba cada valor y que el decodificador da todos los campos que lee el ingestor. También comprueba
el downlink de intervalo. Necesita `g++` y `node`:

```
$ sh pruebas/payload/probar.sh
normal: 02010859034a02f9ffff019c339a0181
  {"version":2,"flags":1,"agua_presente":true,...,"temperatura_c":21.37,"oxigeno_mgl":8.42,"ph":7.61,
   "conductividad_uscm":null,"nivel_mm":412,"bateria_v":13.21,"caudal_lmin":3.85}
...
TODO OK (3 payloads, 10 campos del ingestor comprobados)
```
