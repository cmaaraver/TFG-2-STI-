// Pantalla OLED SSD1306 128x64 con U8g2 (https://github.com/olikraus/u8g2).
// Distribución (píxeles):
//   0-22  logo de Los Viveros
//   33    línea pequeña: qué está haciendo el nodo
//   36-52 número grande: temporizador
//   63    línea pequeña: detalle (ciclo, tiempo en el aire, próximo envío)
#include "pantalla.h"
#include "config.h"
#include "logo.h"
#include "i2c_compartido.h"
#include <U8g2lib.h>

#if PANTALLA_ACTIVA

// Placa sin pin de reset para la OLED (utilities.h de LilyGO: OLED_RST = UNUSED_PIN)
static U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE, I2C_SCL, I2C_SDA);

enum Estado { FASE, ENVIANDO, RESULTADO, MENSAJE };

// Lo que se dibuja. Lo escribe el programa principal y lo lee la tarea de refresco.
static volatile Estado estado = FASE;
static char texto1[24] = "";
static char texto2[24] = "";
static volatile uint32_t tInicioCiclo = 0;
static volatile uint32_t tInicioEnvio = 0;
static volatile uint32_t msResultado = 0;
static TaskHandle_t tarea = nullptr;
static uint32_t cicloActual = 0;

// Milisegundos → "1,23 s"
static void formatoSegundos(char* buf, size_t n, uint32_t ms) {
  snprintf(buf, n, "%lu,%02lu s", (unsigned long)(ms / 1000), (unsigned long)((ms % 1000) / 10));
}

static void dibujar() {
  char grande[16];
  oled.clearBuffer();
  oled.drawXBMP(0, 0, LOGO_ANCHO, LOGO_ALTO, LOGO_VIVEROS);
  oled.drawHLine(0, LOGO_ALTO + 2, 128);

  oled.setFont(u8g2_font_6x10_tf);
  switch (estado) {
    case FASE:
      oled.drawUTF8(0, 34, texto1);
      snprintf(grande, sizeof(grande), "%lu s", (unsigned long)((millis() - tInicioCiclo) / 1000));
      oled.drawUTF8(0, 63, texto2);
      break;
    case ENVIANDO:
      oled.drawUTF8(0, 34, "Enviando por LoRa...");
      formatoSegundos(grande, sizeof(grande), millis() - tInicioEnvio);   // cuenta en directo
      oled.drawUTF8(0, 63, texto2);
      break;
    case RESULTADO:
      oled.drawUTF8(0, 34, texto1);
      formatoSegundos(grande, sizeof(grande), msResultado);               // tiempo final, fijo
      oled.drawUTF8(0, 63, texto2);
      break;
    case MENSAJE:
      oled.drawUTF8(0, 40, texto1);
      oled.drawUTF8(0, 56, texto2);
      grande[0] = '\0';
      break;
  }
  if (grande[0]) {
    oled.setFont(u8g2_font_logisoso16_tr);
    int ancho = oled.getUTF8Width(grande);
    oled.drawUTF8((128 - ancho) / 2, 52, grande);
  }
  oled.sendBuffer();
}

// Tarea de refresco: redibuja cada 100 ms (el temporizador se mueve solo)
static void tareaPantalla(void*) {
  for (;;) {
    i2cTomar();
    dibujar();
    i2cSoltar();
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

void pantallaIniciar(uint32_t ciclo) {
  cicloActual = ciclo;
  tInicioCiclo = millis();
  i2cTomar();
  oled.begin();                    // usa el mismo bus I2C que el ADS1115 (ya iniciado)
  oled.setPowerSave(0);
  oled.enableUTF8Print();
  i2cSoltar();
  snprintf(texto1, sizeof(texto1), "Arrancando");
  snprintf(texto2, sizeof(texto2), "Ciclo %lu", (unsigned long)ciclo);
  estado = FASE;
  xTaskCreatePinnedToCore(tareaPantalla, "pantalla", 4096, nullptr, 1, &tarea, 0);
}

void pantallaFase(const char* texto) {
  snprintf(texto1, sizeof(texto1), "%s", texto);
  snprintf(texto2, sizeof(texto2), "Ciclo %lu", (unsigned long)cicloActual);
  estado = FASE;
}

void pantallaEnviando() {
  snprintf(texto2, sizeof(texto2), "Ciclo %lu", (unsigned long)cicloActual);
  tInicioEnvio = millis();
  estado = ENVIANDO;
}

void pantallaResultado(bool ok, uint32_t msEnvio, uint32_t msAire, uint8_t sf, uint16_t proximoMin) {
  msResultado = msEnvio;
  if (ok) {
    snprintf(texto1, sizeof(texto1), "Enviado OK  SF%u", sf);
    snprintf(texto2, sizeof(texto2), "Aire %lums Prox %umin", (unsigned long)msAire, proximoMin);
  } else {
    snprintf(texto1, sizeof(texto1), "Error al enviar");
    snprintf(texto2, sizeof(texto2), "Reintento en %u min", proximoMin);
  }
  estado = RESULTADO;
}

void pantallaMensaje(const char* linea1, const char* linea2) {
  snprintf(texto1, sizeof(texto1), "%s", linea1);
  snprintf(texto2, sizeof(texto2), "%s", linea2);
  estado = MENSAJE;
}

void pantallaDormir() {
  if (tarea) {
    i2cTomar();                    // esperar a que termine el dibujo en curso
    vTaskDelete(tarea);
    tarea = nullptr;
    dibujar();                     // último estado, fijo
#if PANTALLA_APAGAR_AL_DORMIR
    oled.setPowerSave(1);          // pantalla apagada: casi no gasta mientras el ESP32 duerme
#endif
    i2cSoltar();
  }
}

#else  // sin pantalla: funciones vacías

void pantallaIniciar(uint32_t) {}
void pantallaFase(const char*) {}
void pantallaEnviando() {}
void pantallaResultado(bool, uint32_t, uint32_t, uint8_t, uint16_t) {}
void pantallaMensaje(const char*, const char*) {}
void pantallaDormir() {}

#endif
