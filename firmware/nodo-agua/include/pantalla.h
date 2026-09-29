#pragma once
#include <Arduino.h>

// Pantalla OLED de la LILYGO: logo de Los Viveros arriba y debajo lo que está haciendo el nodo.
// Mientras se envía por LoRa se ve un temporizador que cuenta en directo.
// Se refresca desde una tarea de FreeRTOS, así el temporizador avanza aunque
// el envío (sendReceive) tenga bloqueado el programa principal.

void pantallaIniciar(uint32_t ciclo);
void pantallaFase(const char* texto);            // "Bombeando", "Midiendo"... con segundos de ciclo
void pantallaEnviando();                         // arranca el temporizador del envío LoRa
// Resultado: ok, ms que tardó el envío completo, ms en el aire, factor de ensanchado y minutos hasta el siguiente
void pantallaResultado(bool ok, uint32_t msEnvio, uint32_t msAire, uint8_t sf, uint16_t proximoMin);
void pantallaMensaje(const char* linea1, const char* linea2);  // avisos (error de radio, join fallido...)
void pantallaDormir();                           // para la tarea y apaga (o deja) la pantalla
