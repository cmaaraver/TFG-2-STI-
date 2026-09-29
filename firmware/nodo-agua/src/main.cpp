// Nodo de calidad del agua — LoRaWAN 1.1 (OTAA, EU868, clase A) con RadioLib.
// Ciclo: despertar → encender sensores y bomba → join/restaurar sesión → medir caudal →
//        parar bomba → agua quieta → medir → enviar → dormir.
// La pantalla OLED enseña el logo de Los Viveros, la fase del ciclo y un temporizador
// con lo que tarda el envío por LoRa.
// Persistencia de sesión basada en el ejemplo "LoRaWAN_ESP32" / persistencia de RadioLib.
// TODO VERIFICAR la API con los ejemplos de la versión de RadioLib instalada.
#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>
#include <Preferences.h>
#include "config.h"
#include "secrets.h"
#include "sensores.h"
#include "payload.h"
#include "pantalla.h"

#if defined(RADIO_SX1276)
SX1276 radio = new Module(LORA_CS, LORA_DIO0, LORA_RST, LORA_DIO1);
#else
SX1262 radio = new Module(LORA_CS, LORA_DIO1, LORA_RST, LORA_BUSY);
#endif
LoRaWANNode node(&radio, &EU868);

// Variables que sobreviven al deep sleep (memoria RTC)
RTC_DATA_ATTR uint8_t  sesionLW[RADIOLIB_LORAWAN_SESSION_BUF_SIZE];
RTC_DATA_ATTR bool     haySesion    = false;
RTC_DATA_ATTR uint16_t intervaloMin = INTERVALO_ENVIO_MIN_DEF;
RTC_DATA_ATTR uint32_t ciclo        = 0;

static void dormir(uint32_t segundos) {
  bombaApagar();
  sensoresApagar();
  pantallaDormir();
  radio.sleep();
  Serial.printf("Durmiendo %lu s\n", (unsigned long)segundos);
  Serial.flush();
  esp_sleep_enable_timer_wakeup((uint64_t)segundos * 1000000ULL);
  esp_deep_sleep_start();
}

// Join OTAA o restauración de la sesión guardada
static bool activarLoRaWAN() {
  uint8_t appKey[] = LW_APP_KEY;
  uint8_t nwkKey[] = LW_NWK_KEY;
  node.beginOTAA(LW_JOIN_EUI, LW_DEV_EUI, nwkKey, appKey);

  Preferences p;
  p.begin("lorawan", false);
  if (p.isKey("nonces")) {                       // los nonces se guardan en flash (no se pueden repetir)
    uint8_t buf[RADIOLIB_LORAWAN_NONCES_BUF_SIZE];
    p.getBytes("nonces", buf, sizeof(buf));
    node.setBufferNonces(buf);
  }
  if (haySesion) node.setBufferSession(sesionLW);

  int16_t st = node.activateOTAA();
  // Guardar siempre los nonces: cada intento de join gasta un DevNonce
  p.putBytes("nonces", node.getBufferNonces(), RADIOLIB_LORAWAN_NONCES_BUF_SIZE);
  p.end();

  if (st == RADIOLIB_LORAWAN_NEW_SESSION)      { Serial.println("Join OK (sesion nueva)"); return true; }
  if (st == RADIOLIB_LORAWAN_SESSION_RESTORED) { Serial.println("Sesion restaurada");       return true; }
  Serial.printf("Fallo de join: %d\n", st);
  haySesion = false;
  return false;
}

static void procesarDownlink(const uint8_t* d, size_t n) {
  if (n >= 3 && d[0] == 0x01) {                  // cambiar intervalo de envío
    uint16_t m = (d[1] << 8) | d[2];
    if (m >= 5 && m <= 120) { intervaloMin = m; Serial.printf("Nuevo intervalo: %u min\n", m); }
  }
}

void setup() {
  uint32_t t0 = millis();
  Serial.begin(115200);
  delay(200);
  ciclo++;
  Serial.printf("\n--- Nodo calidad agua, ciclo %lu ---\n", (unsigned long)ciclo);

  sensoresIniciar();
  pantallaIniciar(ciclo);

  pinMode(PIN_MODO_CAL, INPUT);
  if (digitalRead(PIN_MODO_CAL) == LOW) {
    pantallaMensaje("MODO CALIBRACION", "Monitor serie 115200");
    modoCalibracion();
    while (true) delay(1000);
  }

  sensoresEncender();                            // empiezan a calentar mientras se hace el join
  bombaEncender();                               // mover el agua para que las sondas no vean agua estancada
  pantallaFase("Bomba y sensores ON");

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  int16_t st = radio.begin();
  if (st != RADIOLIB_ERR_NONE) {
    Serial.printf("Error de radio: %d\n", st);
    pantallaMensaje("Error de radio", "Revisar placa");
    delay(T_PANTALLA_RESULTADO_MS);
    dormir(T_REINTENTO_JOIN_S);
  }

  pantallaFase("Conectando LoRaWAN");
  if (!activarLoRaWAN()) {
    pantallaMensaje("Join fallido", "Reintento en 5 min");
    delay(T_PANTALLA_RESULTADO_MS);
    dormir(T_REINTENTO_JOIN_S);
  }
  pantallaFase("Bombeando agua");

  // Medir caudal en los últimos segundos de bomba y pararla
  while (millis() - t0 < T_BOMBA_MS - T_MEDIDA_CAUDAL_MS) delay(100);
  pantallaFase("Midiendo caudal");
  float caudal = medirCaudal(T_MEDIDA_CAUDAL_MS);
  bombaApagar();

  // Agua quieta y sensores calientes antes de leer (el motor mete ruido en el pH)
  pantallaFase("Agua en reposo");
  delay(T_REPOSO_AGUA_MS);
  while (millis() - t0 < T_CALENTAMIENTO_MS) delay(100);

  pantallaFase("Leyendo sensores");
  Medida m = sensoresMedir();
  sensoresApagar();
  m.caudal_lmin = caudal;
  m.bomba_sin_caudal = caudal < CAUDAL_MINIMO_LMIN;
  Serial.printf("T=%.2f O2=%.2f pH=%.2f nivel=%.0f bat=%.0f caudal=%.2f agua=%d\n",
                m.temperatura_c, m.oxigeno_mgl, m.ph, m.nivel_mm, m.bateria_mv,
                m.caudal_lmin, m.agua_presente);

  uint8_t payload[PAYLOAD_LEN];
  construirPayload(m, payload);

  uint8_t bajada[32];
  size_t lenBajada = 0;
  LoRaWANEvent_t evSubida, evBajada;
  // Temporizador del envío: incluye la transmisión y las dos ventanas de recepción
  // (RX1 a 1 s y RX2 a 2 s en EU868) en las que el servidor puede contestar.
  pantallaEnviando();
  uint32_t tEnvio = millis();
  st = node.sendReceive(payload, PAYLOAD_LEN, FPORT_DATOS, bajada, &lenBajada, false, &evSubida, &evBajada);
  uint32_t msEnvio = millis() - tEnvio;
  uint32_t msAire = node.getLastToA();                         // solo la transmisión, en ms
  uint8_t sf = evSubida.datarate <= 5 ? 12 - evSubida.datarate : 7;   // EU868: DR0 = SF12 ... DR5 = SF7
  bool envioOk = st >= RADIOLIB_ERR_NONE;

  if (!envioOk) {
    Serial.printf("Error al enviar: %d\n", st);
  } else {
    Serial.printf("Uplink enviado: fcnt=%lu SF%u, %lu ms en el aire, %lu ms en total\n",
                  (unsigned long)evSubida.fCnt, sf, (unsigned long)msAire, (unsigned long)msEnvio);
    if (st > 0 && lenBajada > 0 && evBajada.fPort == FPORT_CONFIG) procesarDownlink(bajada, lenBajada);
  }
  pantallaResultado(envioOk, msEnvio, msAire, sf, intervaloMin);

  // Guardar la sesión para el siguiente despertar
  memcpy(sesionLW, node.getBufferSession(), RADIOLIB_LORAWAN_SESSION_BUF_SIZE);
  haySesion = true;

  delay(T_PANTALLA_RESULTADO_MS);                                // que dé tiempo a leer el resultado
  uint32_t transcurrido = (millis() - t0) / 1000;
  uint32_t periodo = (uint32_t)intervaloMin * 60;
  dormir(periodo > transcurrido ? periodo - transcurrido : 60);
}

void loop() {}  // no se usa: todo ocurre en setup() y luego deep sleep
