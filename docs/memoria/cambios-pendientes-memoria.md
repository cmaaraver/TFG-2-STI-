# Cambios pendientes de meter en la memoria (Word)

La memoria en Word (`Memoria_TFG_Calidad_Agua_LoRaWAN.docx`) se regeneró por última vez el **19-11-2026** (PR 20).
Aquí se apunta todo lo que ha cambiado después, para meterlo de una vez en el documento final. Cuando se pase al
Word (scripts de `fuentes-word/`), se tacha la línea o se borra el apartado.

| Fecha | PR | Qué cambió | Dónde va en la memoria |
|---|---|---|---|
| 24-11-2026 | 21 | Guía de montaje cable a cable (`docs/12-guia-montaje.md` y PDF) con el dibujo `docs/img/montaje-visual.png` | 2.x Descripción del montaje · Plano de conexionado (sustituye o acompaña a `plano-conexionado.png`) |
| 24-11-2026 | 22 | El montaje pasa a la **protoboard pegada en la caja estanca**: línea + de arriba 12 V, + de abajo 3V3, una columna por señal. SEN0204 con su **placa adaptadora** (rojo/negro/verde) y divisor 27k/10k. El conversor 4-20 mA es el **SEN0262** que viene en la caja del KIT0139 | Memoria descriptiva (nodo y sensores) · Pliego (montaje) · Presupuesto: el SEN0262 no se compra aparte |
| 24-11-2026 | 23 y 24 | **Pines reales** de la T3 V1.6.1 según el esquema oficial `T3_V1.6.1.pdf` y la serigrafía de nuestra placa: GPIO36 y GPIO39 salen como **S_VP** y **S_VN**; las tiras de pines vienen **sin soldar** | Tabla de pines del nodo · Anexo de programación |
| 25-11-2026 | 25 | Firmware real revisado: corregido que GPIO4 y GPIO25 se usaban a la vez como conmutadores y como presencia de agua / DE del RS485. Comandos nuevos del modo calibración: `mv`, `nivel0`, `sal`, `sal0`, `o2_100`, `o2_cero`. Herramienta `herramientas/calibrar.py` | Anexo de programación (firmware) · Problemas encontrados |
| 25-11-2026 | 25 | Guía de calibración (`docs/13-guia-calibracion.md`): pH en dos puntos, cero del nivel guardado en la flash, SEN0204, salinidad a 0 y punto del 100 % del oxígeno (registros 0x1020 y 0x1010 de la wiki del SEN0680) | Anexo de cálculos / calibración · Pruebas |
| 25-11-2026 | 26 | Checklist visual de calibración para el taller (`docs/14-checklist-calibracion.md` y PDF) con 6 dibujos `docs/img/calib-*.png` y hoja de resultados | Anexo de pruebas (la hoja de resultados rellena es la prueba de la fase 2) · Figuras del puente IO15 y del pH en la memoria descriptiva |

## Datos que saldrán de la calibración (para los [COMPLETAR] del Word)

- mV del pH en los tampones 7 y 4 y lecturas de comprobación (fase 2, criterio ±0,1 pH).
- Cero del nivel y tabla de 5 en 5 L; `alturaLlenoMm` real del bidón.
- Litros a los que el SEN0204 cambia a "hay agua".
- Con el RS485: salinidad de fábrica del SEN0681, temperatura frente al termómetro y O2 tras calibrar.
