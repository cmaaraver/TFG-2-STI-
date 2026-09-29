#pragma once
// =====================================================================
//  Configuración del nodo. Todo lo que dependa del hardware está aquí.
//  IMPORTANTE: verificar los pines con el pinout oficial de LILYGO.
// =====================================================================

#if defined(PLACA_LILYGO_T3_V1_6_1)
  // LILYGO T3 V1.6.1 (ESP32 + SX1276)
  #define RADIO_SX1276
  #define LORA_SCK   5
  #define LORA_MISO  19
  #define LORA_MOSI  27
  #define LORA_CS    18
  #define LORA_RST   23
  #define LORA_DIO0  26
  #define LORA_DIO1  33
  #define I2C_SDA    21
  #define I2C_SCL    22
  #define RS485_TX   13
  #define RS485_RX   14
  #define RS485_DE   -1     // -1 si el adaptador RS485 cambia de dirección solo
  #define PIN_EN_12V 4
  #define PIN_EN_5V  25
  #define PIN_AGUA   39     // solo entrada, pull-up externa
  #define PIN_MODO_CAL 36   // solo entrada, pull-up externa; a GND = calibración
  #define PIN_BOMBA  2      // puerta del N-MOSFET de la bomba (pull-down 100k: GPIO2 debe estar a 0 al arrancar)
  #define PIN_CAUDAL 34     // solo entrada; pulsos del caudalímetro a través de divisor 5 V → 3,3 V
#elif defined(PLACA_LILYGO_T3S3_SX1262)
  // LILYGO T3-S3 (ESP32-S3 + SX1262) — TODO VERIFICAR todos los pines con el pinout oficial
  #define RADIO_SX1262
  #define LORA_SCK   5
  #define LORA_MISO  3
  #define LORA_MOSI  6
  #define LORA_CS    7
  #define LORA_RST   8
  #define LORA_DIO1  33
  #define LORA_BUSY  34
  #define I2C_SDA    18
  #define I2C_SCL    17
  #error "T3-S3: asignar RS485_TX/RX, PIN_EN_12V, PIN_EN_5V, PIN_AGUA y PIN_MODO_CAL tras revisar el pinout y borrar esta linea"
#else
  #error "Define la placa en platformio.ini (PLACA_LILYGO_...)"
#endif

// ---------- Tiempos ----------
#define INTERVALO_ENVIO_MIN_DEF  15        // minutos entre envíos (cambiable por downlink)
#define T_CALENTAMIENTO_MS       60000UL   // SEN0681: tiempo de respuesta <= 60 s
#define N_MUESTRAS               15        // muestras por medida (se usa la mediana)
#define T_REINTENTO_JOIN_S       300       // si falla el join, reintentar en 5 min
#define T_BOMBA_MS               45000UL   // recirculación antes de medir (renueva el agua en las sondas)
#define T_MEDIDA_CAUDAL_MS       10000UL   // últimos 10 s de bomba: contar pulsos
#define T_REPOSO_AGUA_MS         5000UL    // bomba parada y agua quieta antes de leer pH/EC

// ---------- Caudalímetro de efecto Hall ----------
#define CAUDAL_HZ_POR_LMIN  7.5f   // TODO VERIFICAR con el modelo comprado (YF-S201: F = 7,5 × Q)
#define CAUDAL_MINIMO_LMIN  0.3f   // por debajo con la bomba encendida = bomba atascada o sin agua

// ---------- LoRaWAN ----------
#define FPORT_DATOS   1
#define FPORT_CONFIG  10

// ---------- SEN0681 (Modbus RTU) ----------
// TODO VERIFICAR en la wiki de DFRobot (SEN0681 → Reference → Register):
// dirección, baudios, registros y formato del float (big-endian según la wiki).
#define MODBUS_DIRECCION    1
#define MODBUS_BAUDIOS      9600
#define MODBUS_REGISTROS_OK 0          // poner a 1 cuando se rellenen los registros de abajo
#define REG_OXIGENO_MGL     0x0000     // TODO VERIFICAR
#define REG_TEMPERATURA_C   0x0000     // TODO VERIFICAR
#define REG_SALINIDAD       0x0000     // TODO VERIFICAR (poner 0 ‰ si el agua es dulce)

// ---------- ADS1115 ----------
#define ADS_DIRECCION 0x48
#define CANAL_PH      0
#define CANAL_EC      1
#define CANAL_NIVEL   2
#define CANAL_BATERIA 3

// ---------- Conversiones ----------
#define DIVISOR_BATERIA   ((100.0f + 22.0f) / 22.0f)  // 100k arriba, 22k abajo
#define BATERIA_BAJA_MV   12400                      // LiFePO4 ~20 % de carga
#define NIVEL_R_SHUNT_OHM 120.0f    // TODO VERIFICAR con el convertidor 4-20 mA usado
#define NIVEL_RANGO_MM    5000.0f   // TODO VERIFICAR rango del KIT0139 comprado
#define TEMP_DEFECTO_C    25.0f     // si no hay temperatura del SEN0681

// Sonda de conductividad: 1 = K=1 (fórmula DFRobot_EC), 10 = K=10 (usar fórmula de DFRobot_EC10)
#define EC_TIPO_SONDA 1
