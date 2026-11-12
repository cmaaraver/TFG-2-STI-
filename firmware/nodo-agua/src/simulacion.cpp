// Simulación de sensores (entorno lilygo_t3_simulado). Fuera de ese entorno este archivo no compila nada.
#ifdef SIMULAR_SENSORES
#include "simulacion.h"
#include "config.h"
#include <math.h>

// Ruido aleatorio entre -a y +a (esp_random usa el generador de números aleatorios del ESP32)
static float ruido(float a) {
  return ((esp_random() % 2001) / 1000.0f - 1.0f) * a;
}

Medida simularMedida(uint32_t ciclo, uint16_t intervaloMin) {
  Medida m;
  // Hora "del día" simulada a partir del número de ciclo: así las curvas suben y bajan
  // como lo harían en un día real (máximo de temperatura por la tarde).
  float horas = ciclo * intervaloMin / 60.0f;
  float dia = sinf(2.0f * PI * (horas - 9.0f) / 24.0f);       // -1 de madrugada, +1 por la tarde

  m.temperatura_c = 21.0f + 3.0f * dia + ruido(0.15f);          // 18-24 °C
  // El oxígeno disuelto baja cuando el agua se calienta (≈ 9,5 mg/L a 18 °C, ≈ 8,3 a 24 °C)
  m.oxigeno_mgl = 8.9f - 0.2f * (m.temperatura_c - 21.0f) + ruido(0.08f);
  m.ph = 7.5f + 0.15f * dia + ruido(0.03f);                     // 7,3-7,7
  // Nivel: oscila despacio alrededor de 420 mm (evaporación y rellenos)
  m.nivel_mm = 420.0f + 25.0f * sinf(2.0f * PI * horas / 30.0f) + ruido(2.0f);
  // Batería LiFePO4 de 12,8 V: sube de día con el panel y baja de noche
  m.bateria_mv = 13150.0f + 150.0f * dia + ruido(15.0f);

  // Caudal de la bomba ≈ 4 L/min; uno de cada 12 ciclos la bomba está "parada" para probar el aviso
  m.caudal_lmin = (ciclo % 12 == 0) ? 0.0f : 4.1f + ruido(0.25f);
  m.bomba_sin_caudal = m.caudal_lmin < CAUDAL_MINIMO_LMIN;

  m.agua_presente = m.nivel_mm > 100.0f;                        // con este nivel siempre hay agua
  m.fallo_rs485 = false;
  m.fallo_ads = false;
  m.temp_defecto = false;
  return m;
}
#endif
