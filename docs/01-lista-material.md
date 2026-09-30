# Lista de material

Versión 2 (2026-09-29). Cambios respecto a la versión anterior:
- **Se quita la medida de conductividad (sensor de sales)**: fuera la sonda K=1, su placa, un aislador,
  un pasamuros BNC y la solución de 1413 µS/cm. La DFR0300-H (K=10) tampoco se usa.
- **Circuito de agua completo**: bomba, tubos, racores, válvula, filtro y soporte con cantidades.
- **Sin cámara de medida**: las sondas van colgadas dentro del depósito.
- **Todo lo de la maqueta es autónomo**: bomba, LILYGO y sensores funcionan solo con el panel solar y la
  batería. No hay ningún cable de 230 V ni de red hasta la maqueta; los datos salen por LoRaWAN.

Enlaces de compra y precios de todo esto: `07-lista-compra.md`. Lo que lleva `TODO VERIFICAR` se comprueba con la ficha del modelo que se compre antes de pedirlo.

## A. Material que ya tenemos y se usa

| Equipo | Modelo | Uso en el proyecto |
|---|---|---|
| Nodo | LILYGO ESP32 con LoRa (modelo por confirmar) | Lee sensores, controla la bomba y envía por LoRaWAN |
| Gateway | MikroTik wAP LR8 kit (con fuente 24 V e inyector PoE) | Recibe LoRaWAN y reenvía a la Raspberry |
| Servidor completo | Raspberry Pi 5 4 GB | ChirpStack, MQTT, base de datos, web, DuckDNS, NAT, NTP |
| Almacenamiento de la Raspberry | microSD 64 GB | Sistema y datos (sin SSD NVMe, decisión de 2026-09-29) |
| Oxígeno disuelto + temperatura | DFRobot SEN0681 (RS485, 10-30 V, 0,2 W) | Sensor principal; su temperatura compensa el pH |
| pH | DFRobot SEN0169-V2 (sonda industrial) | Inmersión continua dentro del depósito |
| Nivel de agua | DFRobot KIT0139 (4-20 mA) | Nivel del depósito (evaporación, alarma de rellenar) |
| Presencia de agua | DFRobot SEN0204 o SEN0509 (se usa uno) | Alarma de nivel mínimo (sonda de pH a punto de quedar al aire) |
| Actuador (fase 7) | DFRobot DFR1120-868 | Relé controlado por downlink (baliza/alarma) |

## B. Material en reserva (no se usa)

| Modelo | Motivo |
|---|---|
| SEN0161-V2 (pH laboratorio) | Referencia para comprobar la calibración; no aguanta inmersión continua |
| SEN0237-A (O2 galvánico) | Repuesto; necesita electrolito y membrana |
| SEN0189 (turbidez) | Opcional, solo dentro de una cámara opaca (no es estanco, le afecta la luz) |
| SEN0507 (nivel capacitivo) | Repuesto de detección de líquido |
| DFR0886 Edge101 | Consume ~50 mA a 12 V en reposo; no apto para nodo solar |
| DFR0300-H (EC K=10) | Se quita la medida de conductividad |

## C. Lista de compra para el centro

### C1. Electrónica del nodo (dentro de la caja estanca de electrónica)
| Cant. | Material | Motivo |
|---|---|---|
| 1 | ADC ADS1115 16 bits I2C (Adafruit, dirección 0x48) | Lecturas analógicas estables (pH, nivel, batería) |
| 1 | Aislador de señal analógica Gravity (DFR0504) | Aísla el pH de la masa de la bomba, que está en la misma agua |
| 1 | Adaptador RS485↔UART aislado (3,3 V, dirección automática) | Leer el SEN0681 |
| 1 | Convertidor DC-DC 12 V → 5 V, 1-2 A, bajo consumo en reposo (< 1 mA) | Alimentar la LILYGO y los módulos de 5 V |
| 1 | P-MOSFET IRF9540N o AOD417 + NPN BC547 + resistencias 10k, 1k, 100k | Conmutador 12 V de sensores (`docs/03`, apartado 4) |
| 1 | P-MOSFET AO3401 + NPN BC547 + resistencias 10k, 1k, 100k | Conmutador 5 V de sensores |
| 1 | N-MOSFET de nivel lógico IRLZ44N + diodo 1N5819 + resistencias 220 Ω y 100 kΩ | Encender la bomba desde la LILYGO |
| 1 | Resistencias 1 %: 100 kΩ y 22 kΩ (batería), 10 kΩ y 20 kΩ (caudalímetro), 2 × 10 kΩ (pull-ups) | Divisores y entradas |
| 1 | Placa de topos doble cara 9×15 cm + tiras de pines hembra y macho | Placa base (la LILYGO va pinchada, no soldada) |
| 1 | Bornas de tornillo 5,08 mm (2 y 3 polos, ~10 uds) | Entradas de alimentación, bomba, RS485 |
| 1 | Kit de cables Gravity PH2.0 3 pines | Conectar módulos Gravity a la placa base |
| 1 | Antena 868 MHz exterior + pigtail u.FL/SMA a pasamuros SMA hembra | Radio del nodo (nunca encender sin antena) |
| 1 | Cable USB-C / micro-USB de datos (según la LILYGO) | Programar y monitor serie |

### C2. Cajas, conectores y cableado exterior
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Caja estanca IP66/IP67 ~250×200×100 mm | Electrónica del nodo |
| 1 | Caja estanca IP66 ~300×250×150 mm (o caja de batería ventilada) | Batería LiFePO4, regulador MPPT y fusibles (la batería no cabe con la electrónica) |
| 2 | Membrana de ventilación IP67 (tapón transpirable M12) | Evitar condensación en las dos cajas |
| 5 | Conectores de aviación GX16 estancos macho+hembra: 4 pines (SEN0681), 2 pines (bomba), 3 pines (caudalímetro, presencia de agua, nivel) | Desmontar sensores sin abrir la caja |
| 1 | Pasamuros BNC hembra-hembra | Sonda de pH |
| 6 | Prensaestopas PG9/PG11 (cables entre cajas y del panel) | Entradas de cable, siempre hacia abajo |
| 5 m | Manguera apantallada 4 × 0,5 mm² | Alargar SEN0681 (RS485 + 12 V) si su cable no llega |
| 5 m | Manguera 3 × 0,5 mm² exterior | Caudalímetro, presencia de agua, nivel |
| 3 m | Manguera 2 × 1 mm² exterior | Bomba |
| 1 | Bolsitas de gel de sílice + barniz protector (conformal coating) | Humedad en la placa |
| 1 | Candado o tornillos de seguridad para las cajas | Vandalismo |

### C3. Circuito de agua y soporte de sondas (maqueta)

Las sondas van **colgadas directamente dentro del depósito**; no hay cámara de medida.
Recorrido del agua: bomba sumergida en el depósito → manguera → caudalímetro → válvula de bola →
retorno por la tapa al mismo depósito. Como no hay cámara que vaciar, **no hace falta válvula antirretorno**.

| Cant. | Material | Motivo |
|---|---|---|
| 1 | Depósito opaco o blanco 50-100 L con tapa | Evitar algas y calentamiento; dentro van todas las sondas |
| 1 | Bomba sumergible 12 V DC sin escobillas, ≤ 1 A, 3-8 L/min, altura ≥ 2 m, salida para tubo 1/2" (TODO VERIFICAR modelo; tipo DC40) | Mover el agua del depósito. Sin escobillas: dura años y apenas mete ruido eléctrico |
| 1 | Rejilla/filtro de aspiración para la bomba (o malla inox atada) | Que no entren algas ni suciedad al caudalímetro |
| 1 | Caudalímetro de efecto Hall YF-S201 (rosca macho G1/2", 1-30 L/min) | Medir L/min (comprueba que la bomba funciona) |
| 1 | Válvula de bola PVC 1/2" | Regular el caudal |
| 3 m | Tubo flexible PVC transparente reforzado (manguera cristal) Ø interior 13 mm | Bomba → caudalímetro → válvula → retorno. Opaco o pintado si hay algas |
| 4 | Racor de espiga 1/2" para manguera 13 mm con rosca G1/2" | Unir la manguera al caudalímetro y a la válvula |
| 8 | Abrazaderas inox para manguera 12-20 mm | Sujetar las espigas |
| 1 | Perfil de aluminio en U o pletina de ~60 cm (más largo que la boca del depósito) | Soporte que cruza la boca del depósito y del que cuelgan las sondas |
| 3 | Prensaestopas del diámetro de cada sonda o clips/abrazaderas de cable (pH, SEN0681, cable del KIT0139) (TODO VERIFICAR medir las sondas) | Fijar cada sonda a su profundidad en el soporte |
| 2 | Prensaestopas PG16 para la tapa del depósito | Paso de cables y del tubo de retorno |
| 1 | Cinta de teflón | Roscas |
| 1 | Base de madera tratada o perfil de aluminio + tornillería inox | Estructura |
| 1 | Toldo o sombra para depósito y caja de batería | El SEN0681 trabaja hasta 40 °C y la LiFePO4 no debe calentarse |

### C4. Energía autónoma (dimensionado en `docs/06-maqueta.md`, ≈ 35 Wh/día con la bomba)
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Panel solar 12 V 50 W monocristalino | Carga diaria con margen en diciembre |
| 1 | Soporte de panel orientable (~50° al sur) + tornillería inox | Mejor producción en invierno |
| 1 | Batería LiFePO4 12,8 V 20 Ah con BMS integrado (mejor con protección de carga a baja temperatura) | 3-6 días sin sol |
| 1 | Regulador de carga MPPT compatible con LiFePO4, 10 A, **con salida de carga y corte por baja tensión**, bajo autoconsumo (TODO VERIFICAR autoconsumo en la ficha) | Carga la batería y alimenta todo el nodo; corta la carga antes de vaciar la batería |
| 2 | Portafusibles estancos + fusibles 5 A (batería) y 3 A (salida de carga) | Protección contra cortocircuitos |
| 1 | Interruptor/desconectador general 12 V | Apagar todo para trabajar en la maqueta |
| 5 m | Cable solar 4 mm² rojo/negro + par de conectores MC4 | Panel → MPPT |
| 2 m | Cable 2,5 mm² + terminales de ojal y punteras | Batería, MPPT y salida de carga |
| 1 | Bridas negras resistentes a UV | Sujeción del cableado exterior |
| 1 | Cable de tierra 6 mm² + pica de tierra (si no hay tierra cerca) | Estructura y marco del panel a tierra (rayos) |

### C5. Red y servidor (dentro del edificio)
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Adaptador USB 3.0 a Gigabit Ethernet (chip Realtek RTL8153) | Salida a la red del instituto (funciona sin drivers) |
| 2 | Latiguillos Cat6 (+ 1 cable Cat6 exterior si el wAP va en fachada) | Raspberry-inyector PoE y red del instituto (sin switch: solo está el wAP) |
| 1 | Batería RTC oficial Raspberry Pi 5 | Mantener la hora sin corriente ni Internet |
| 1 | Fuente oficial Raspberry Pi 27 W USB-C + Active Cooler | Estabilidad |
| 1 | SAI pequeño (opcional) | Evitar corrupción por cortes |

### C6. Calibración, medida y mantenimiento
| Cant. | Material | Motivo |
|---|---|---|
| 1 | Soluciones tampón pH 4,00 / 7,00 / 10,00 | Calibrar el pH |
| 1 | Solución de almacenamiento de electrodos de pH (KCl 3 M) | Guardar la sonda si se desmonta |
| 1 | Agua destilada, vasos de precipitado y cepillo suave | Calibración y limpieza de sondas |
| 1 | Vatímetro DC 12 V en línea (o multímetro con escala de mA) | Medir consumos reales en la fase 6 |
