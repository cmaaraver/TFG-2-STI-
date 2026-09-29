#pragma once
#include <Arduino.h>

// Resultado de un ciclo de medida. NAN = sin dato.
struct Medida {
  float temperatura_c = NAN;
  float oxigeno_mgl   = NAN;
  float ph            = NAN;
  float ec_uscm       = NAN;
  float nivel_mm      = NAN;
  float bateria_mv    = NAN;
  float caudal_lmin   = NAN;
  bool  bomba_sin_caudal = false;
  bool  agua_presente = false;
  bool  fallo_rs485   = false;
  bool  fallo_ads     = false;
  bool  temp_defecto  = false;
};

void sensoresIniciar();
void sensoresEncender();
void sensoresApagar();
void bombaEncender();
void bombaApagar();
float medirCaudal(uint32_t duracionMs);   // L/min, contando pulsos durante duracionMs
Medida sensoresMedir();
void modoCalibracion();   // menú por el monitor serie (puente MODO_CAL a GND)
