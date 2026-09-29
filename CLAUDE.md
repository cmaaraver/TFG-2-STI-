# CLAUDE.md — TFG Monitorización de calidad del agua (LoRaWAN)

Este fichero lo lee Claude Code al abrir el repositorio. Es el plan maestro del proyecto.
Léelo entero antes de hacer nada y consulta la carpeta `docs/` para los detalles.

## 1. Contexto

- TFG de 2º de Grado Superior STI (Sistemas de Telecomunicaciones e Informáticos), CPIFP Los Viveros (Sevilla).
- Equipo: Carlos Maraver Román (responsable técnico) y Rubén Trillo García.
- Objetivo: maqueta exterior (depósito + bomba de recirculación + sensores) alimentada con energía solar,
  que mide la calidad del agua (oxígeno disuelto, pH, temperatura, nivel y caudal),
  envía la telemetría por LoRaWAN al gateway situado en el edificio, la guarda con fecha y hora en
  una base de datos y la muestra en un panel accesible desde fuera del instituto.
- Referencia: proyecto de innovación colaborativo "Sistema de telemetría para la monitorización de la
  calidad del agua" (cartel del centro). Nuestra versión sustituye WiFi por LoRaWAN privado y añade
  oxígeno y control remoto de la bomba. **No se mide conductividad** (decisión de 2026-09-29).
- Las sondas van **colgadas directamente dentro del depósito** (no hay cámara de medida aparte);
  en la tubería solo va el caudalímetro y, si acaso, el sensor de presencia de agua.
- Todo lo de la maqueta (LILYGO, sensores y bomba) es **autónomo**: panel solar + batería LiFePO4,
  sin cables de 230 V ni de red.

## 2. Arquitectura (resumen)

```
 [Sondas] → [LILYGO ESP32 LoRa] ~~~ LoRaWAN EU868 ~~~ [MikroTik wAP LR8]
                 (nodo solar)                               │ PoE, 192.168.50.2
                                                            ▼
                                  eth0 192.168.50.1 ┌─────────────────┐
                                                    │ Raspberry Pi 5  │ todo el servidor en Docker
                                  eth1 (USB, DHCP)  └────────┬────────┘
                                                             ▼
                                   red del instituto 192.168.155.x → Internet
                                   https://<nombre>.duckdns.org (web pública)
```

| Equipo | Función | Software |
|---|---|---|
| LILYGO (nodo, maqueta exterior) | Remueve el agua del depósito con la bomba, mide caudal y sensores, envía cada 15 min, duerme | Firmware PlatformIO + RadioLib (LoRaWAN 1.1, OTAA) |
| DFR1120-868 (maqueta, fase 7) | Relé controlado por downlink (llenado, alarma o anulación de la bomba) | Configuración propia de DFRobot |
| wAP LR8 | Gateway LoRaWAN, reenvía por UDP 1700 | RouterOS (packet forwarder nativo) |
| Raspberry Pi 5 | **Todo el servidor**: router/NAT/firewall, NTP, servidor LoRaWAN, MQTT, base de datos, web con HTTPS y DuckDNS | Raspberry Pi OS Lite 64 bits, NetworkManager, chrony, ufw, Tailscale, Docker (`raspberry/docker-compose.yml`): ChirpStack v4 + Gateway Bridge + Redis + Mosquitto + TimescaleDB + ingestor + web + Caddy + DuckDNS |

Ya **no hay PC de datos ni Grafana** (decisión de 2026-09-29): la base de datos y una web propia
van en la Raspberry.

Flujo de datos: nodo → wAP → ChirpStack (decodifica con `raspberry/codec/decoder.js`) → MQTT (QoS 1)
→ ingestor → TimescaleDB → web (tiempo real por NOTIFY + SSE, gráficas del histórico con ECharts)
→ Caddy (HTTPS) → `https://<nombre>.duckdns.org`.

Detalle completo en `docs/02-arquitectura-red.md`.

## 3. Reglas para Claude Code

1. **Idioma**: código comentado en español, nombres de variables en español sencillo. Documentación en español.
2. **No inventar datos de hardware.** Registros Modbus del SEN0681, pines de la LILYGO, fórmulas de sondas,
   parámetros de ChirpStack o RouterOS: si no están confirmados en este repo, se consultan en la
   documentación oficial (wiki DFRobot, pinout LILYGO, docs ChirpStack/MikroTik) y se cita la fuente
   en un comentario. Si no se puede confirmar, se deja un `TODO VERIFICAR` y se avisa.
3. **Secretos fuera de git**: claves LoRaWAN, contraseñas de la BD y de ChirpStack y el token de DuckDNS en `secrets.h` / `raspberry/.env`
   (existen plantillas `*.example`). Añadir al `.gitignore`.
4. **Hora siempre en UTC** en la base de datos (`timestamptz`). La web muestra Europe/Madrid.
5. **Todo en Docker Compose** (`raspberry/docker-compose.yml`) con `restart: unless-stopped`, volúmenes con nombre y healthchecks.
6. **Cambios pequeños y probados**: después de cada tarea, explicar cómo probarla y qué salida se espera.
7. **Documentación**: cada fase deja escrito en `docs/` qué se hizo, comandos usados, capturas pendientes
   y problemas encontrados, en tono natural de alumno de grado superior (claro, sin florituras).
   No mencionar el trabajo externo de ningún miembro del equipo.
8. Antes de tocar la red de la Raspberry por SSH, dejar siempre una vía de acceso alternativa
   (teclado/monitor o el otro interfaz) para no quedarse fuera.

## 4. Estructura del repositorio

```
CLAUDE.md                     ← este plan
docs/
  01-lista-material.md        ← material disponible y lista de compra
  02-arquitectura-red.md      ← IPs, NAT, NTP, acceso remoto, seguridad
  03-conexionado-nodo.md      ← cómo cablear y montar la LILYGO y los sensores
  04-formato-payload.md       ← formato binario del mensaje LoRaWAN (v2, con caudal)
  05-indice-memoria.md        ← índice provisional de la memoria
  06-maqueta.md               ← maqueta exterior, ciclo de bombeo y balance de energía
  07-lista-compra.md          ← lo que hay que comprar, con enlaces y precios
  08-guia-instalacion.md      ← guía de instalación completa, de la caja de material a la web funcionando
  img/                        ← esquema del sistema, conexionado del nodo, sondas en el depósito, pantalla OLED
  memoria/                    ← (se crea en la fase 7) capítulos de la memoria del TFG
firmware/nodo-agua/           ← proyecto PlatformIO de la LILYGO (OLED con logo de Los Viveros y temporizador del envío)
  herramientas/logo_a_xbm.py  ← convierte el logo PNG en include/logo.h
pruebas/payload/              ← prueba sin hardware: payload.h (C++) → decoder.js → campos del ingestor
raspberry/                    ← todo el servidor (ver raspberry/README.md para ponerlo en marcha)
  docker-compose.yml          ← ChirpStack, Mosquitto, TimescaleDB, ingestor, web, Caddy, DuckDNS
  .env.example                ← plantilla de contraseñas y token de DuckDNS (.env no se sube)
  configuracion/              ← ChirpStack (eu868, MQTT QoS 1) y Gateway Bridge
  codec/decoder.js            ← decodificador del payload para ChirpStack v4
  mosquitto/mosquitto.conf    ← broker interno con cola persistente
  db/                         ← creación de las bases de datos, tablas y usuarios
  ingestor/                   ← MQTT → TimescaleDB
  web/                        ← API (FastAPI) + página en tiempo real con gráficas (ECharts)
  caddy/                      ← HTTPS con certificado de Let's Encrypt por DNS de DuckDNS
  red/                        ← NetworkManager, chrony y firewall
  backup.sh                   ← copia diaria de las dos bases de datos
```

## 5. Datos pendientes (preguntar antes de cerrar la tarea afectada)

- [ ] Modelo exacto de la LILYGO (T3 V1.6.1 con SX1276, T3-S3 con SX1262, T-Beam...). Afecta a `firmware/nodo-agua/include/config.h`.
- [x] Ubicación: maqueta FUERA del edificio con alimentación solar; gateway dentro del centro (o en fachada).
- [x] Agua de red (dulce): salinidad del SEN0681 a 0 ‰ (es un ajuste del sensor de oxígeno, no un sensor).
- [x] Sin sonda de conductividad; sondas dentro del depósito, sin cámara de medida.
- [x] Conductividad quitada del firmware (`config.h`, `sensores.cpp`). El formato del payload **no cambia**:
      los bytes 8-9 van siempre a 0xFFFF ("sin dato"), `decoder.js` da `null` y la BD guarda NULL (`docs/04`).
      Si algún día se quiere quitar también de `decoder.js`/`10-init.sql`/ingestor, sería payload v3: preguntar antes.
- [ ] Modelo concreto de bomba (12 V, ≤ 1 A) y de caudalímetro (factor de pulsos por L/min).
- [ ] Consumo real del DFR1120 en reposo (si es clase C escucha siempre y gasta más).
- [ ] Registros Modbus del SEN0681 (copiar de la wiki oficial de DFRobot).
- [ ] Permiso del coordinador TIC del centro para conectar la Raspberry a la red del instituto y usar Tailscale.
- [ ] Subred real del instituto (en principio 192.168.155.x) y si el centro tiene IP pública propia.
- [ ] Permiso del coordinador TIC para reservar la IP de la Raspberry y reenviar el puerto 443 (DuckDNS). Si no, plan B con Tailscale Funnel.

## 6. Fases, tareas y criterios de aceptación

### Fase 1 — Organización
- [ ] Lista de compra entregada al centro (`docs/01-lista-material.md`).
- [ ] Cronograma y reparto de tareas en `docs/memoria/planificacion.md`.
- **Hecho cuando**: el tutor ha validado la lista y el plan.

### Fase 2 — Banco de pruebas del nodo (en el aula, con alimentación USB)
- [ ] Confirmar placa y pines; ajustar `config.h`.
- [ ] Compilar el firmware (`pio run`) sin errores.
- [ ] Leer ADS1115 (pH, nivel, batería) por el monitor serie en modo calibración.
- [ ] Leer SEN0681 por RS485 (oxígeno + temperatura) y poner salinidad a 0 si el agua es dulce.
- [ ] Calibrar pH (tampones 7 y 4) y guardar en NVS.
- **Hecho cuando**: el monitor serie muestra valores coherentes con las soluciones patrón (±0,1 pH).

### Fase 3 — Red y servidor en la Raspberry Pi 5 (`raspberry/README.md`)
- [ ] Raspberry Pi OS Lite 64 bits sobre NVMe, SSH con clave, usuario propio, actualizaciones.
- [ ] Red con `raspberry/red/configurar-red.sh`: eth0 = 192.168.50.1/24 en modo compartido (DHCP + NAT)
      hacia el wAP, eth1 (USB) = red del instituto por DHCP (`docs/02`).
- [ ] chrony como servidor NTP de la red privada; batería RTC colocada; comprobar `timedatectl`.
- [ ] `.env` rellenado y `docker compose up -d --build`: ChirpStack v4 (eu868, MQTT **QoS 1**),
      Gateway Bridge (UDP 1700), Mosquitto interno, TimescaleDB, ingestor, web, Caddy y DuckDNS.
- [ ] wAP LR8: IP estática 192.168.50.2, NTP → 192.168.50.1, servidor LoRa → 192.168.50.1:1700.
- [ ] Alta en ChirpStack: gateway (EUI del wAP), perfil de dispositivo EU868 / LoRaWAN 1.1 / OTAA / clase A,
      codec `decoder.js`, dispositivo con DevEUI y claves.
- [ ] Firewall con `raspberry/red/firewall.sh`.
- **Hecho cuando**: el nodo hace join, los uplinks salen decodificados en ChirpStack y aparecen en la web al momento.

### Fase 4 — Base de datos y web
- [ ] Comprobar cola persistente: parar el ingestor, enviar 2 uplinks, arrancarlo → deben entrar en la BD.
- [ ] Web: tarjetas en tiempo real, gráficas del histórico (6 h, 24 h, 7 días, 30 días, personalizado), descarga CSV.
- [ ] Ajustar los rangos de color de las tarjetas (`raspberry/web/static/app.js`) con datos reales.
- [ ] Copia de seguridad diaria (`raspberry/backup.sh` en cron) y prueba de restauración.
- **Hecho cuando**: hay 24 h de datos en la BD con hora correcta y se ven en la web.

### Fase 5 — Acceso remoto
- [ ] DuckDNS: cuenta, subdominio y token en `.env`; Caddy obtiene el certificado HTTPS.
- [ ] Coordinador TIC: reserva de IP de la Raspberry y reenvío del TCP 443. Si no es posible, `tailscale funnel`.
- [ ] Tailscale en la Raspberry y en los equipos del grupo; ChirpStack solo por `tailscale serve`.
- **Hecho cuando**: se ve la web desde un móvil con datos móviles, fuera del instituto.

### Fase 6 — Maqueta, energía e instalación exterior
- [ ] Montar la maqueta: base, depósito opaco, bomba, tubería, caudalímetro y soporte de sondas dentro del depósito (`docs/06-maqueta.md`).
- [ ] Medir consumo real (nodo activo, deep sleep, bomba, DFR1120) y revisar el balance de `docs/06-maqueta.md`.
- [ ] Montaje en caja estanca según `docs/03-conexionado-nodo.md`.
- [ ] Ubicar el gateway (idealmente en fachada, con visión directa a la maqueta) y medir RSSI/SNR.
- [ ] Pruebas de campo: RSSI/SNR, autonomía, estabilidad de lecturas durante 1 semana.
- **Hecho cuando**: una semana sin pérdidas significativas de paquetes y batería estable.

### Fase 7 — Alarmas y actuador (ampliación)
- [ ] Node-RED (contenedor en el mismo compose): alarmas por umbral (pH, O2, nivel, batería, nodo sin transmitir > 1 h).
- [ ] DFR1120-868 dado de alta como segundo nodo; downlink para activar su relé (baliza) ante alarma.
- [ ] Downlink de configuración al nodo principal: cambiar intervalo de envío (fPort 10).

### Fase 8 — Documentación (se hace en paralelo desde la fase 1)
- [ ] Capítulos de la memoria en `docs/memoria/`.
- [ ] Anexos: esquemas, código, configuración, pruebas y resultados.
