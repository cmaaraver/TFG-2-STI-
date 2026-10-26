# Maqueta exterior

## 1. Qué es
Depósito con agua de red con **todas las sondas colgadas dentro**, una bomba sumergida que mueve el agua
en circuito cerrado (sale por la tubería, pasa por el caudalímetro y vuelve al mismo depósito), y el
nodo LILYGO en una caja estanca. No hay cámara de medida aparte. El nodo y los sensores van alimentados con un
panel solar y una batería. **La bomba va aparte** (decisión de 2026-10-26): tiene su propia alimentación, no se
conecta al nodo y el nodo no la enciende ni la apaga; solo mide el caudal que da.
Está fuera del edificio; la telemetría entra al centro por LoRaWAN hasta el gateway.

```
        panel solar (orientado al sur, ~50°)
             │
   caja 1: LILYGO y placa base        caja 2: MPPT, batería y fusibles
             │ cables por la tapa (prensaestopas)
  ┌──────────┴──────────────────────┐
  │  soporte en la boca del depósito│◄── retorno ◄── válvula de bola ◄── caudalímetro ◄─┐
  │   ├─ sonda pH      (colgada)    │                                                    │
  │   └─ SEN0681 O2+T  (colgada)    │                                                    │
  │  DEPÓSITO opaco                 │                                                    │
  │   KIT0139 nivel (en el fondo)   │                                                    │
  │   bomba 12 V sumergida (aparte)─┼──► manguera ───────────────────────────────────────┘
  │   SEN0204 en la pared exterior  │
  └─────────────────────────────────┘
```

## 2. Funcionamiento en cada ciclo (cada 15 min)
La bomba, que va aparte, es la que mueve el agua para que las sondas no vean agua estancada. El nodo:
1. Se despierta, enciende los sensores y hace el join (o recupera la sesión LoRaWAN).
2. Espera 60 s a que se calienten los sensores (el SEN0681 tarda hasta 60 s en dar un valor estable).
3. En los últimos 10 s de esa espera mide el caudal. Si es menor de 0,3 L/min → aviso "bomba sin caudal"
   (la bomba está apagada, atascada o sin agua).
4. Lee todos los sensores, los apaga, envía el mensaje y se duerme.

## 3. Balance de energía (estimación, se confirma midiendo en la fase 6)

| Consumo | Cálculo | Wh/día |
|---|---|---|
| SEN0681 (0,2 W) + KIT0139 (~0,25 W) | 60 s × 96 | 0,7 |
| LILYGO activa + placas analógicas | ~70 s × 96 a ~0,9 W | 1,7 |
| Reposo (deep sleep, DC-DC, regulador MPPT) | ~25 mA × 12 V × 24 h | 7,2 |
| DFR1120 (fase 7, reserva hasta medirlo) | — | 5 |
| **Total** | | **≈ 15 Wh/día** (se dimensiona para 20) |

La bomba no entra en la cuenta porque va aparte, con su propia alimentación.

- **Batería**: 3 días sin sol → 20 × 3 / 0,8 (descarga útil LiFePO4) = 75 Wh → **12,8 V 20 Ah (256 Wh)**, más de una semana de margen.
- **Panel**: peor mes en Sevilla (diciembre) ≈ 2,5-3 horas de sol pico. 20 Wh / (2,5 h × 0,7) ≈ 12 W,
  y ×2 para recargar tras días nublados ≈ 25 W → el **panel de 50 W** va sobrado, inclinado ~50° al sur (mejor en invierno).
- Lo que más gasta es el reposo: elegir un DC-DC y un regulador MPPT con poco autoconsumo es lo que más ahorra.

## 4. Cosas a tener en cuenta por estar al aire libre
- **Temperatura**: el SEN0681 trabaja de 0 a 40 °C. En verano en Sevilla un depósito al sol pasa de eso:
  depósito blanco u opaco, a la sombra o con toldo, y la batería LiFePO4 también a la sombra.
- **Algas**: depósito opaco y tapado; limpiar sondas cada 2-4 semanas.
- **Sondas dentro del depósito**: colgadas del soporte a media altura, lejos de la salida de la bomba
  (el chorro y las burbujas falsean el oxígeno) y por encima del fondo (lodos). El nivel mínimo del
  depósito tiene que cubrir siempre la punta de la sonda de pH: si baja de ahí, alarma de rellenar.
- **Evaporación**: el nivel bajará solo; es un buen dato para el panel (y para la alarma de rellenar).
- **Vandalismo y robo**: caja con candado o tornillos de seguridad, dentro de una zona vallada del centro.
- **Lluvia y rayos**: prensaestopas hacia abajo (goteo), caja con membrana de ventilación, estructura y panel a tierra si es posible.
- **Radio**: el wAP LR8 va en el mástil de la azotea del instituto (decisión de 2026-10-26), lo más alto
  posible y con visión directa a la maqueta. Detalles del montaje en `docs/02-arquitectura-red.md`.
  Medir RSSI/SNR antes de apretar las abrazaderas.
