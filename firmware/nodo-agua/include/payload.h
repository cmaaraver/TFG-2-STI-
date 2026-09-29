#pragma once
#include <Arduino.h>
#include <math.h>
#include "sensores.h"
#include "config.h"

// Formato versión 2, 16 bytes big-endian (ver docs/04-formato-payload.md)
static const size_t PAYLOAD_LEN = 16;

static inline void ponerU16(uint8_t* b, size_t i, uint16_t v) { b[i] = v >> 8; b[i + 1] = v & 0xFF; }

static inline uint16_t aU16(float v, float escala) {
  if (isnan(v) || v < 0) return 0xFFFF;
  float r = v * escala + 0.5f;
  return r > 65534.0f ? 65534 : (uint16_t)r;
}
static inline uint16_t aI16(float v, float escala) {
  if (isnan(v)) return 0x7FFF;
  float r = v * escala;
  if (r > 32766.0f) r = 32766.0f;
  if (r < -32767.0f) r = -32767.0f;
  return (uint16_t)(int16_t)lroundf(r);
}

static inline void construirPayload(const Medida& m, uint8_t* b) {
  uint8_t flags = 0;
  if (m.agua_presente) flags |= 0x01;
  if (m.fallo_rs485)   flags |= 0x02;
  if (m.fallo_ads)     flags |= 0x04;
  if (!isnan(m.bateria_mv) && m.bateria_mv < BATERIA_BAJA_MV) flags |= 0x08;
  if (m.temp_defecto)  flags |= 0x10;
  if (m.bomba_sin_caudal) flags |= 0x20;
  b[0] = 2;
  b[1] = flags;
  ponerU16(b, 2,  aI16(m.temperatura_c, 100));
  ponerU16(b, 4,  aU16(m.oxigeno_mgl, 100));
  ponerU16(b, 6,  aU16(m.ph, 100));
  ponerU16(b, 8,  0xFFFF);                  // reservado: antes conductividad, ya no se mide
  ponerU16(b, 10, aU16(m.nivel_mm, 1));
  ponerU16(b, 12, aU16(m.bateria_mv, 1));
  ponerU16(b, 14, aU16(m.caudal_lmin, 100));
}
