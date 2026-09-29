// Construye el payload con el MISMO código del firmware (payload.h) para varios casos
// y lo imprime en hexadecimal, una línea por caso: nombre;hex
#include <cstdio>
#include "payload.h"

static void imprimir(const char* nombre, const Medida& m) {
  uint8_t b[PAYLOAD_LEN];
  construirPayload(m, b);
  printf("%s;", nombre);
  for (size_t i = 0; i < PAYLOAD_LEN; i++) printf("%02x", b[i]);
  printf("\n");
}

int main() {
  Medida normal;
  normal.temperatura_c = 21.37f; normal.oxigeno_mgl = 8.42f; normal.ph = 7.61f;
  normal.nivel_mm = 412; normal.bateria_mv = 13210; normal.caudal_lmin = 3.85f;
  normal.agua_presente = true;
  imprimir("normal", normal);

  Medida frio = normal;                  // temperatura negativa y batería baja
  frio.temperatura_c = -2.5f; frio.bateria_mv = 12100;
  imprimir("frio_bateria_baja", frio);

  Medida fallos;                         // todo sin dato (NAN) y todos los fallos
  fallos.fallo_rs485 = true; fallos.fallo_ads = true; fallos.temp_defecto = true;
  fallos.bomba_sin_caudal = true;
  imprimir("sin_datos", fallos);
  return 0;
}
