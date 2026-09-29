# TFG — Monitorización de la calidad del agua con LoRaWAN

Nodo solar con sondas (O2, pH, EC, temperatura, nivel) → LoRaWAN privado → Raspberry Pi 5
(ChirpStack) → PC con TimescaleDB y Grafana, accesible desde fuera por Tailscale.

- Plan completo y tareas: `CLAUDE.md`
- Material: `docs/01-lista-material.md`
- Red: `docs/02-arquitectura-red.md`
- Conexionado del nodo: `docs/03-conexionado-nodo.md`
- Firmware: `firmware/nodo-agua` (PlatformIO: `pio run -e lilygo_t3_v1_6_1`)
