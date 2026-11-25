# Cambios pendientes de meter en la memoria (Word)

La memoria en Word (`Memoria_TFG_Calidad_Agua_LoRaWAN.docx`) se regeneró el **25-11-2026** (PR 27 y PR 28) con
todos los cambios de los PR 21 a 26: protoboard en la caja estanca (plano 3B), pines S_VP/S_VN, SEN0262, placa del
SEN0204, firmware real, comandos del modo calibración, checklist visual con los dibujos `calib-*.png` y hoja de
resultados en el apartado 5.6. **No queda nada pendiente de los PR hasta el 26.**

Si cambia algo más, se apunta aquí en una tabla (fecha, PR, qué cambió, dónde va en la memoria) hasta la próxima
regeneración.

## Datos que saldrán de la calibración (para los [COMPLETAR] del Word)

- mV del pH en los tampones 7 y 4 y lecturas de comprobación (fase 2, criterio ±0,1 pH).
- Cero del nivel y tabla de 5 en 5 L; `alturaLlenoMm` real del bidón.
- Litros a los que el SEN0204 cambia a "hay agua".
- Con el RS485: salinidad de fábrica del SEN0681, temperatura frente al termómetro y O2 tras calibrar.
