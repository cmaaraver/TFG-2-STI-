# Conexionado y montaje del nodo

> Pines de la LILYGO según `firmware/nodo-agua/include/config.h`, sacados del `utilities.h` oficial de LilyGO
> (https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series). **Verificar con la placa exacta antes de soldar nada.**
> Los de abajo son para la T3 V1.6.1 (SX1276).

![Conexionado del nodo](img/conexionado-nodo.png)

(El dibujo se puede editar: `img/conexionado-nodo.svg`.)

## 1. Idea general: no soldar los sensores a la LILYGO

Todo va sobre una **placa base de topos** dentro de la caja estanca:
- La LILYGO va **pinchada en tiras de pines hembra**, no soldada. Si se rompe, se cambia en 1 minuto.
- Los módulos Gravity (placa del pH, aislador, ADS1115) se conectan con sus
  **cables PH2.0 de 3 pines** a tiras de pines macho soldadas en la placa base.
- Alimentación, RS485 y cables largos entran por **bornas de tornillo**.
- Los sensores exteriores entran por **conectores de aviación GX12/GX16** en la pared de la caja
  y la sonda de pH por **pasamuros BNC**. Así se desmonta un sensor sin abrir la caja.
- Lo único que se suelda es la placa base (pines, bornas, MOSFET, resistencias, puentes).

## 2. Esquema de bloques

```
 Panel 12V ──► Regulador MPPT ◄──► Batería LiFePO4 12,8 V
                    │ salida CARGA
                  [F 3A]
                    ├──────────────► DC-DC 12→5 V ──► LILYGO 5V/VBUS  (siempre)
                    │                                   └─ 3V3 ──► ADS1115 (siempre, 3,3 V)
                    ├──[N-MOSFET, GPIO BOMBA]──────────► Bomba 12 V (con diodo en paralelo)
                    ├──[conmutador 12V, GPIO EN_12V]──► SEN0681 (oxígeno) 10-30 V
                    │                                  └► KIT0139 (nivel 4-20 mA)
                    └──[divisor 100k/22k]──────────────► ADS1115 A3 (batería)

  DC-DC 5 V ──[conmutador 5V, GPIO EN_5V]──► placa pH ──► aislador ──► ADS1115 A0
                                          ├► convertidor 4-20 mA ────► ADS1115 A2
                                          ├► adaptador RS485 (lado aislado lo alimenta él)
                                          ├► SEN0204 (presencia de agua) ──► GPIO AGUA
                                          └► Caudalímetro ──[divisor 10k/20k]──► GPIO CAUDAL
```

## 3. Tabla de conexiones (LILYGO T3 V1.6.1)

| Señal | Pin LILYGO | Va a | Notas |
|---|---|---|---|
| 5 V entrada | 5V / VBUS | Salida DC-DC 5 V | No conectar USB y 5 V externo a la vez sin revisar el esquema de la placa |
| GND | GND | Masa común (punto estrella en la placa base) | |
| I2C SDA | GPIO 21 | ADS1115 SDA | Compartido con la OLED de la placa (0x3C). ADS1115 en 0x48 |
| I2C SCL | GPIO 22 | ADS1115 SCL | |
| RS485 TX | GPIO 13 | Adaptador RS485 RX(D) | UART2 |
| RS485 RX | GPIO 14 | Adaptador RS485 TX(D) | |
| EN_12V | GPIO 4 | Base del NPN del conmutador 12 V | HIGH = sensores 12 V encendidos |
| EN_5V | GPIO 25 | Puerta/driver del conmutador 5 V | HIGH = sensores 5 V encendidos (el LED de la placa también parpadea) |
| AGUA | GPIO 39 | Salida SEN0204 | Solo entrada; poner pull-up externa 10 kΩ a 3,3 V. Comprobar nivel de salida (≤3,3 V) |
| MODO_CAL | GPIO 36 | Puente a GND | Solo entrada; pull-up externa 10 kΩ. Puente puesto al arrancar = modo calibración |
| BOMBA | GPIO 12 | Puerta del N-MOSFET (IRLZ44N) de la bomba | Pull-down 100 kΩ obligatoria: GPIO12 es pin de arranque y tiene que estar a 0 al encender (si no, el ESP32 no arranca y la bomba podría encenderse sola) |
| CAUDAL | GPIO 34 | Salida del caudalímetro por divisor 10k/20k | Solo entrada; el caudalímetro va a 5 V y sus pulsos llegan a ~3,3 V |
| Radio LoRa | 5,18,19,23,26,27,33 | Internos | No usar |
| Antena | Conector u.FL/SMA | Pigtail a pasamuros SMA | **Nunca encender sin antena** |
| OLED | Interna (I2C 21/22, 0x3C) | — | Ya viene en la placa. Muestra el logo de Los Viveros, la fase del ciclo y el temporizador del envío LoRa |

**No poner tarjeta microSD en la LILYGO.** En la T3 V1.6.1 el lector de tarjetas usa los GPIO 2, 13, 14 y 15
(`utilities.h` de LilyGO) y nosotros usamos el 13 y el 14 para el RS485. Por eso la bomba tampoco va en el GPIO 2.

### ADS1115 (dirección 0x48, ADDR a GND)
| Canal | Señal | Rango esperado |
|---|---|---|
| A0 | pH (tras aislador) | 0-3 V |
| A1 | Libre (antes conductividad) | — |
| A2 | Nivel (convertidor 4-20 mA) | ~0,48-2,4 V (4-20 mA en 120 Ω, verificar) |
| A3 | Batería (divisor 100k/22k) | 12,8 V → ~2,3 V |

Ganancia `GAIN_ONE` (±4,096 V). Nunca meter más de VDD+0,3 V (3,6 V) en una entrada.

### SEN0681 (oxígeno) — colores del cable
| Cable | Función | Va a |
|---|---|---|
| Marrón | VCC 10-30 V | Salida del conmutador 12 V |
| Negro | GND | Masa |
| Amarillo | RS485 A | Borna A del adaptador |
| Azul | RS485 B | Borna B del adaptador |

## 4. Conmutador de 12 V (lado alto), para soldar en la placa base
```
 +12V ───┬──────────── S  P-MOSFET (IRF9540N / AOD417)
         │                D ──────► +12V_SENSORES
        [10k]           G
         │               │
         └───────────────┤
                         C  NPN (BC547 / 2N2222)
 GPIO EN_12V ──[1k]──── B
                         E ── GND
```
GPIO en HIGH → NPN conduce → puerta a masa → MOSFET conduce. Añadir 100 kΩ de base a masa
para que al arrancar el ESP32 los sensores queden apagados. El de 5 V es igual con un P-MOSFET
de nivel lógico (AO3401).

## 5. Bomba (lado bajo, N-MOSFET)
```
 +12V (tras fusible) ───────── Bomba (+)
                         ┌──── Bomba (−) ────┐
               diodo 1N5819 (cátodo a +12V)  D
                                             N-MOSFET IRLZ44N
 GPIO BOMBA ──[220 Ω]──────────────────────── G
                   └──[100 kΩ]── GND         S ── GND
```
El diodo protege el MOSFET del pico que da el motor al apagarse.

## 6. Buenas prácticas del montaje
- Masa en estrella: todas las masas llegan a un punto; la sonda de pH lejos del DC-DC.
- Sonda de pH siempre mojada: se puede apagar su placa, pero la sonda no puede secarse.
- Cables de sondas separados de los de 12 V; RS485 con par trenzado.
- Membrana de ventilación en la caja (evita condensación) y bolsitas de gel de sílice.
- Barniz protector (conformal coating) sobre la placa base una vez probada.
- Etiquetar cada cable en los dos extremos.
- Sondas colgadas del soporte dentro del depósito, con el cable sujeto para que no tire del conector.

## 7. Instalación física de las sondas en el depósito

![Instalación de las sondas](img/instalacion-sensores.png)

| Sensor | Dónde va | Cómo se sujeta | Ojo con |
|---|---|---|---|
| pH SEN0169-V2 | Colgado del soporte de la tapa, a media altura, lado contrario a la bomba | Prensaestopas o abrazadera en el soporte; la punta siempre por debajo del nivel mínimo | Nunca dejarlo en seco. Cable BNC sin tensión |
| Oxígeno SEN0681 | Colgado junto al pH, membrana hacia abajo | Igual que el pH | Lejos del retorno y de la bomba (las burbujas falsean el O2) |
| Nivel KIT0139 | Apoyado en el fondo | Colgado de su propio cable hasta tocar fondo | El cable lleva un tubo de aire dentro: no aplastarlo ni doblarlo fuerte; el extremo del cable, dentro de la caja seca |
| Bomba 12 V | En el fondo, lado contrario a las sondas | Con su rejilla de aspiración | Que no aspire lodo: un par de cm por encima del fondo si tiene patas |
| Presencia de agua SEN0204 | Pegado por fuera de la pared del depósito, a la altura del nivel mínimo | Cinta de doble cara o adhesivo | Detecta a través de una pared de hasta 13 mm (wiki DFRobot SEN0204: "thickness of induction 0 ~ 13 mm"); sin metal cerca |
| Caudalímetro YF-S201 | En la tubería de salida, horizontal, antes de la válvula | Racores de espiga 1/2" | La flecha del cuerpo en el sentido del agua |

Los cables salen de la caja 1 por los prensaestopas y conectores GX16, **siempre hacia abajo** para que el agua
de lluvia gotee y no entre. Etiquetar cada conector con el nombre del sensor.
