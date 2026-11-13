#pragma once
// =====================================================================
//  Configuración del nodo. Todo lo que dependa del hardware está aquí.
//  Pines de la placa sacados de la librería oficial de LilyGO:
//  https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series → examples/*/utilities.h
// =====================================================================

#if defined(PLACA_LILYGO_T3_V1_6_1)
  // LILYGO T3 V1.6.1 (ESP32 + SX1276). utilities.h de LilyGO, bloque T3_V1_6_SX1276:
  // radio 5/19/27/18/23/26/33, I2C 21/22 (OLED SSD1306 en 0x3C, sin pin de reset),
  // LED en GPIO 25 y lector microSD en GPIO 2/13/14/15 (NO poner tarjeta SD: usamos 13 y 14).
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
  #define PIN_AGUA   39     // solo entrada; SEN0204 por divisor 10k/20k (su salida da 5 V)
  #define PIN_MODO_CAL 36   // solo entrada, pull-up externa; a GND = calibración
  // GPIO12 se queda libre: la bomba va aparte, con su propia alimentación (decisión de 2026-10-26).
  // Es pin de arranque y tiene que estar a 0 al encender, así que no se le conecta nada.
                            // No se usa GPIO2 porque es la línea MISO del lector microSD de la placa.
  #define PIN_CAUDAL 34     // solo entrada; pulsos del caudalímetro a través de divisor 5 V → 3,3 V
  #define PIN_MODO_CAL_PULLUP 0  // 0 = pull-up externa de 10k (GPIO36 no tiene pull-up interna)

  #ifdef SIN_ADS1115
  // Montaje simple (2026-11-12, revisado 2026-11-13): todo se lee directamente con la LILYGO, sin ADS1115, sin
  // aislador DFR0504 y sin medir la batería. LILYGO por USB (cargador de 5 V con respaldo) y sensores con una fuente
  // de 12 V de PC. Esquema: docs/img/conexionado-simple.png
  // El pH y el nivel se leen con el ADC1 del ESP32, que funciona aunque esté la radio LoRa.
  // GPIO36 y GPIO39 son ADC1_CH0 y ADC1_CH3 (hoja de datos del ESP32, tabla "ADC"), solo entrada.
  // Por eso la presencia de agua pasa a GPIO4 y el puente de calibración a GPIO15.
    #undef  PIN_AGUA
    #undef  PIN_MODO_CAL
    #undef  PIN_MODO_CAL_PULLUP
    #define PIN_PH        36   // salida de la placa del pH (0-3,0 V, wiki DFRobot SEN0169-V2)
    #define PIN_NIVEL     39   // Signal del conversor 4-20 mA del KIT0139 (0,48-2,40 V con 120 Ω)
    #define PIN_AGUA      4    // SEN0204 alimentado a 12 V (admite 5-24 V, wiki DFRobot SEN0204; su salida alta = VCC):
                               // divisor 27k en serie / 10k a GND → 12 V × 10/37 ≈ 3,2 V. No se alimenta del pin 5V
                               // de la LILYGO porque por USB da ~4,7 V (diodo BAT20J del esquema T3_V1.6) y pide 5 V mínimo.
                               // GPIO4 es DAT1 del lector microSD (sin tarjeta queda libre; su pull-up no está montada)
    #undef  PIN_CAUDAL
    #define PIN_CAUDAL    34   // YF-S201 alimentado a 12 V (4,5-24 V según su ficha). La ficha no dice qué salida tiene,
                               // así que va por un diodo 1N4148 (raya hacia el sensor) + pull-up de 10k a 3V3:
                               // pulsos de ~0,6 V a 3,3 V valga lo que valga la salida. GPIO34 no tiene pull-up interna.
    #define PIN_MODO_CAL  15   // puente a GND al arrancar = calibración. GPIO15 es pin de arranque: a 0 solo
                               // calla los mensajes de arranque del ESP32, así que el puente no estorba
    #define PIN_MODO_CAL_PULLUP 1  // pull-up interna: no hace falta resistencia
    #undef  RS485_DE
    #define RS485_DE      25   // DE+RE de un módulo MAX485. Con un módulo de dirección automática este pin
                               // se queda sin conectar y no molesta (solo parpadea el LED de la placa al enviar)
  #endif
#elif defined(PLACA_LILYGO_T3S3_SX1262)
  // LILYGO T3-S3 (ESP32-S3 + SX1262) — TODO VERIFICAR todos los pines con el pinout oficial
  #define RADIO_SX1262
  #define LORA_SCK   5
  #define LORA_MISO  3
  #define LORA_MOSI  6
  #define LORA_CS    7
  #define LORA_RST   8
  #define LORA_BUSY  34
  #define I2C_SDA    18
  #define I2C_SCL    17
  #define LORA_DIO1  33       // utilities.h de LilyGO, bloque T3_S3_V1_2 con USING_SX1262
  #error "T3-S3: asignar RS485_TX/RX, PIN_EN_12V, PIN_EN_5V, PIN_AGUA y PIN_MODO_CAL tras revisar el pinout y borrar esta linea"
#else
  #error "Define la placa en platformio.ini (PLACA_LILYGO_...)"
#endif

// ---------- Tiempos ----------
#define INTERVALO_ENVIO_MIN_DEF  15        // minutos entre envíos (cambiable por downlink)
#define T_CALENTAMIENTO_MS       60000UL   // SEN0681: tiempo de respuesta <= 60 s
#define N_MUESTRAS               15        // muestras por medida (se usa la mediana)
#define T_REINTENTO_JOIN_S       300       // si falla el join, reintentar en 5 min
#define T_MEDIDA_CAUDAL_MS       10000UL   // contar pulsos del caudalímetro durante 10 s

// ---------- Caudalímetro de efecto Hall ----------
#define CAUDAL_HZ_POR_LMIN  7.5f   // TODO VERIFICAR con el modelo comprado (YF-S201: F = 7,5 × Q)
#define CAUDAL_MINIMO_LMIN  0.3f   // por debajo = la bomba (que va aparte) está parada, atascada o sin agua

// ---------- LoRaWAN ----------
#define FPORT_DATOS   1
#define FPORT_CONFIG  10

// ---------- SEN0681 (Modbus RTU) ----------
// Fuente: wiki DFRobot del SEN0680 (versión de agua dulce del mismo sensor),
// https://wiki.dfrobot.com/sen0680/docs/21672 → "Register". Por defecto: dirección 1, 4800 baudios, 8N1.
// Cada medida es un float big-endian en 2 registros, que se leen con 0x03 o 0x04.
// El SEN0681 es la versión de agua de mar y su wiki no publica la tabla.
// TODO VERIFICAR con el sensor real que el mapa es el mismo (lectura en modo calibración).
#define MODBUS_DIRECCION    1
#define MODBUS_BAUDIOS      4800
#define MODBUS_REGISTROS_OK 1
#define REG_SATURACION      0x0000     // saturación de oxígeno (1,0 = 100 %), no se envía
#define REG_OXIGENO_MGL     0x0002     // oxígeno disuelto en mg/L
#define REG_TEMPERATURA_C   0x0004     // temperatura en °C
#define REG_SALINIDAD       0x1020     // salinidad (lectura/escritura). Con agua de red tiene que valer 0.
                                       // TODO VERIFICAR el valor de fábrica del SEN0681 (al ser de agua de mar
                                       // puede venir distinto de 0) y el formato del dato, que la wiki no indica.

// ---------- ADS1115 ----------
#define ADS_DIRECCION 0x48
#define CANAL_PH      0
// canal 1 libre (antes conductividad, que ya no se mide)
#define CANAL_NIVEL   2
#define CANAL_BATERIA 3

// ---------- Conversiones ----------
#define DIVISOR_BATERIA   ((100.0f + 22.0f) / 22.0f)  // 100k arriba, 22k abajo
#define BATERIA_BAJA_MV   12400                      // LiFePO4 ~20 % de carga
#define NIVEL_R_SHUNT_OHM 120.0f    // TODO VERIFICAR con el convertidor 4-20 mA usado
#define NIVEL_RANGO_MM    5000.0f   // KIT0139: 0-5 m (wiki DFRobot SKU_KIT0139, etiqueta del kit comprobada)
#define TEMP_DEFECTO_C    25.0f     // si no hay temperatura del SEN0681

// ---------- Pantalla OLED (SSD1306 128x64 de la placa) ----------
#define PANTALLA_ACTIVA          1     // 0 = no usar la pantalla (ahorra unos mA durante el ciclo)
#define PANTALLA_APAGAR_AL_DORMIR 1    // 1 en la maqueta (ahorro); 0 en el banco de pruebas: el último
                                       // resultado se queda en pantalla mientras duerme
#define T_PANTALLA_RESULTADO_MS  5000UL  // tiempo que se ve el resultado del envío antes de dormir
