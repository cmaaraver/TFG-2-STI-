# Formato del mensaje LoRaWAN (versión 2)

fPort 1, 16 bytes, big-endian. Valor "sin dato": 0xFFFF (sin signo) o 0x7FFF (con signo).
El decodificador acepta también la versión 1 (14 bytes, sin caudal).

| Byte | Campo | Tipo | Escala | Ejemplo |
|---|---|---|---|---|
| 0 | versión | uint8 | — | 2 |
| 1 | flags | uint8 | bit0 agua presente, bit1 fallo RS485, bit2 fallo ADS1115, bit3 batería baja, bit4 temperatura por defecto, bit5 bomba sin caudal | 0x01 |
| 2-3 | temperatura agua | int16 | ×100 °C | 2150 → 21,50 °C |
| 4-5 | oxígeno disuelto | uint16 | ×100 mg/L | 812 → 8,12 mg/L |
| 6-7 | pH | uint16 | ×100 | 734 → 7,34 |
| 8-9 | conductividad | uint16 | µS/cm (a 25 °C) | 640 |
| 10-11 | nivel | uint16 | mm | 1250 |
| 12-13 | batería | uint16 | mV | 13150 |
| 14-15 | caudal bomba | uint16 | ×100 L/min | 450 → 4,50 L/min |

## Downlink de configuración (fPort 10)
| Byte 0 (comando) | Datos | Acción |
|---|---|---|
| 0x01 | uint16 minutos (5-120) | Cambiar intervalo de envío |

Con envíos cada 15 min y 16 bytes a SF7-SF10, el tiempo en el aire está muy por debajo
del 1 % permitido en la sub-banda de 868 MHz.
