#pragma once
#include <Arduino.h>

// El ADS1115 y la pantalla OLED van por el mismo bus I2C. La pantalla se refresca
// desde otra tarea, así que cada acceso al bus se protege con este mutex.
void i2cIniciarMutex();
void i2cTomar();
void i2cSoltar();
