# Guía de instalación completa

Esta guía lleva el proyecto desde la caja de material hasta ver los datos en el móvil. Va por orden:
cada paso termina con una **comprobación**, y no se pasa al siguiente hasta que se cumple. Así, si algo falla,
se sabe en qué tramo está el problema.

```
 1. Banco de pruebas del nodo (USB, en el aula)
 2. Placa base y cableado de sensores
 3. Calibración
 4. Servidor en la Raspberry Pi 5
 5. Gateway wAP LR8
 6. Alta del nodo en ChirpStack
 7. Primer envío de punta a punta   ◄── aquí se comprueba que todo llega bien
 8. Montaje exterior de la maqueta
 9. Pruebas finales (24 h y una semana)
```

Documentos relacionados: material en `01-lista-material.md` y `07-lista-compra.md`, red en `02-arquitectura-red.md`,
cableado en `03-conexionado-nodo.md`, mensaje LoRaWAN en `04-formato-payload.md`, maqueta en `06-maqueta.md`
y los comandos del servidor en `raspberry/README.md`.

---

## 0. Antes de empezar

**Herramientas**: soldador y estaño, multímetro, pelacables, destornilladores, pistola de silicona o
adhesivo, bridas, un PC con VS Code y cable USB de datos para la LILYGO.

**Software en el PC**:
- VS Code + extensión **PlatformIO IDE** (o `pip install platformio` y usar `pio` desde la terminal).
- `git` para bajar el repositorio: `git clone https://github.com/cmaaraver/TFG-2-STI-.git`
- Opcional para las pruebas sin hardware: `g++` y `node`.

**Comprobación rápida sin hardware** (que el formato del mensaje es coherente entre firmware, ChirpStack
y base de datos):
```
sh pruebas/payload/probar.sh
```
Tiene que terminar con `TODO OK (3 payloads, 10 campos del ingestor comprobados)`.

---

## 1. Banco de pruebas del nodo (solo la LILYGO por USB)

1. Conectar la **antena** a la LILYGO. *Nunca* encenderla sin antena: el chip de radio se puede estropear al emitir.
2. **Sin tarjeta microSD** en la placa (comparte pines con el RS485, ver `03-conexionado-nodo.md`).
3. Abrir `firmware/nodo-agua` en VS Code. PlatformIO descarga solo las librerías (versiones fijas en `platformio.ini`).
4. Crear las claves: copiar `include/secrets.example.h` a `include/secrets.h`. De momento se dejan los ceros;
   las claves de verdad se ponen en el paso 6. `secrets.h` **no se sube a git** (está en `.gitignore`).
5. Compilar y grabar:
   ```
   pio run -e lilygo_t3_v1_6_1                 # compilar
   pio run -e lilygo_t3_v1_6_1 -t upload       # grabar
   pio device monitor                          # ver el monitor serie (115200)
   ```

**Comprobación**:
- La compilación acaba en `[SUCCESS]`.
- La pantalla OLED enseña el **logo de Los Viveros** arriba y debajo la fase del ciclo con un contador de segundos:

  ![Pantallas del nodo](img/pantalla-oled.png)

- En el monitor serie sale `--- Nodo calidad agua, ciclo 1 ---`. Sin sensores y con claves a cero es normal que
  luego salga `Fallo de join` y la pantalla ponga *Join fallido / Reintento en 5 min*. Lo importante aquí es
  que la placa arranca, la pantalla funciona y la radio no da `Error de radio`.

> Qué enseña la pantalla en cada ciclo: la fase (*Bomba y sensores ON*, *Conectando LoRaWAN*, *Bombeando agua*,
> *Midiendo caudal*, *Agua en reposo*, *Leyendo sensores*) con los segundos desde que despertó; después
> *Enviando por LoRa...* con un **temporizador en directo** (se refresca cada 0,1 s desde una tarea aparte,
> así avanza aunque el envío tenga ocupado el programa principal); y al final el resultado:
> *Enviado OK SF7*, el tiempo total del envío en grande y debajo el tiempo en el aire y cuándo es el próximo.
> Ese resultado se ve 5 s y la pantalla se apaga para ahorrar (`PANTALLA_APAGAR_AL_DORMIR` en `config.h`;
> en el banco de pruebas se puede poner a 0 para que se quede encendida).

---

## 2. Placa base y cableado de sensores

Esquema completo en `03-conexionado-nodo.md`:

![Conexionado del nodo](img/conexionado-nodo.png)

Orden de montaje recomendado (siempre **sin la LILYGO puesta** hasta el último punto):

1. Soldar en la placa de topos: tiras hembra para la LILYGO, bornas, conmutadores de 12 V y 5 V, driver de la
   bomba (con la **pull-down de 100 kΩ en GPIO 12**, obligatoria), divisores de batería y caudalímetro y las pull-ups.
2. Conectar la alimentación de 12 V (de una fuente de laboratorio limitada a 1 A, todavía no la batería).
3. Medir con el multímetro:

   | Punto | Valor esperado |
   |---|---|
   | Salida del DC-DC | 5,0 V ± 0,1 |
   | Pin 5V de la LILYGO (zócalo vacío) | 5,0 V |
   | Salida de los conmutadores con EN a GND | 0 V (sensores apagados) |
   | Salida de los conmutadores con EN a 3,3 V (puente provisional) | 12 V y 5 V |
   | Divisor de batería con 12,8 V | ≈ 2,3 V |
   | Entrada GPIO 34 (caudalímetro) con la salida del caudalímetro a 5 V | ≈ 3,3 V, nunca más de 3,6 V |
   | GPIO 12 respecto a GND | 0 V (pull-down) |

4. Pinchar la LILYGO, conectar ADS1115, placa de pH (tras el aislador), convertidor 4-20 mA, adaptador RS485 y sensores.

**Comprobación**: el nodo arranca igual que en el paso 1 (si con la placa base no arranca o se reinicia en bucle,
lo primero es mirar que GPIO 12 esté a 0 V al encender).

---

## 3. Calibración (modo calibración por el monitor serie)

1. Poner el **puente MODO_CAL a GND** y reiniciar. La pantalla pone *MODO CALIBRACION*.
2. En el monitor serie sale `=== MODO CALIBRACION ===` y espera 60 s a que calienten los sensores.
3. Comandos (escribir y pulsar Intro):

   | Comando | Qué hace |
   |---|---|
   | `leer` | Mide todo una vez: `T=... C  O2=... mg/L  pH=...  nivel=... mm  bat=... mV  agua=...  rs485_err=...` |
   | `bomba` | Enciende la bomba unos 15 s (5 s de arranque + 10 s midiendo) y enseña el caudal en L/min |
   | `ph7` | Con la sonda en tampón pH 7,00: guarda ese punto en la memoria (NVS) |
   | `ph4` | Con la sonda en tampón pH 4,00 (tras enjuagarla con agua destilada): guarda el segundo punto |
   | `ver` | Enseña la calibración guardada |
   | `reset` | Vuelve a la calibración por defecto |
   | `salir` | Apaga todo; quitar el puente y reiniciar |

4. **SEN0681 (oxígeno)**: antes hay que rellenar los registros Modbus en `config.h` con los de la wiki oficial de
   DFRobot (están marcados `TODO VERIFICAR`) y poner `MODBUS_REGISTROS_OK 1`. Con agua de red, salinidad a 0 ‰.
5. **Caudalímetro**: `CAUDAL_HZ_POR_LMIN` en `config.h` según el modelo comprado (YF-S201: 7,5).
   Se comprueba llenando un recipiente de volumen conocido durante 1 minuto.

**Comprobación** (criterio de la fase 2): tras calibrar, `leer` con la sonda en tampón 7 da 7,00 ± 0,1 y en tampón 4
da 4,00 ± 0,1; `rs485_err=0`; la temperatura cuadra con un termómetro; `bat` cuadra con el multímetro (± 100 mV).

---

## 4. Servidor en la Raspberry Pi 5

Pasos detallados en `raspberry/README.md` (apartados 1 a 3). Resumen:

1. Raspberry Pi OS Lite 64 bits en el NVMe, SSH con clave, `apt full-upgrade`, Docker.
2. Red **con teclado y monitor conectados** (para no quedarse fuera):
   `IF_LORA=eth0 IF_INSTITUTO=eth1 ./red/configurar-red.sh` y copiar `red/chrony.conf`.
3. `cp .env.example .env`, cambiar **todas** las contraseñas y poner el subdominio y el token de DuckDNS.
4. `docker compose up -d --build`

**Comprobación**:
- `docker compose ps` → todos los servicios `running` y los que tienen healthcheck `healthy`.
- `curl http://localhost/api/salud` → `{"estado":"ok"}`.
- Desde un PC del aula, `http://<ip-de-la-raspberry>` → se abre la web (sin datos todavía).
- Simular un uplink con el comando de `raspberry/README.md` ("Probar la web sin el nodo") → la tarjeta de la web
  cambia **sin recargar la página**. Después borrar los datos de prueba.

---

## 5. Gateway MikroTik wAP LR8

Configuración en `raspberry/README.md` (apartado 4): IP 192.168.50.2, NTP y servidor LoRa hacia 192.168.50.1:1700.
Conectarlo con su inyector PoE al puerto eth0 de la Raspberry.

**Comprobación**: `ping 192.168.50.2` desde la Raspberry, y `docker compose logs gateway-bridge` enseña
mensajes del gateway (estadísticas cada 30 s aprox.).

---

## 6. Alta del nodo en ChirpStack

1. Entrar a ChirpStack (por Tailscale o túnel SSH, `raspberry/README.md` apartado 5) y cambiar la contraseña de `admin`.
2. **Gateway**: con el EUI del wAP → al rato sale *online*.
3. **Perfil de dispositivo**: región EU868, MAC LoRaWAN 1.1.0, revisión RP002-1.0.3 o la que ofrezca, OTAA,
   clase A. En *Codec*: JavaScript, pegar entero `raspberry/codec/decoder.js`.
4. **Aplicación** `calidad-agua` → **Dispositivo**: DevEUI inventado o el de la placa (16 cifras hex) y JoinEUI
   todo ceros. En *OTAA keys* generar la Application key y la Network key.
5. Copiar los datos a `firmware/nodo-agua/include/secrets.h` **tal cual se leen en ChirpStack** (MSB primero):

   ```cpp
   #define LW_JOIN_EUI 0x0000000000000000ULL
   #define LW_DEV_EUI  0x70B3D57ED0012345ULL          // DevEUI de ChirpStack con 0x delante
   #define LW_APP_KEY { 0x2B,0x7E,0x15,0x16, ... }       // Application key, de 2 en 2 cifras
   #define LW_NWK_KEY { 0x8A,0x3C,0x01,0xF4, ... }       // Network key
   ```
   (Los valores de arriba son un ejemplo; hay que poner los del dispositivo creado.)
6. Volver a grabar el firmware.

---

## 7. Primer envío de punta a punta: comprobar que todo llega bien

Con el nodo encendido y los sensores conectados, se sigue el mensaje por todos los tramos. Si un tramo falla,
el problema está entre ese tramo y el anterior.

| # | Dónde mirar | Qué tiene que salir |
|---|---|---|
| 1 | Pantalla OLED | *Conectando LoRaWAN* → *Bombeando agua* → ... → *Enviando por LoRa...* con el temporizador corriendo → *Enviado OK SF7* |
| 2 | Monitor serie | `Join OK (sesion nueva)` (primera vez) o `Sesion restaurada`, la línea `T=... O2=... pH=...` y `Uplink enviado: fcnt=N SFx, X ms en el aire, Y ms en total` |
| 3 | ChirpStack → gateway → *LoRaWAN frames* | Un `JoinRequest`/`JoinAccept` la primera vez y luego un `UnconfirmedDataUp` por ciclo |
| 4 | ChirpStack → dispositivo → *Events* | Evento `up` con el objeto decodificado: `temperatura_c`, `oxigeno_mgl`, `ph`, `nivel_mm`, `bateria_v`, `caudal_lmin`... y `conductividad_uscm: null` (ya no se mide, es normal) |
| 5 | `docker compose logs -f ingestor` | `Guardado <deveui> fcnt=N` |
| 6 | Base de datos | `docker compose exec db psql -U agua_admin -d calidad_agua -c "SELECT tiempo, ph, oxigeno_mgl, rssi_dbm FROM medidas ORDER BY tiempo DESC LIMIT 3;"` → la fila nueva, con la hora en UTC |
| 7 | Web | La tarjeta se actualiza sola al momento, la hora sale en hora de Madrid y el punto aparece en las gráficas |
| 8 | Siguiente ciclo (15 min) | `fcnt` sube de uno en uno; si salta números, se han perdido mensajes (mirar RSSI/SNR) |

Para dejarlo documentado: captura de cada tramo (pantalla, monitor serie, ChirpStack, logs, web).

**Prueba de la cola persistente** (fase 4): parar el ingestor, esperar 2 envíos y arrancarlo; tienen que entrar
los 2 mensajes (`raspberry/README.md`, "Prueba de robustez").

---

## 8. Montaje exterior de la maqueta

Diseño y balance de energía en `06-maqueta.md`; colocación de cada sonda en `03-conexionado-nodo.md` (apartado 7):

![Instalación de las sondas](img/instalacion-sensores.png)

1. **Depósito**: opaco, tapado, a la sombra y sobre una base firme y nivelada. Llenar con agua de red.
2. **Circuito de agua**: bomba con rejilla en el fondo → manguera → caudalímetro (horizontal, flecha en el
   sentido del agua) → válvula de bola → retorno al mismo depósito por debajo del nivel del agua y lejos de las sondas.
   Abrazaderas en todas las espigas. Probar fugas con la bomba a mano (comando `bomba` del modo calibración).
3. **Sondas**: pH y SEN0681 colgadas del soporte de la tapa a media altura; KIT0139 en el fondo; SEN0204 por fuera
   de la pared a la altura del nivel mínimo. La punta del pH siempre mojada.
4. **Caja 1** (nodo) en el poste, con los prensaestopas y conectores **hacia abajo**, membrana de ventilación y gel
   de sílice. La antena vertical, por encima de la caja.
5. **Energía**, en este orden (el habitual en reguladores MPPT; confirmar en el manual del modelo comprado):
   1. Fusible de la batería **quitado**.
   2. Cablear batería → MPPT, poner el fusible: el MPPT arranca y reconoce la batería (configurarlo para LiFePO4).
   3. Conectar el panel al MPPT (conectores MC4).
   4. Conectar la salida de CARGA (con su fusible de 3 A) a la caja 1.
   Para desmontar, al revés: carga, panel y por último batería.
6. **Gateway**: el wAP en la fachada o en una ventana con visión directa a la maqueta.

**Comprobación**: se repite la tabla del paso 7 con el nodo ya en su sitio y alimentado solo por el sol.
En ChirpStack mirar RSSI y SNR de los uplinks: con SNR positiva y RSSI mejor que −110 dBm hay margen de sobra.

---

## 9. Pruebas finales

| Prueba | Cómo | Se cumple si |
|---|---|---|
| 24 h de datos (fase 4) | Dejarlo funcionando un día | La web enseña 24 h de gráficas sin huecos y con la hora correcta |
| Acceso remoto (fase 5) | Móvil con datos móviles → `https://<nombre>.duckdns.org` | Carga con candado (HTTPS) y datos al momento |
| Autonomía (fase 6) | Una semana a la intemperie | Batería estable o subiendo en la gráfica y menos del 2-3 % de mensajes perdidos (`fcnt`) |
| Copia de seguridad | `raspberry/backup.sh` en cron y una restauración de prueba | La restauración recupera las medidas |

---

## 10. Problemas típicos

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El ESP32 no arranca o se reinicia en bucle con la placa base puesta | GPIO 12 a nivel alto al encender | Revisar la pull-down de 100 kΩ del driver de la bomba |
| Pantalla negra | `PANTALLA_ACTIVA 0`, o el bus I2C tiene un corto | `config.h`; quitar el ADS1115 y probar solo la placa |
| `Error de radio` | Placa mal elegida en `platformio.ini` / `config.h` | Confirmar modelo exacto de la LILYGO |
| `Fallo de join` siempre | Claves mal copiadas, perfil no 1.1.0, gateway offline o fuera de alcance | Revisar `secrets.h` (orden MSB), perfil y que el gateway esté *online* |
| Join rechazado tras borrar la flash de la placa | Los DevNonce empiezan otra vez y ChirpStack ya los había visto | Borrar el dispositivo en ChirpStack y crearlo otra vez (mismas claves) |
| Uplinks en ChirpStack pero sin objeto decodificado | Codec no puesto en el perfil | Pegar `decoder.js` en el perfil |
| En ChirpStack sí, en la web no | Ingestor parado o sin acceso a la BD | `docker compose logs ingestor` |
| `rs485_err=1` | A/B cruzados, sin 12 V en el SEN0681 o registros sin rellenar | Cambiar A por B, medir 12 V, revisar `MODBUS_REGISTROS_OK` |
| Aviso "bomba sin caudal" | Bomba atascada, rejilla sucia, válvula cerrada o depósito bajo | Revisar el circuito de agua |
| pH que baila mucho | Masas mezcladas o sonda seca | Comprobar el aislador y que la sonda esté sumergida |
