# Guía de calibración de los sensores (y cómo grabar el firmware real)

Esta guía sirve para pasar la LILYGO del firmware de **simulación** al firmware **real** y dejar calibrados los
sensores que tenemos de verdad. Está escrita para que la siga cualquiera del grupo (o Claude Code con la LILYGO
conectada al PC por USB). El cableado es el de `docs/12-guia-montaje.md` (montaje simple en la protoboard). Para el día del taller hay una
versión corta con dibujos y hoja de resultados: `docs/14-checklist-calibracion.md` (y su PDF).

Sensores que se calibran aquí:

| Sensor | Qué se calibra | ¿Hace falta? |
|---|---|---|
| pH SEN0169-V2 | Dos puntos con los tampones 7 y 4 | **Sí**, antes de dar por buenos los datos |
| Nivel KIT0139 + conversor SEN0262 | Cero con el bidón vacío y tabla de 5 en 5 L | **Sí** (el cero), la tabla es recomendable |
| Presencia de agua SEN0204 | Sensibilidad (botón SET) y sentido de la salida | Solo comprobar |
| Oxígeno y temperatura SEN0681 (RS485) | Salinidad a 0 y, si se puede, oxígeno al 100 % | Solo cuando tengamos el **módulo RS485** |

No hay ADS1115, ni aislador, ni medida de batería, ni caudalímetro: en el monitor serie `bat=0 mV` es normal y el
caudal no aparece.

## 0. Grabar el firmware real

El entorno real es **`lilygo_t3_simple`** (`firmware/nodo-agua/platformio.ini`). Usa estos pines, que coinciden con
la serigrafía de nuestra T3 V1.6.1 (`docs/12`, apartado 1.5):

| Señal | Pin en la serigrafía | GPIO |
|---|---|---|
| pH (placa SEN0169-V2, salida A) | S_VP | 36 |
| Nivel (SIG del conversor SEN0262) | S_VN | 39 |
| Presencia de agua (SEN0204, tras el divisor 27k/10k) | IO4 | 4 |
| Puente de calibración (a GND al arrancar) | IO15 | 15 |
| RS485 DI (TX de la LILYGO) | IO13 | 13 |
| RS485 RO (RX de la LILYGO) | IO14 | 14 |
| RS485 DE y RE | IO25 | 25 |

Radio LoRa (5, 18, 19, 23, 26, 27, 33), pantalla (21, 22), IO0, IO2 e IO12 no se tocan. IO34 e IO35 se quedan libres.

### 0.1. Pasos en el PC de Carlos (Windows, LILYGO en COM7)

1. **Copiar el firmware nuevo de `main`** a la carpeta del PC (la carpeta `TFG` del escritorio no es un clon de git):
   como mínimo `firmware/nodo-agua/include/config.h`, `firmware/nodo-agua/src/sensores.cpp` y
   `firmware/nodo-agua/herramientas/calibrar.py`.
2. **Comprobar `secrets.h`**: tiene que existir `firmware/nodo-agua/include/secrets.h` con las claves del nodo.
   Es el mismo que se usó para el firmware de simulación (mismo DevEUI y mismas claves), así que no hay que tocarlo.
   Si no está, se copia de la Raspberry, donde lo dejó el contenedor `provisionar`:
   ```
   scp charlie@rpi-lora:~/TFG/firmware/nodo-agua/include/secrets.h firmware\nodo-agua\include\
   ```
3. Antena puesta en la LILYGO y cable USB al PC.
4. En PowerShell, dentro de `firmware\nodo-agua`:
   ```
   pio run -e lilygo_t3_simple -t upload --upload-port COM7
   pio device monitor -p COM7 -b 115200
   ```
   Si `pio` no se encuentra, la ruta completa es
   `C:\Users\wwwca\AppData\Roaming\Python\Python314\Scripts\pio.exe`. Si sale `Failed to connect to ESP32`,
   mantener pulsado el botón BOOT (IO0) de la placa mientras empieza a grabar.
5. **Qué tiene que salir** en el monitor, sin puente de calibración:
   ```
   --- Nodo calidad agua, ciclo 1 ---
   Sesion restaurada            (o "Join OK (sesion nueva)")
   ```
   Y ya **no** sale `[SIMULADO]`. A los 60 s envía y en la web aparecen los datos reales. Mientras no esté el
   módulo RS485, la temperatura y el oxígeno salen sin dato (y el pH se compensa como si el agua estuviera a 25 °C).

Para volver a la simulación: `pio run -e lilygo_t3_simulado -t upload --upload-port COM7`.

### 0.2. Entrar en el modo calibración

1. Con todo apagado, poner el **puente de calibración**: dupont hembra-hembra entre **IO15** y **GND**.
2. Encender primero la LILYGO (USB) y después la fuente de 12 V.
3. Abrir el monitor serie (`pio device monitor -p COM7 -b 115200`) y pulsar **RST** en la placa.
4. Sale `=== MODO CALIBRACION ===`, la lista de comandos y `Esperando calentamiento de sensores (60 s)...`.
   La pantalla OLED pone `MODO CALIBRACION`. Después de esos 60 s ya se pueden escribir comandos (uno por línea,
   con Intro).

| Comando | Qué hace |
|---|---|
| `leer` | Una medida completa: `T=… O2=… pH=… nivel=… bat=… agua=… rs485_err=…` |
| `mv` | Tensiones crudas en los pines: pH en mV, nivel en mV y mA, y el pin de presencia de agua (0/1) |
| `ph7` / `ph4` | Guarda el punto del tampón 7 / 4 |
| `nivel0` | Guarda el cero del nivel (bidón vacío) |
| `sal` / `sal0` | Lee la salinidad del SEN0681 / la pone a 0 |
| `o2_100` / `o2_cero` | Calibración del oxígeno al 100 % / a cero (SEN0681) |
| `ver` | Enseña lo guardado: `ph7=… ph4=… nivel0=…` |
| `reset` | Vuelve a la calibración de fábrica (pH 1500/2032 mV y cero del nivel de `config.h`) |
| `salir` | Sale del menú. Luego se **quita el puente** y se pulsa RST |

Todo lo que se guarda con `ph7`, `ph4` y `nivel0` va a la memoria flash (NVS): **no se pierde al apagar ni al
volver a grabar el firmware**. Solo se borra con `reset` o borrando la flash entera (`pio run -t erase`).

## 1. Comprobación general (5 min)

Antes de calibrar nada, escribir `mv` y luego `leer`, y comparar con esto:

| Lectura | Valor normal | Si no sale así |
|---|---|---|
| pH, en `mv` | 1300-1700 mV con la sonda en agua del grifo | ~0 mV: cable A suelto o placa sin 3V3. ~3000 mV o fijo: sonda sin enroscar |
| nivel, en `mv` | ~480 mV (4 mA) con la sonda fuera del agua | <420 mV (`nivel=nan`): sonda sin 12 V, I+ e I− cambiados o falta el puente de GND |
| agua, en `mv` | `pin=1` con agua detrás de la pared del bidón, `pin=0` sin agua | ver apartado 4 |
| `rs485_err` | 1 sin módulo RS485 (normal); 0 con el módulo | ver apartado 5 |

## 2. pH (SEN0169-V2) con los tampones 7 y 4

Material: tampón **pH 7,00** y tampón **pH 4,00**, agua destilada (o del grifo) para enjuagar, papel para secar
y dos vasos limpios. Los tampones, a temperatura ambiente (unos 20-25 °C).

1. Quitar el capuchón de la sonda. Enjuagarla y secarla con cuidado, **sin frotar el bulbo de cristal**.
2. Meter la sonda en el **tampón 7**. Esperar a que se estabilice (1-2 min): escribir `mv` varias veces hasta que el
   valor del pH no cambie más de 1-2 mV. Debería rondar los **1500 mV**.
3. Escribir **`ph7`**. Sale `pH7 guardado: …mV`.
4. Enjuagar y secar la sonda. Meterla en el **tampón 4** y esperar igual.
   Debería rondar los **2000 mV** (más alto que en el 7).
5. Escribir **`ph4`**. Sale `pH4 guardado: …mV`.
6. **Comprobar**: volver a meterla en el tampón 7 y escribir `leer`: tiene que salir `pH=7.00 ± 0.10`. En el
   tampón 4, `pH=4.00 ± 0.10`. Si es así, la fase 2 queda cumplida para el pH.
7. `ver` enseña los dos valores guardados. Apuntarlos en la memoria con la fecha (sirven para ver cómo envejece la
   sonda: si la diferencia entre los dos baja mucho de unos 450 mV, la sonda está gastada).
8. Volver a poner el capuchón con su líquido o dejar la sonda dentro del bidón. **No dejarla secar.**

Notas:
- Si se calibra mal (por ejemplo, se escribe `ph4` con la sonda en el tampón 7), se repite el paso. Si salen
  valores raros, `reset` y empezar de nuevo.
- Mientras no esté el SEN0681, el firmware compensa la temperatura como si el agua estuviera a 25 °C. Con el
  agua a 15-30 °C el error que mete es de menos de 0,05 pH cerca de pH 7.
- Repetir la calibración **cada mes** o si los datos se van poco a poco.
- Si el pH baila mucho con todo montado, apagar la bomba un momento: sin aislador, la sonda comparte masa con el
  resto (`docs/12`, problemas típicos).

## 3. Nivel (KIT0139 + conversor SEN0262)

El firmware convierte la tensión del conversor en corriente (resistencia de 120 Ω) y la corriente en mm:
4 mA = 0 mm y 20 mA = 5000 mm (rango de 0-5 m del KIT0139). Lo único que hay que ajustar es el **cero**, porque el
4 mA real del sensor y la resistencia del conversor nunca son exactos.

### 3.1. Cero del nivel (obligatorio)

1. Bidón **vacío** y la sonda apoyada en el fondo, de pie, como va a quedar montada. El tubo de aire, sin doblar y
   con la punta seca.
2. Esperar 1 min y escribir `mv` varias veces: el nivel tiene que estar estable (unos 480 mV).
3. Escribir **`nivel0`**. Sale `Cero del nivel guardado: … mm` (lo normal es un número pequeño, entre -50 y 50).
4. Escribir `leer`: ahora tiene que salir `nivel=0 mm`.

Ya **no hace falta tocar `NIVEL_CERO_MM` en `config.h` ni volver a grabar**: el cero se guarda en la flash.
`NIVEL_CERO_MM` solo se usa si nunca se ha hecho `nivel0` (o después de un `reset`).

### 3.2. Tabla de 5 en 5 L (recomendable)

1. Con una garrafa de 5 L, echar agua de 5 en 5 L. Después de cada garrafa, esperar 30 s y escribir `leer`.
2. Apuntar en una tabla:

   | Litros | `nivel=` (mm) |
   |---|---|
   | 0 | 0 |
   | 5 | |
   | 10 | |
   | 15 | |
   | 20 | |
   | 25 | |

3. El valor con **25 L** se pone en `BIDON.alturaLlenoMm` de `raspberry/web/static/app.js` (ahora vale 400) y se
   despliega la web (`raspberry/README.md`, apartado 9). Así el % y los litros de la web cuadran con el bidón real.
4. Si los pasos no son parecidos entre sí (el bidón se estrecha arriba), se apunta en la memoria como limitación.
   El error del KIT0139 es de unos ±25 mm (±1,5 L) en este bidón (`docs/06`, apartado 1.4): no esperar más precisión.

## 4. Presencia de agua (SEN0204)

No tiene calibración numérica: solo dice si hay agua (1) o no (0) a la altura donde está pegado.

1. Con el bidón por debajo del sensor, `mv` tiene que dar `agua: pin=0`.
2. Llenar hasta que el agua pase el sensor (o poner la mano mojada detrás de la pared, en el mismo sitio):
   `pin=1`. Con el polímetro, en la columna 27 de la protoboard: unos 3,2 V con agua y 0 V sin agua.
3. **Si no cambia**: pulsar el botón **SET** de la placa adaptadora para cambiar la sensibilidad (4 niveles, el LED
   parpadea) y repetir. La pared del bidón no puede tener más de 13 mm (wiki DFRobot SEN0204).
4. **Si sale al revés** (1 sin agua y 0 con agua): cambiar `AGUA_ACTIVO_ALTO` a 0 al principio de
   `src/sensores.cpp` y volver a grabar.

## 5. Oxígeno y temperatura (SEN0681 por RS485)

**Solo cuando tengamos el módulo RS485 a TTL de 3,3 V** y esté conectado como en `docs/12`, paso 5.

### 5.1. Comprobar la comunicación

1. Escribir `leer`. Tiene que salir `rs485_err=0` y valores lógicos: `T=` la temperatura del agua (comparar con un
   termómetro: ±0,5 °C) y `O2=` entre 6 y 11 mg/L en agua del grifo que haya estado al aire.
2. Si sale `rs485_err=1`: intercambiar los cables de las columnas 6 y 7 (DI y RO); si sigue igual, intercambiar A y
   B en el módulo. Comprobar 3,3 V en el VCC del módulo y 12 V en el marrón del sensor. No se rompe nada.
3. Si sigue sin responder, puede que el sensor no esté a 4800 baudios o en la dirección 1 (valores de fábrica de la
   wiki del SEN0680). Se cambian en `MODBUS_BAUDIOS` y `MODBUS_DIRECCION` de `config.h`. **TODO VERIFICAR** con el
   sensor real.

### 5.2. Salinidad a 0 (agua de red)

El SEN0681 es la versión de **agua de mar** del sensor, así que puede venir con una salinidad distinta de 0 y daría
el oxígeno mal en agua dulce.

1. Escribir **`sal`**. Sale algo como `Salinidad: registros 0x0000 0x0000 (como entero: 0, como float: 0.000)`.
2. Si no es 0, escribir **`sal0`**. Sale `Salinidad a 0: OK` y vuelve a leerla: tiene que dar 0.
3. Apuntar en la memoria el valor que traía de fábrica (sirve para confirmar el formato del registro, que la wiki no
   da) y quitar el `TODO VERIFICAR` de `REG_SALINIDAD` en `config.h`.

El valor se guarda en el propio sensor: solo hay que hacerlo una vez.

### 5.3. Calibrar el oxígeno (opcional)

La wiki del SEN0680 (https://wiki.dfrobot.com/sen0680/docs/21672) recomienda calibrar antes de usarlo y luego cada
tres meses. Primero el 100 % y después el cero.

**Punto de 100 % (aire saturado de agua)**. Es el importante y no necesita productos:
1. Meter un poco de agua en una botella, cerrarla y agitarla fuerte 30 s.
2. Meter la sonda en la botella con la membrana a **1 cm por encima del agua** (sin tocarla), y tapar la boca
   alrededor del cable con film o un trapo.
3. Esperar a que `leer` dé el mismo `O2=` varias veces seguidas (unos minutos: el sensor tiene que coger la
   temperatura del aire de la botella).
4. Escribir **`o2_100`**. Tiene que salir `Calibracion O2 al 100 %: OK`.
5. Comprobar: en agua del grifo que haya estado unas horas al aire, el `O2=` tiene que parecerse a la tabla de
   saturación: unos **10,1 mg/L a 15 °C, 9,1 mg/L a 20 °C, 8,3 mg/L a 25 °C y 7,6 mg/L a 30 °C**.

**Punto de cero** (solo si conseguimos **sulfito sódico**):
1. Disolver 5 g de sulfito sódico anhidro en 95 g de agua y dejarlo reposar 1 hora (wiki del SEN0680).
2. Meter la sonda, remover un poco y esperar a que el `O2=` se quede quieto cerca de 0.
3. Escribir **`o2_cero`** → `Calibracion O2 a cero: OK`.
4. Enjuagar bien la sonda con agua antes de volver a meterla en el bidón.

Si no hay sulfito, se deja el cero de fábrica y se dice en la memoria.

## 6. Al terminar

1. `ver` y apuntar en la memoria (anexo de pruebas) los valores guardados y la fecha.
2. `salir`, **quitar el puente IO15-GND** y pulsar RST. El nodo hace el join (o restaura la sesión) y empieza a
   enviar cada 15 min.
3. En la web (`https://rpi-lora.tailc40e5c.ts.net`), comprobar que los valores coinciden con los del último `leer`.

## 7. Si lo hace Claude Code (sin escribir en el monitor serie)

Con la LILYGO conectada por USB al PC de Carlos (Remote Control o Claude Code en el PC), el monitor serie es
interactivo y no le sirve a Claude. Para eso está `firmware/nodo-agua/herramientas/calibrar.py`, que reinicia la
placa, espera el menú y los 60 s de calentamiento, manda los comandos y enseña la respuesta:

```
cd firmware\nodo-agua\herramientas
python calibrar.py COM7 mv leer                 # comprobación general (apartado 1)
python calibrar.py COM7 --sin-reset ph7         # sonda en el tampón 7 (la placa ya está en el menú)
python calibrar.py COM7 --sin-reset ph4         # sonda en el tampón 4
python calibrar.py COM7 --sin-reset nivel0 ver  # bidón vacío
python calibrar.py COM7 --sin-reset sal         # con el módulo RS485
```

Reglas para Claude:
- El puente IO15-GND, meter la sonda en cada tampón, vaciar o llenar el bidón y la botella del oxígeno los hace
  **una persona**. Claude pide cada paso, espera a que le confirmen y entonces manda el comando.
- Antes de `ph7`/`ph4`, mandar `mv` varias veces y no guardar hasta que el pH no cambie más de 2 mV.
- `sal0`, `o2_100` y `o2_cero` escriben en el propio sensor: preguntar antes de mandarlos.
- Si `monitor` o `calibrar.py` dicen que el puerto está ocupado, cerrar el otro programa que tenga abierto COM7.
- Al acabar, apuntar los valores en `docs/` y avisar de que hay que quitar el puente.

---
Fuentes: wikis de DFRobot (SEN0169-V2, KIT0139, SEN0262, SEN0204 y SEN0680 para el SEN0681),
`firmware/nodo-agua/include/config.h` y `src/sensores.cpp` (entorno `lilygo_t3_simple`). Tabla de saturación de
oxígeno en agua dulce a 1 atm (valores redondeados de las tablas de solubilidad del oxígeno, p. ej. USGS).
