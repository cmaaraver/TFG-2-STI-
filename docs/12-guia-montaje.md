# Guía de montaje paso a paso (montaje simple en protoboard)

Esta guía explica cómo cablear el nodo **cable a cable** sobre la protoboard pegada dentro de la caja estanca,
con los colores reales de cada sensor y los pines de la LILYGO. Es el montaje que usamos de verdad (`docs/03`,
apartado 0): todo se lee directamente con la LILYGO, sin ADS1115 ni aislador, y el firmware es el entorno
**`lilygo_t3_simple`**.

![Esquema de montaje en la protoboard](img/montaje-visual.png)

(Editable: `img/montaje-visual.svg`. Se vuelve a generar con `python3 img/montaje-visual.py img/montaje-visual.svg`.)

## 1. Antes de empezar

### 1.1. Qué es cada cosa

| Pieza | Qué es | Cables |
|---|---|---|
| LILYGO T3 V1.6.1 | El nodo (ESP32 + radio LoRa + pantalla) | Se conecta a la protoboard con cables dupont |
| SEN0681 | Sonda de oxígeno y temperatura (RS485) | marrón +12 V, negro GND, amarillo A, azul B |
| Módulo RS485 a TTL de 3,3 V | Traduce el RS485 del SEN0681 a la LILYGO | **Por conseguir** (MAX3485 o parecido) |
| KIT0139 | Sonda de nivel (4-20 mA) | rojo fino +12 V, negro salida, rojo grueso = **tubo de aire** |
| **Conversor 4-20 mA → V (SEN0262)** | **La placa azul pequeña que viene en la misma caja del KIT0139** (sale en su lista de contenido). Tiene dos bornas de tornillo **I+** e **I−** y un conector de 3 pines **GND / VCC / SIG** | Convierte la corriente de la sonda en 0,48-2,4 V |
| SEN0169-V2 | Sonda de pH con conector BNC + su placa (conector de 3 pines **− / + / A**) | |
| SEN0204 | Sensor de presencia de agua (Y25, se pega por fuera) + **su placa adaptadora** | El sensor saca 4 hilos (marrón, amarillo, azul, negro) que van a la placa; de la placa sale un cable de 3 hilos **rojo, negro y verde** |
| Fuente de PC adaptada | 12 V, al menos 1 A | amarillo +12 V, negro GND |
| Cargador USB de 5 V con batería de respaldo | Alimenta la LILYGO | cable USB de datos |
| Protoboard | Pegada en la caja estanca | ver 1.3 |

Material pequeño (comprobar que lo hay en el aula): resistencias de **27 kΩ y 10 kΩ**, cables dupont
**macho-hembra** y **macho-macho**, un poco de estaño y soldador (para estañar puntas) y un polímetro.

### 1.2. Por qué el SEN0204 necesita dos resistencias

El sensor admite de 5 a 24 V y en su salida da **la misma tensión con la que se alimenta** (wiki DFRobot
SEN0204: salida en alto = VCC). Lo alimentamos a 12 V porque la LILYGO no tiene una salida de 5 V fiable
(por USB su pin 5V da ~4,7 V), y el ESP32 solo aguanta 3,3 V en un pin. Por eso la salida verde pasa por un
divisor: 12 V × 10 / (27 + 10) ≈ **3,2 V**.

La placa adaptadora solo sirve para pasar de 4 hilos a 3 y para el botón **SET** de sensibilidad (versión V1.0).
La wiki no dice qué tensión aguanta la placa, solo la del sensor (5-24 V). Por eso en el paso 4 se mide antes de
conectar nada a la LILYGO. **TODO VERIFICAR** con la placa real: si se calienta o la salida no cambia, se quita la
placa y se usan los 4 hilos del sensor directamente (marrón = rojo, azul = negro, amarillo = verde y el negro del
sensor suelto con cinta). Va en las mismas columnas.

### 1.3. Cómo es la protoboard

```
  + ───────────────────────────  ← línea roja de arriba: +12 V
  − ───────────────────────────  ← línea azul de arriba: GND
     1  2  3  4 ...         30
  a  ●  ●  ●  ●              ●   ┐
  b  ●  ●  ●  ●              ●   │ cada COLUMNA de 5 agujeros (a-e)
  c  ●  ●  ●  ●              ●   │ está unida por dentro
  d  ●  ●  ●  ●              ●   │
  e  ●  ●  ●  ●              ●   ┘
  ═══════════ canal central ═══════════
  f-j  (mitad de abajo: no se usa)
  − ───────────────────────────  ← línea azul de abajo: GND
  + ───────────────────────────  ← línea roja de abajo: 3V3 (¡no confundir con la de arriba!)
```

- Las columnas que salen en el esquema son las de la mitad de arriba (filas a-e). Con 30 columnas basta, así que
  vale igual una protoboard pequeña (400 puntos) que una grande (830 puntos).
- **Ojo**: en algunas protoboards grandes las líneas de alimentación están cortadas por la mitad. Con el polímetro
  en continuidad, comprobad que el primer y el último agujero de cada línea pitan. Si no, unid las dos mitades con
  un cable.
- Poned un trozo de cinta en la línea **+ de abajo** que diga "3V3" y otro en la **+ de arriba** que diga "12 V".
  Meter un cable de 3V3 en la línea de 12 V quema la placa del pH, el conversor o la LILYGO.
- Los cables de los sensores son de hilos sueltos y no agarran en la protoboard: **estañad la punta** (unos 6 mm)
  o crimpad un pin macho. Si un cable de 3 hilos acaba en un conector hembra, pinchad un cable macho-macho en cada
  hembra.

### 1.4. Reglas de seguridad

1. **Todo desenchufado** mientras se pinchan cables. La LILYGO, aparte hasta el paso 8.
2. **Nada de 230 V dentro de la caja**: la fuente de 12 V y el cargador USB se enchufan fuera, en la regleta de
   230 V del inversor.
3. La LILYGO se alimenta **solo por USB**. El pin 5V no se usa, no se pone tarjeta microSD, y GPIO12 y GPIO34 se
   quedan sin conectar.
4. **Nunca encender la LILYGO sin la antena puesta.**
5. Ningún cable que vaya a un GPIO puede tener más de 3,3 V. La columna 23 lleva 12 V cuando hay agua: **nunca**
   va directa a un pin.
6. La sonda de pH siempre con su capuchón con líquido o en agua: si se seca, se estropea.

## 2. Tabla de conexiones

| Dónde en la protoboard | Qué se pincha |
|---|---|
| **+ de arriba (12 V)** | Fuente **amarillo** · SEN0681 **marrón** · KIT0139 **rojo fino** · SEN0204 (placa) **rojo** |
| **− de arriba (GND)** | Fuente **negro** · SEN0681 **negro** · RS485 **GND** · conversor **I−** y **GND** · placa pH **−** · SEN0204 (placa) **negro** · pata de la **10 kΩ** · puente a la − de abajo |
| **− de abajo (GND)** | Puente desde la − de arriba · dupont a **GND** de la LILYGO |
| **+ de abajo (3V3)** | Dupont a **3V3** de la LILYGO · RS485 **VCC** · conversor **VCC** · placa pH **+** |
| Columna 6 | RS485 **DI** → dupont a **GPIO13** |
| Columna 7 | RS485 **RO** → dupont a **GPIO14** |
| Columna 8 | RS485 **DE** y **RE** (unidos en el módulo) → dupont a **GPIO25** |
| Columna 11 | KIT0139 **negro** + conversor **I+** (no va a la LILYGO) |
| Columna 15 | Conversor **SIG** → dupont a **GPIO39** |
| Columna 19 | Placa pH **A** → dupont a **GPIO36** |
| Columna 23 | SEN0204 (placa) **verde** + pata de la **27 kΩ** |
| Columna 27 | Otra pata de la **27 kΩ** + pata de la **10 kΩ** (la otra a la − de arriba) → dupont a **GPIO4** |
| Fuera de la protoboard | SEN0681 **amarillo → A** y **azul → B** del módulo RS485 · dupont hembra-hembra **GPIO15 ↔ GND** solo para calibrar |

Los números de columna son los del esquema. Si vuestra protoboard está numerada distinto, no pasa nada: lo que
importa es que cada grupo vaya en su propia columna y que no se toquen dos columnas distintas.

## 3. Pasos

### Paso 1. Alimentación de la protoboard

1. Marcar con cinta: **+ de arriba = 12 V** y **+ de abajo = 3V3**.
2. Puente negro de la **− de arriba** a la **− de abajo** (por el lado izquierdo). Así la masa de la fuente y la de
   la LILYGO son la misma: sin este puente no se lee ningún sensor.
3. Fuente de PC: si es ATX y no está adaptada, unir el **verde** (PS_ON) con un **negro** para que arranque.
4. Fuente: **amarillo → + de arriba** y **negro → − de arriba**.
5. **Prueba 1:** enchufar la fuente y medir entre la + y la − de arriba: **12-13 V**. Entre la + y la − de abajo:
   **0 V** (todavía no hay 3V3). Desenchufar.

### Paso 2. Presencia de agua (SEN0204 con su placa)

1. Pegar el sensor **por fuera** del bidón, en la pared lisa, a unos 12 cm del fondo (`docs/06`, apartado 1.2).
2. Enchufar sus 4 hilos a la placa adaptadora (como viene de fábrica).
3. Cable de 3 hilos de la placa: **rojo → + de arriba**, **negro → − de arriba**, **verde → columna 23**.
4. Resistencia de **27 kΩ** (rojo, violeta, naranja) entre la **columna 23** y la **columna 27**.
5. Resistencia de **10 kΩ** (marrón, negro, naranja) entre la **columna 27** y la **− de arriba**.
6. **Prueba 2:** enchufar la fuente.
   - Columna 23 contra GND: unos **12 V** con agua delante del sensor y **0 V** sin agua.
   - Columna 27 contra GND: unos **3,2 V** con agua y **0 V** sin agua. **Nunca más de 3,3 V.**
   - Tocar la placa adaptadora: no se tiene que calentar.

   Si la salida no cambia con el agua, pulsar **SET** en la placa para cambiar la sensibilidad (4 niveles, el
   LED parpadea). Si sigue igual o algo se calienta, hacerlo con los 4 hilos directos (apartado 1.2). Desenchufar.

### Paso 3. Nivel (KIT0139 + conversor SEN0262)

1. Sonda: **rojo fino → + de arriba** (12 V) y **negro → columna 11**.
2. El **rojo grueso es el tubo de aire**: no se conecta, no se corta, no se dobla, y su punta queda al aire y seca
   dentro de la caja. Sin él, el nivel sale mal.
3. Conversor, bornas de tornillo: **I+ → columna 11** (la misma del negro de la sonda) e **I− → − de arriba**.
   Para meterlos en la protoboard, un trozo de cable rígido en cada borna.
4. Conversor, conector de 3 pines: **GND → − de arriba**, **VCC → + de abajo (3V3)**, **SIG → columna 15**.
   Fiaos de la serigrafía de la placa (GND / VCC / SIG) más que del color del cable.

Nota: la sonda pide 12-36 V y la fuente da justo 12 V. Con el bidón de 25 L la corriente es pequeña (unos 5 mA), así
que la resistencia de 120 Ω del conversor solo se come unos 0,6 V. Si el nivel sale raro, es de lo primero que hay
que mirar.

### Paso 4. pH (SEN0169-V2)

1. Enroscar el BNC de la sonda en la placa del pH.
2. Conector de 3 pines de la placa: **− → − de arriba**, **+ → + de abajo (3V3)**, **A → columna 19**.

### Paso 5. Oxígeno (SEN0681) y módulo RS485

Solo cuando tengamos el módulo RS485. Hasta entonces, las columnas 6, 7 y 8 se quedan libres y el SEN0681 sin
conectar.

1. SEN0681: **marrón → + de arriba** (12 V) y **negro → − de arriba**.
2. SEN0681 al módulo: **amarillo → A** y **azul → B** (bornas de tornillo del módulo).
3. Módulo: **VCC → + de abajo (3V3)**, **GND → − de arriba**, **DI → columna 6**, **RO → columna 7**.
4. En el módulo, unir **DE con RE** con un cablecito y llevarlo a la **columna 8**.

Si el módulo es de **dirección automática** (solo tiene TXD y RXD, sin DE ni RE), la columna 8 y el GPIO25 sobran.

### Paso 6. Cables a la LILYGO (sin pincharlos todavía)

Cables dupont **macho-hembra**: el macho a la protoboard y la hembra al pin de la LILYGO.

| Desde | Color | Pin de la LILYGO |
|---|---|---|
| + de abajo (3V3) | naranja | 3V3 |
| − de abajo (GND) | negro | GND |
| Columna 6 | morado | GPIO13 |
| Columna 7 | gris | GPIO14 |
| Columna 8 | blanco | GPIO25 |
| Columna 15 | verde | GPIO39 |
| Columna 19 | azul | GPIO36 |
| Columna 27 | amarillo | GPIO4 |

Cada pin se busca por su nombre en la serigrafía de la placa (y si hay duda, en el pinout oficial de LilyGO de la
T3 V1.6.1). Etiquetad la hembra de cada cable con un trozo de cinta.

### Paso 7. Comprobaciones antes de pinchar la LILYGO

1. Todo desenchufado, polímetro en continuidad: **no** tiene que pitar entre la + y la − de arriba, ni entre la +
   y la − de abajo, ni entre la + de arriba y la + de abajo.
2. Enchufar la fuente y medir cada hembra de los dupont contra GND. Ninguna puede pasar de 3,3 V. Lo normal es 0 V
   en todas menos la amarilla (GPIO4), que marca unos 3,2 V si hay agua delante del SEN0204. Desenchufar.

### Paso 8. Primer encendido

1. Poner la **antena** en la LILYGO.
2. Pinchar los 8 dupont en sus pines.
3. Encender en este orden: **primero la LILYGO** (USB del cargador) y **después la fuente de 12 V**. Para apagar, al
   revés: primero la fuente y luego la LILYGO. Así nunca llega tensión a un pin con el ESP32 apagado.
4. La pantalla tiene que enseñar el logo de Los Viveros y el temporizador del envío.

### Paso 9. Grabar el firmware y comprobar las lecturas

1. Grabar el entorno simple desde el PC (carpeta `firmware/nodo-agua`):
   ```
   pio run -e lilygo_t3_simple -t upload
   pio device monitor -b 115200
   ```
2. Poner el **puente de calibración** (dupont hembra-hembra entre GPIO15 y GND) y pulsar reset. En el monitor sale
   `=== MODO CALIBRACION ===` y espera 60 s a que calienten los sensores.
3. Escribir `leer`. Sale una línea así (ejemplo con todo montado):
   ```
   T=21.50 C  O2=8.90 mg/L  pH=7.20  nivel=180 mm  bat=0 mV  agua=1  rs485_err=0
   ```
   - `pH`: en agua del grifo, entre 6,5 y 8,5 (antes de calibrar puede salir algo desviado).
   - `nivel`: sonda fuera del agua, cerca de 0 mm; dentro del bidón, la altura del agua sobre la sonda.
   - `agua`: 1 con agua delante del SEN0204 y 0 sin agua. Si sale al revés, se cambia `AGUA_ACTIVO_ALTO` a 0 en
     `src/sensores.cpp`.
   - `rs485_err=1` mientras no esté el módulo RS485 (normal). Con el módulo puesto tiene que salir 0; si no,
     cambiar entre sí los cables de las columnas 6 y 7, y si sigue igual, A y B. No se rompe nada.
   - `bat=0 mV` es normal: en este montaje no se mide la batería.
4. Calibrar el pH: sonda en tampón 7 → `ph7`; enjuagar, sonda en tampón 4 → `ph4`. `ver` enseña lo guardado.
5. Cero del nivel: con el bidón vacío y la sonda en el fondo, apuntar `nivel=` y ponerlo en `NIVEL_CERO_MM` de
   `config.h` (`docs/06`, apartado 1.4).
6. `salir`, **quitar el puente de calibración** y pulsar reset. El nodo hace el join y empieza a enviar; los datos
   salen en la web a los pocos segundos de cada envío.

### Paso 10. Cerrar la caja

1. Sondas en el bidón de una en una por la boca, con los cables por los agujeros del tapón (`docs/06`,
   apartados 1.2 y 1.3). El KIT0139 apoyado en el fondo; el pH y el SEN0681 a 8-10 cm del fondo.
2. Dentro de la caja estanca: protoboard, LILYGO, conversor, placa del pH, placa del SEN0204 y módulo RS485.
   Fuera: la fuente y el cargador, enchufados a la regleta de 230 V del inversor.
3. Sujetar con bridas o cinta los cables que entran a la caja, para que un tirón no saque nada de la protoboard.
   La LILYGO, pegada con cinta de doble cara o una brida para que no cuelgue de los dupont.
4. La antena, vertical y fuera de la caja si se puede (nunca dentro de una caja metálica).
5. La protoboard no aguanta bien la humedad ni las vibraciones: la caja bien cerrada y, cuando todo funcione, se
   puede pasar el mismo esquema a una placa de topos soldada.

## 4. Problemas típicos

| Qué pasa | Qué mirar |
|---|---|
| No hay 12 V en la + de arriba | La fuente no arranca: puente verde-negro (si es ATX) o el interruptor |
| No hay 3V3 en la + de abajo | La LILYGO apagada o el dupont naranja suelto |
| `agua` siempre 0 | Verde en la columna 23, resistencias bien pinchadas, sensibilidad con el botón SET |
| `agua` siempre 1 | La 10 kΩ no llega a la −, o el sensor detecta la mano u otra cosa cerca |
| `nivel` raro o negativo | Tubo de aire doblado o mojado; I+ e I− cambiados; falta el puente de GND |
| `pH` que baila | Probar a desenchufar la bomba: sin aislador, el pH comparte masa con las otras sondas (`docs/03`) |
| `rs485_err=1` con el módulo puesto | Cambiar 6 y 7, después A y B; comprobar 3V3 en el VCC del módulo |
| Una lectura va y viene | Un cable flojo en la protoboard: estañar la punta o cambiar de agujero |
| La LILYGO se reinicia | Cargador USB flojo o cable USB malo |

---
Fuentes: wikis de DFRobot (SEN0681, SEN0204, KIT0139, SEN0262, SEN0169-V2), esquema oficial `T3_V1.6.1.pdf` de
LilyGO y `firmware/nodo-agua/include/config.h` (entorno `lilygo_t3_simple`).
