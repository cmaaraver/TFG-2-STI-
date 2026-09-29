#include "i2c_compartido.h"
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

static SemaphoreHandle_t mutexI2C = nullptr;

void i2cIniciarMutex() {
  if (!mutexI2C) mutexI2C = xSemaphoreCreateMutex();
}

void i2cTomar() {
  if (mutexI2C) xSemaphoreTake(mutexI2C, portMAX_DELAY);
}

void i2cSoltar() {
  if (mutexI2C) xSemaphoreGive(mutexI2C);
}
