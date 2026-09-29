# Maqueta exterior

## 1. Qué es
Depósito con agua de red, una bomba que recircula el agua por un circuito de tubería donde van
las sondas, y el nodo LILYGO en una caja estanca. Todo alimentado con un panel solar y una batería.
Está fuera del edificio; la telemetría entra al centro por LoRaWAN hasta el gateway.

```
        panel solar (orientado al sur, ~50°)
             │
  ┌──────────┴──────────┐      caja estanca: LILYGO, placa base, MPPT, batería (o caja aparte)
  │                     │
  │   DEPÓSITO opaco    │──► bomba 12 V ──► caudalímetro ──► cámara de sondas (pH, EC, O2) ──┐
  │   (KIT0139 al fondo,│                                     SEN0509 en la tubería           │
  │    SEN0204 en pared)│◄─────────────────────────── retorno ────────────────────────────────┘
  └─────────────────────┘
```

## 2. Funcionamiento en cada ciclo (cada 15 min)
1. Se despierta la LILYGO, enciende sensores y bomba.
2. La bomba recircula 45 s para que las sondas vean agua "nueva" (no agua estancada).
3. En los últimos 10 s se mide el caudal. Si es menor de 0,3 L/min → aviso "bomba sin caudal".
4. Se para la bomba y se esperan 5 s con el agua quieta (el motor mete ruido en pH y EC).
5. Se leen todos los sensores, se apaga todo, se envía el mensaje y se duerme.

## 3. Balance de energía (estimación, se confirma midiendo en la fase 6)

| Consumo | Cálculo | Wh/día |
|---|---|---|
| Bomba 12 V ~0,8 A (≈10 W) | 45 s × 96 ciclos = 72 min | 12 |
| SEN0681 (0,2 W) + KIT0139 (~0,25 W) | 60 s × 96 | 0,7 |
| LILYGO activa + placas analógicas | ~70 s × 96 a ~0,9 W | 1,7 |
| Reposo (deep sleep, DC-DC, regulador MPPT) | ~25 mA × 12 V × 24 h | 7,2 |
| DFR1120 (fase 7, reserva hasta medirlo) | — | 5 |
| **Total** | | **≈ 27 Wh/día** (se dimensiona para 35) |

- **Batería**: 3 días sin sol → 35 × 3 / 0,8 (descarga útil LiFePO4) ≈ 130 Wh → **12,8 V 20 Ah (256 Wh)**, casi una semana de margen.
- **Panel**: peor mes en Sevilla (diciembre) ≈ 2,5-3 horas de sol pico. 35 Wh / (2,5 h × 0,7) ≈ 20 W,
  y ×2 para recargar tras días nublados → **panel de 50 W**, inclinado ~50° al sur (mejor en invierno).
- La bomba es el 45 % del consumo: si hiciera falta ahorrar, se baja `T_BOMBA_MS` o se bombea 1 de cada 2 ciclos.

## 4. Cosas a tener en cuenta por estar al aire libre
- **Temperatura**: el SEN0681 trabaja de 0 a 40 °C. En verano en Sevilla un depósito al sol pasa de eso:
  depósito blanco u opaco, a la sombra o con toldo, y la batería LiFePO4 también a la sombra.
- **Algas**: depósito opaco y tapado; limpiar sondas cada 2-4 semanas.
- **Evaporación**: el nivel bajará solo; es un buen dato para el panel (y para la alarma de rellenar).
- **Vandalismo y robo**: caja con candado o tornillos de seguridad, dentro de una zona vallada del centro.
- **Lluvia y rayos**: prensaestopas hacia abajo (goteo), caja con membrana de ventilación, estructura y panel a tierra si es posible.
- **Radio**: el wAP LR8 es IP54; mejor en la fachada o una ventana con visión directa a la maqueta
  y cable de red (PoE) hacia dentro. Medir RSSI/SNR antes de fijar nada.
