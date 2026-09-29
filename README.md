# TFG — Monitorización de la calidad del agua con LoRaWAN

Proyecto final del 2º curso de Sistemas de Telecomunicaciones e Informáticos (CPIFP Los Viveros, Sevilla).
Carlos Maraver Román y Rubén Trillo García.

Una maqueta exterior con energía solar mide el oxígeno disuelto, el pH, la temperatura, el nivel del depósito
y el caudal de la bomba. Envía los datos por LoRaWAN al gateway del edificio. La Raspberry Pi 5 lo hace todo:
servidor LoRaWAN, base de datos y una web con los datos en tiempo real y gráficas del histórico,
accesible desde Internet con DuckDNS.

![Esquema del sistema](docs/img/esquema-sistema.png)

- **Guía de instalación paso a paso**: [`docs/08-guia-instalacion.md`](docs/08-guia-instalacion.md)
- Plan completo y tareas: [`CLAUDE.md`](CLAUDE.md)
- Material: [`docs/01-lista-material.md`](docs/01-lista-material.md) · compra con enlaces: [`docs/07-lista-compra.md`](docs/07-lista-compra.md)
- Red: [`docs/02-arquitectura-red.md`](docs/02-arquitectura-red.md)
- Conexionado del nodo e instalación de las sondas: [`docs/03-conexionado-nodo.md`](docs/03-conexionado-nodo.md)
- Formato del mensaje LoRaWAN: [`docs/04-formato-payload.md`](docs/04-formato-payload.md) (prueba sin hardware: `sh pruebas/payload/probar.sh`)
- Maqueta y energía: [`docs/06-maqueta.md`](docs/06-maqueta.md)
- Firmware: `firmware/nodo-agua` (PlatformIO: `pio run -e lilygo_t3_v1_6_1`). La pantalla OLED enseña el logo de
  Los Viveros, la fase del ciclo y un temporizador con lo que tarda el envío por LoRa:

  ![Pantalla OLED](docs/img/pantalla-oled.png)

- Servidor (Raspberry): [`raspberry/README.md`](raspberry/README.md) (`docker compose up -d --build`)
