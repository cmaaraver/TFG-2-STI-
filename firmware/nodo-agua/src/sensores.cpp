// Lectura de sensores del nodo: ADS1115 (pH, nivel, batería), SEN0681 por RS485 y presencia de agua.
#include "sensores.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <ModbusMaster.h>
#include <Preferences.h>
#include "i2c_compartido.h"

#ifndef AGUA_ACTIVO_ALTO
#define AGUA_ACTIVO_ALTO 1   // TODO VERIFICAR: nivel de la salida del SEN0204 cuando detecta agua
#endif

static Adafruit_ADS1115 ads;
static ModbusMaster mb;
static bool adsOk = false;
static volatile uint32_t pulsosCaudal = 0;
static void IRAM_ATTR contarPulso() { pulsosCaudal++; }

// ---------- Calibración guardada en la flash (NVS) ----------
// Valores por defecto = los de la librería DFRobot_PH (pH V2).
struct Calibracion {
  float ph7_mv = 1500.0f;
  float ph4_mv = 2032.44f;
};
static Calibracion cal;

static void cargarCalibracion() {
  Preferences p;
  p.begin("cal", true);
  cal.ph7_mv = p.getFloat("ph7", cal.ph7_mv);
  cal.ph4_mv = p.getFloat("ph4", cal.ph4_mv);
  p.end();
}

static void guardarCalibracion() {
  Preferences p;
  p.begin("cal", false);
  p.putFloat("ph7", cal.ph7_mv);
  p.putFloat("ph4", cal.ph4_mv);
  p.end();
}

// ---------- RS485 ----------
static void antesTx()   { if (RS485_DE >= 0) digitalWrite(RS485_DE, HIGH); }
static void despuesTx() { if (RS485_DE >= 0) digitalWrite(RS485_DE, LOW); }

// Lee un float de 2 registros (big-endian según la wiki). TODO VERIFICAR si son holding (0x03) o input (0x04).
__attribute__((unused)) static bool leerFloatModbus(uint16_t reg, float& salida) {
  uint8_t r = mb.readHoldingRegisters(reg, 2);
  if (r != mb.ku8MBSuccess) return false;
  uint32_t crudo = ((uint32_t)mb.getResponseBuffer(0) << 16) | mb.getResponseBuffer(1);
  memcpy(&salida, &crudo, sizeof(float));
  return !isnan(salida);
}

// ---------- Utilidades ----------
static float mediana(float* v, int n) {
  for (int i = 1; i < n; i++) {           // ordenación por inserción (n es pequeño)
    float x = v[i]; int j = i - 1;
    while (j >= 0 && v[j] > x) { v[j + 1] = v[j]; j--; }
    v[j + 1] = x;
  }
  return (n % 2) ? v[n / 2] : (v[n / 2 - 1] + v[n / 2]) / 2.0f;
}

// Tensión en mV de un canal del ADS1115 (mediana de N_MUESTRAS)
static float leerMv(uint8_t canal) {
  if (!adsOk) return NAN;
  float v[N_MUESTRAS];
  for (int i = 0; i < N_MUESTRAS; i++) {
    i2cTomar();                           // el bus I2C se comparte con la pantalla
    v[i] = ads.computeVolts(ads.readADC_SingleEnded(canal)) * 1000.0f;
    i2cSoltar();
    delay(20);
  }
  return mediana(v, N_MUESTRAS);
}

// ---------- Conversiones ----------
// pH por dos puntos (tampones 7 y 4) con corrección de la pendiente de Nernst por temperatura
static float calcularPH(float mv, float tempC) {
  float pendiente = 3.0f / (cal.ph4_mv - cal.ph7_mv);          // pH por mV a 25 °C
  float factorT = 298.15f / (tempC + 273.15f);
  return 7.0f - (mv - cal.ph7_mv) * pendiente * factorT;
}

// Nivel: convertidor 4-20 mA → tensión en una resistencia
static float calcularNivel(float mv) {
  float mA = mv / NIVEL_R_SHUNT_OHM;
  if (mA < 3.5f) return NAN;                                   // cable cortado o sensor apagado
  float mm = (mA - 4.0f) / 16.0f * NIVEL_RANGO_MM;
  return mm < 0 ? 0 : mm;
}

// ---------- API ----------
void sensoresIniciar() {
  pinMode(PIN_EN_12V, OUTPUT);
  pinMode(PIN_EN_5V, OUTPUT);
  sensoresApagar();
  pinMode(PIN_AGUA, INPUT);
  pinMode(PIN_BOMBA, OUTPUT);
  bombaApagar();
  pinMode(PIN_CAUDAL, INPUT);
  if (RS485_DE >= 0) { pinMode(RS485_DE, OUTPUT); digitalWrite(RS485_DE, LOW); }

  i2cIniciarMutex();
  Wire.begin(I2C_SDA, I2C_SCL);
  adsOk = ads.begin(ADS_DIRECCION, &Wire);
  if (adsOk) ads.setGain(GAIN_ONE);                            // ±4,096 V

  Serial2.begin(MODBUS_BAUDIOS, SERIAL_8N1, RS485_RX, RS485_TX);
  mb.begin(MODBUS_DIRECCION, Serial2);
  mb.preTransmission(antesTx);
  mb.postTransmission(despuesTx);

  cargarCalibracion();
}

void sensoresEncender() {
  digitalWrite(PIN_EN_12V, HIGH);
  digitalWrite(PIN_EN_5V, HIGH);
}

void sensoresApagar() {
  digitalWrite(PIN_EN_12V, LOW);
  digitalWrite(PIN_EN_5V, LOW);
}

void bombaEncender() { digitalWrite(PIN_BOMBA, HIGH); }
void bombaApagar()   { digitalWrite(PIN_BOMBA, LOW); }

float medirCaudal(uint32_t duracionMs) {
  pulsosCaudal = 0;
  attachInterrupt(digitalPinToInterrupt(PIN_CAUDAL), contarPulso, FALLING);
  delay(duracionMs);
  detachInterrupt(digitalPinToInterrupt(PIN_CAUDAL));
  float hz = pulsosCaudal * 1000.0f / duracionMs;
  return hz / CAUDAL_HZ_POR_LMIN;
}

Medida sensoresMedir() {
  Medida m;
  m.fallo_ads = !adsOk;

  // 1) Oxígeno y temperatura (SEN0681)
#if MODBUS_REGISTROS_OK
  float o2, t;
  bool okO2 = leerFloatModbus(REG_OXIGENO_MGL, o2);
  bool okT  = leerFloatModbus(REG_TEMPERATURA_C, t);
  if (okO2) m.oxigeno_mgl = o2;
  if (okT)  m.temperatura_c = t;
  m.fallo_rs485 = !(okO2 && okT);
#else
  m.fallo_rs485 = true;                                        // registros sin configurar todavía
#endif

  float tComp = isnan(m.temperatura_c) ? TEMP_DEFECTO_C : m.temperatura_c;
  m.temp_defecto = isnan(m.temperatura_c);

  // 2) Analógicos
  float mvPH = leerMv(CANAL_PH);
  float mvNivel = leerMv(CANAL_NIVEL);
  float mvBat = leerMv(CANAL_BATERIA);

  if (!isnan(mvPH))    m.ph = calcularPH(mvPH, tComp);
  if (!isnan(mvNivel)) m.nivel_mm = calcularNivel(mvNivel);
  if (!isnan(mvBat))   m.bateria_mv = mvBat * DIVISOR_BATERIA;

  // 3) Presencia de agua (nivel mínimo del depósito)
  m.agua_presente = (digitalRead(PIN_AGUA) == (AGUA_ACTIVO_ALTO ? HIGH : LOW));

  if (m.ph < 0 || m.ph > 14) m.ph = NAN;                       // lectura imposible = sin dato
  return m;
}

// ---------- Modo calibración (monitor serie a 115200) ----------
static void imprimir(const Medida& m) {
  Serial.printf("T=%.2f C  O2=%.2f mg/L  pH=%.2f  nivel=%.0f mm  bat=%.0f mV  agua=%d  rs485_err=%d\n",
                m.temperatura_c, m.oxigeno_mgl, m.ph, m.nivel_mm, m.bateria_mv,
                m.agua_presente, m.fallo_rs485);
}

void modoCalibracion() {
  Serial.println("\n=== MODO CALIBRACION ===");
  Serial.println("Comandos: leer | bomba | ph7 | ph4 | ver | reset | salir");
  sensoresEncender();
  Serial.println("Esperando calentamiento de sensores (60 s)...");
  delay(T_CALENTAMIENTO_MS);

  while (true) {
    if (!Serial.available()) { delay(50); continue; }
    String c = Serial.readStringUntil('\n');
    c.trim();
    Medida m = sensoresMedir();

    if (c == "leer") {
      imprimir(m);
    } else if (c == "bomba") {
      bombaEncender(); delay(5000);
      Serial.printf("Caudal: %.2f L/min\n", medirCaudal(T_MEDIDA_CAUDAL_MS));
      bombaApagar();
    } else if (c == "ph7") {
      cal.ph7_mv = leerMv(CANAL_PH); guardarCalibracion();
      Serial.printf("pH7 guardado: %.1f mV\n", cal.ph7_mv);
    } else if (c == "ph4") {
      cal.ph4_mv = leerMv(CANAL_PH); guardarCalibracion();
      Serial.printf("pH4 guardado: %.1f mV\n", cal.ph4_mv);
    } else if (c == "ver") {
      Serial.printf("ph7=%.1f mV  ph4=%.1f mV\n", cal.ph7_mv, cal.ph4_mv);
    } else if (c == "reset") {
      cal = Calibracion(); guardarCalibracion(); Serial.println("Calibracion por defecto");
    } else if (c == "salir") {
      bombaApagar(); sensoresApagar(); Serial.println("Quitar el puente MODO_CAL y reiniciar"); return;
    } else {
      Serial.println("Comando no valido");
    }
  }
}
