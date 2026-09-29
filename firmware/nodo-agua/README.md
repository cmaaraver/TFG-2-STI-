# Firmware del nodo (LILYGO T3 V1.6.1)

Proyecto PlatformIO. Cómo cablearlo: `docs/03-conexionado-nodo.md`. Cómo grabarlo y calibrarlo paso a paso:
`docs/08-guia-instalacion.md` (apartados 1 a 3 y 6).

```
pio run -e lilygo_t3_v1_6_1                 # compilar
pio run -e lilygo_t3_v1_6_1 -t upload       # grabar
pio device monitor                          # monitor serie a 115200
```

Antes de compilar: copiar `include/secrets.example.h` a `include/secrets.h` y poner las claves de ChirpStack
(`secrets.h` no se sube a git).

## Qué hace cada ciclo (cada 15 min)
Despierta → enciende sensores y bomba → join o sesión guardada → 45 s de bombeo (los últimos 10 s mide el caudal)
→ para la bomba y espera 5 s → lee sensores → envía 16 bytes por LoRaWAN → enseña el resultado 5 s → deep sleep.

![Pantalla OLED](../../docs/img/pantalla-oled.png)

## Archivos
| Archivo | Qué hay |
|---|---|
| `platformio.ini` | Placas y librerías (versiones fijas) |
| `include/config.h` | **Todo lo ajustable**: pines, tiempos, caudalímetro, Modbus, ADS1115, pantalla |
| `include/secrets.example.h` | Plantilla de las claves LoRaWAN |
| `include/payload.h` | Formato del mensaje (`docs/04-formato-payload.md`) |
| `src/main.cpp` | Ciclo completo, LoRaWAN (RadioLib) y deep sleep |
| `src/sensores.cpp` | pH, nivel y batería (ADS1115), oxígeno y temperatura (SEN0681 por RS485), caudal, bomba y modo calibración |
| `src/pantalla.cpp` | OLED: logo, fase del ciclo y temporizador del envío (tarea de FreeRTOS) |
| `src/i2c_compartido.cpp` | Mutex para que la OLED y el ADS1115 no usen el bus I2C a la vez |
| `include/logo.h` | Logo de Los Viveros en XBM, generado con `herramientas/logo_a_xbm.py` |

Lo que queda por confirmar está marcado con `TODO VERIFICAR` en `config.h` (registros Modbus del SEN0681,
factor del caudalímetro, rango del KIT0139).
