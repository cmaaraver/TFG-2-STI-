# CLAUDE.md — TFG Monitorización de calidad del agua (LoRaWAN)

Este fichero lo lee Claude Code al abrir el repositorio. Es el plan maestro del proyecto.
Léelo entero antes de hacer nada y consulta la carpeta `docs/` para los detalles.

## 1. Contexto

- TFG de 2º de Grado Superior STI (Sistemas de Telecomunicaciones e Informáticos), CPIFP Los Viveros (Sevilla).
- Equipo: Carlos Maraver Román (responsable técnico) y Rubén Trillo García.
- Objetivo: maqueta exterior (depósito + bomba de recirculación + sensores) alimentada con energía solar,
  que mide la calidad del agua (oxígeno disuelto, pH, conductividad, temperatura, nivel y caudal),
  envía la telemetría por LoRaWAN al gateway situado en el edificio, la guarda con fecha y hora en
  una base de datos y la muestra en un panel accesible desde fuera del instituto.
- Referencia: proyecto de innovación colaborativo "Sistema de telemetría para la monitorización de la
  calidad del agua" (cartel del centro). Nuestra versión sustituye WiFi por LoRaWAN privado y añade
  oxígeno, conductividad y control remoto de la bomba.

## 2. Arquitectura (resumen)

```
 [Sondas] → [LILYGO ESP32 LoRa] ~~~ LoRaWAN EU868 ~~~ [MikroTik wAP LR8]
                 (nodo solar)                               │ PoE + Ethernet
                                                            ▼
                                  ┌──────── RED PRIVADA 192.168.50.0/24 ────────┐
                                  │  switch                                     │
                                  │   ├─ wAP LR8 ........ 192.168.50.2          │
                                  │   ├─ Raspberry Pi 5 . 192.168.50.1 (eth0)   │
                                  │   └─ PC de datos .... 192.168.50.5          │
                                  └─────────────────────────────────────────────┘
                                                            │
                          Raspberry Pi 5 eth1 (adaptador USB-Ethernet) → red del instituto → Internet
```

| Equipo | Función | Software |
|---|---|---|
| LILYGO (nodo, maqueta exterior) | Recircula el agua con la bomba, mide caudal y sensores, envía cada 15 min, duerme | Firmware PlatformIO + RadioLib (LoRaWAN 1.1, OTAA) |
| DFR1120-868 (maqueta, fase 7) | Relé controlado por downlink (llenado, alarma o anulación de la bomba) | Configuración propia de DFRobot |
| wAP LR8 | Gateway LoRaWAN, reenvía por UDP 1700 | RouterOS (packet forwarder nativo) |
| Raspberry Pi 5 | Router/NAT/firewall de la red privada, servidor NTP, servidor LoRaWAN, broker MQTT, alarmas | Raspberry Pi OS Lite 64 bits, NetworkManager, chrony, ufw, Docker: ChirpStack v4 + Gateway Bridge + PostgreSQL + Redis + Mosquitto, Node-RED, Tailscale |
| PC de datos | Base de datos histórica y panel | Ubuntu Server 24.04 LTS, Docker: TimescaleDB, ingestor Python, Grafana, copias de seguridad, Tailscale |

Flujo de datos: nodo → wAP → ChirpStack (decodifica con `raspberry/codec/decoder.js`) → MQTT (QoS 1)
→ ingestor en el PC → TimescaleDB → Grafana.

Detalle completo en `docs/02-arquitectura-red.md`.

## 3. Reglas para Claude Code

1. **Idioma**: código comentado en español, nombres de variables en español sencillo. Documentación en español.
2. **No inventar datos de hardware.** Registros Modbus del SEN0681, pines de la LILYGO, fórmulas de sondas,
   parámetros de ChirpStack o RouterOS: si no están confirmados en este repo, se consultan en la
   documentación oficial (wiki DFRobot, pinout LILYGO, docs ChirpStack/MikroTik) y se cita la fuente
   en un comentario. Si no se puede confirmar, se deja un `TODO VERIFICAR` y se avisa.
3. **Secretos fuera de git**: claves LoRaWAN, contraseñas de MQTT, BD y Grafana en `secrets.h` / `.env`
   (existen plantillas `*.example`). Añadir al `.gitignore`.
4. **Hora siempre en UTC** en la base de datos (`timestamptz`). Grafana muestra Europe/Madrid.
5. **Todo en Docker Compose** con `restart: unless-stopped`, volúmenes con nombre y healthchecks.
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
  memoria/                    ← (se crea en la fase 7) capítulos de la memoria del TFG
firmware/nodo-agua/           ← proyecto PlatformIO de la LILYGO
raspberry/
  codec/decoder.js            ← decodificador del payload para ChirpStack v4
  mosquitto/mosquitto.conf    ← broker con cola persistente
  red/                        ← configuración de red, chrony y firewall
servidor-datos/               ← Docker Compose del PC: TimescaleDB + ingestor + Grafana
```

## 5. Datos pendientes (preguntar antes de cerrar la tarea afectada)

- [ ] Modelo exacto de la LILYGO (T3 V1.6.1 con SX1276, T3-S3 con SX1262, T-Beam...). Afecta a `firmware/nodo-agua/include/config.h`.
- [x] Ubicación: maqueta FUERA del edificio con alimentación solar; gateway dentro del centro (o en fachada).
- [x] Agua de red (dulce): sonda de conductividad K=1 y salinidad del SEN0681 a 0 ‰.
- [ ] Modelo concreto de bomba (12 V, ≤ 1 A) y de caudalímetro (factor de pulsos por L/min).
- [ ] Consumo real del DFR1120 en reposo (si es clase C escucha siempre y gasta más).
- [ ] Registros Modbus del SEN0681 (copiar de la wiki oficial de DFRobot).
- [ ] Permiso del coordinador TIC del centro para conectar la Raspberry a la red del instituto y usar Tailscale.
- [ ] PC que se usará como servidor de datos (características).

## 6. Fases, tareas y criterios de aceptación

### Fase 1 — Organización
- [ ] Lista de compra entregada al centro (`docs/01-lista-material.md`).
- [ ] Cronograma y reparto de tareas en `docs/memoria/planificacion.md`.
- **Hecho cuando**: el tutor ha validado la lista y el plan.

### Fase 2 — Banco de pruebas del nodo (en el aula, con alimentación USB)
- [ ] Confirmar placa y pines; ajustar `config.h`.
- [ ] Compilar el firmware (`pio run`) sin errores.
- [ ] Leer ADS1115 (pH, EC, nivel, batería) por el monitor serie en modo calibración.
- [ ] Leer SEN0681 por RS485 (oxígeno + temperatura) y poner salinidad a 0 si el agua es dulce.
- [ ] Calibrar pH (tampones 7 y 4) y EC (1413 µS/cm) y guardar en NVS.
- **Hecho cuando**: el monitor serie muestra valores coherentes con las soluciones patrón (±0,1 pH, ±5 % EC).

### Fase 3 — Red y servidor LoRaWAN (Raspberry Pi 5)
- [ ] Raspberry Pi OS Lite 64 bits sobre NVMe, SSH con clave, usuario propio, actualizaciones.
- [ ] Red: eth0 = 192.168.50.1/24 en modo compartido (DHCP + NAT), eth1 = red del instituto por DHCP (`docs/02`).
- [ ] Firewall ufw: denegar entrada por eth1; permitir LAN privada y `tailscale0`.
- [ ] chrony como servidor NTP de la LAN; batería RTC colocada; comprobar `timedatectl`.
- [ ] ChirpStack v4 con Docker basado en el repositorio oficial `chirpstack/chirpstack-docker`,
      región `eu868`, Gateway Bridge por UDP 1700, integración MQTT con **QoS 1**.
- [ ] Mosquitto con listener interno (red Docker) y listener LAN autenticado (`raspberry/mosquitto/mosquitto.conf`).
- [ ] wAP LR8: IP estática 192.168.50.2, NTP → 192.168.50.1, servidor LoRa → 192.168.50.1:1700.
- [ ] Alta en ChirpStack: gateway (EUI del wAP), perfil de dispositivo EU868 / LoRaWAN 1.1 / OTAA / clase A,
      codec `decoder.js`, dispositivo con DevEUI y claves.
- **Hecho cuando**: el nodo hace join y los uplinks aparecen decodificados en ChirpStack y en `mosquitto_sub`.

### Fase 4 — Servidor de datos (PC)
- [ ] Ubuntu Server 24.04 LTS, IP 192.168.50.5, NTP → 192.168.50.1.
- [ ] `servidor-datos/docker-compose.yml` levantado (TimescaleDB + ingestor + Grafana).
- [ ] Comprobar cola persistente: apagar el ingestor, enviar 2 uplinks, encenderlo → deben entrar en la BD.
- [ ] Panel Grafana: series de cada parámetro, estado de batería, RSSI/SNR, última recepción.
- [ ] Copia de seguridad diaria con `pg_dump` (cron en el host) y prueba de restauración.
- **Hecho cuando**: los datos de 24 h están en la BD con hora correcta y se ven en Grafana.

### Fase 5 — Acceso remoto
- [ ] Tailscale en Raspberry (subnet router de 192.168.50.0/24) y en el PC.
- [ ] Acceso privado del equipo a Grafana y ChirpStack por Tailscale.
- [ ] (Opcional) Enlace público de solo lectura a Grafana con Tailscale Funnel desde el PC.
- **Hecho cuando**: se ve el panel desde un móvil con datos móviles, fuera del instituto.

### Fase 6 — Maqueta, energía e instalación exterior
- [ ] Montar la maqueta: base, depósito opaco, bomba, tubería, caudalímetro y soportes de sondas (`docs/06-maqueta.md`).
- [ ] Medir consumo real (nodo activo, deep sleep, bomba, DFR1120) y revisar el balance de `docs/06-maqueta.md`.
- [ ] Montaje en caja estanca según `docs/03-conexionado-nodo.md`.
- [ ] Ubicar el gateway (idealmente en fachada, con visión directa a la maqueta) y medir RSSI/SNR.
- [ ] Pruebas de campo: RSSI/SNR, autonomía, estabilidad de lecturas durante 1 semana.
- **Hecho cuando**: una semana sin pérdidas significativas de paquetes y batería estable.

### Fase 7 — Alarmas y actuador (ampliación)
- [ ] Node-RED: alarmas por umbral (pH, O2, nivel, batería, nodo sin transmitir > 1 h).
- [ ] DFR1120-868 dado de alta como segundo nodo; downlink para activar su relé (baliza) ante alarma.
- [ ] Downlink de configuración al nodo principal: cambiar intervalo de envío (fPort 10).

### Fase 8 — Documentación (se hace en paralelo desde la fase 1)
- [ ] Capítulos de la memoria en `docs/memoria/`.
- [ ] Anexos: esquemas, código, configuración, pruebas y resultados.
