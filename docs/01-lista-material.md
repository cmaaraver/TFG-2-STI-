# Lista de material

## A. Material que ya tenemos y se usa

| Equipo | Modelo | Uso en el proyecto |
|---|---|---|
| Nodo | LILYGO ESP32 con LoRa (modelo por confirmar) | Lee sensores y envía por LoRaWAN |
| Gateway | MikroTik wAP LR8 kit (con fuente 24 V e inyector PoE) | Recibe LoRaWAN y reenvía a la Raspberry |
| Servidor LoRaWAN / router | Raspberry Pi 5 4 GB | ChirpStack, MQTT, NAT, NTP, Tailscale |
| Oxígeno disuelto + temperatura | DFRobot SEN0681 (RS485, 10-30 V, 0,2 W) | Sensor principal; su temperatura compensa pH y EC |
| pH | DFRobot SEN0169-V2 (sonda industrial) | Inmersión continua |
| Nivel de agua | DFRobot KIT0139 (4-20 mA) | Profundidad / nivel |
| Presencia de agua | DFRobot SEN0204 o SEN0509 | Alarma "cámara de medida seca" |
| Actuador (fase 7) | DFRobot DFR1120-868 | Relé controlado por downlink (baliza/alarma) |

## B. Material en reserva

| Modelo | Motivo |
|---|---|
| SEN0161-V2 (pH laboratorio) | Referencia para comprobar la calibración; no aguanta inmersión continua |
| SEN0237-A (O2 galvánico) | Repuesto; necesita electrolito y membrana |
| SEN0189 (turbidez) | Opcional, solo dentro de una cámara opaca (no es estanco, le afecta la luz) |
| SEN0507 (nivel capacitivo) | Repuesto de detección de líquido |
| DFR0886 Edge101 | Consume ~50 mA a 12 V en reposo; no apto para nodo solar |
| DFR0300-H (EC K=10) | Pensada para agua salina; con agua de red se sustituye por una K=1 (ver C) |

## C. Lista de compra para el centro

### Nodo de medida
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Sonda conductividad K=1 (DFRobot DFR0300 o SEN0451 industrial) | El agua es de red (dulce): la K=10 no sirve |
| 1 | ADC ADS1115 16 bits I2C (p. ej. Gravity DFR0553) | Lecturas analógicas mucho más estables que el ADC del ESP32 |
| 2 | Aislador de señal analógica Gravity (DFR0504) | pH y EC en la misma agua se interfieren |
| 1 | Adaptador RS485↔UART aislado (3,3 V, dirección automática) | Leer el SEN0681 |
| 1 | Convertidor 4-20 mA a tensión (si no viene en el KIT0139) | Leer el sensor de nivel |
| 1 | Convertidor DC-DC 12 V → 5 V, 1-2 A, bajo consumo en reposo | Alimentar la LILYGO |
| 2 | P-MOSFET + transistor NPN + resistencias (o módulo de conmutación en lado alto) | Apagar sensores entre medidas |
| 1 | Placa de topos doble cara 9×15 cm + tiras de pines hembra | Placa base para la LILYGO y módulos |
| 1 | Kit de cables Gravity PH2.0 3 pines + bornas de tornillo 5,08 mm | Conexiones desmontables |
| 3-4 | Conectores aviación GX12/GX16 estancos (4 y 5 pines) | Conectar sensores desde fuera de la caja |
| 2 | Pasamuros BNC hembra-hembra | Sondas de pH y EC |
| 1 | Antena 868 MHz exterior + pigtail pasamuros SMA | Radio del nodo |
| 1 | Caja estanca IP66/IP67 (~250×200×100 mm) + prensaestopas PG9 + membrana de ventilación | Protección |
| 1 | Tubo PVC Ø75-90 mm con tapón perforado + abrazaderas | Proteger las sondas en el agua |
| 1 | Resistencias 100 kΩ y 22 kΩ (1 %) | Medir tensión de batería |

### Maqueta
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Depósito opaco o blanco 50-100 L con tapa | Evitar algas y calentamiento |
| 1 | Bomba de recirculación 12 V DC sin escobillas (≤ 1 A, apta para exterior) | Renovar el agua en las sondas |
| 1 | Caudalímetro de efecto Hall (tipo YF-S201, 1/2") | Medir L/min como en el cartel |
| — | Tubería y racores de PVC 20-25 mm, codos, T, válvula de bola | Circuito de agua |
| 1 | Cámara de medida (tubo PVC Ø75-90 mm con tapas) | Sondas de pH, EC y O2 sumergidas |
| 1 | N-MOSFET de nivel lógico (IRLZ44N) + diodo 1N5819 + resistencia 100 kΩ | Encender la bomba desde la LILYGO |
| 1 | Resistencias 10 kΩ y 20 kΩ | Adaptar los pulsos del caudalímetro a 3,3 V |
| 1 | Base de madera tratada o perfil de aluminio + tornillería inox | Estructura |
| 1 | Toldo o sombra para depósito y batería | El SEN0681 trabaja hasta 40 °C |

### Energía (dimensionado en docs/06-maqueta.md, ≈ 35 Wh/día con la bomba)
| Cant. | Material |
|---|---|
| 1 | Panel solar 12 V 50 W, con soporte orientable (~50° al sur) |
| 1 | Batería LiFePO4 12,8 V 20 Ah (con BMS integrado) |
| 1 | Regulador de carga MPPT compatible con LiFePO4 (10 A) |
| 1 | Portafusibles + fusibles 3 A (carga) y 5 A (batería) |
| — | Cable solar 4 mm², terminales y bridas UV |

### Red y servidor
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Adaptador USB 3.0 a Gigabit Ethernet (chip Realtek RTL8153) | Salida a la red del instituto (funciona sin drivers) |
| 1 | Switch Gigabit 5 puertos no gestionable | Red privada: wAP, Raspberry, PC |
| 3 | Latiguillos Cat6 | Conexiones |
| 1 | SSD NVMe 256 GB + Raspberry Pi M.2 HAT+ | La SD se corrompe con escrituras continuas |
| 1 | Batería RTC oficial Raspberry Pi 5 | Mantener la hora sin corriente ni Internet |
| 1 | Fuente oficial Raspberry Pi 27 W USB-C + Active Cooler | Estabilidad |
| 1 | SAI pequeño (opcional) | Evitar corrupción por cortes |
| 1 | PC servidor de datos (del centro): 8 GB RAM, SSD ≥ 256 GB | Base de datos y Grafana |

### Calibración
| Cant. | Material |
|---|---|
| 1 | Soluciones tampón pH 4,00 / 7,00 / 10,00 |
| 1 | Solución conductividad 1413 µS/cm |
| 1 | Agua destilada y vasos de precipitado |
