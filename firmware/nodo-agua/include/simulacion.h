#pragma once
// Datos simulados de todos los sensores, para probar la web sin tener los sensores conectados.
// Solo se usa con el entorno lilygo_t3_simulado (define SIMULAR_SENSORES).
// Para quitar la simulación basta con grabar otro entorno: el código real no cambia.
#include <Arduino.h>
#include "sensores.h"

#define INTERVALO_SIMULADO_MIN 2   // en simulación se envía cada 2 min para ver la web moverse antes

// Devuelve una medida inventada pero realista que va cambiando de un ciclo a otro
Medida simularMedida(uint32_t ciclo, uint16_t intervaloMin);
