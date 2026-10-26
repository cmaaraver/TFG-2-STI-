# Pruebas sin hardware

| Prueba | Comando | Qué comprueba |
|---|---|---|
| Formato del mensaje | `sh pruebas/payload/probar.sh` | Que el mensaje que arma el firmware (`payload.h`) lo decodifica bien ChirpStack (`decoder.js`) y trae todos los campos que guarda el ingestor. También el downlink de intervalo |

| Servidor completo | `python3 pruebas/servidor/simular_nodo.py raspberry/.env` | Con el servidor en marcha y `provisionar` ejecutado: un wAP y un nodo simulados hacen el join OTAA (LoRaWAN 1.1) y mandan una medida que tiene que acabar en la base de datos y en la web (`raspberry/README.md`) |

Necesita `g++` y `node`. Salida esperada: `TODO OK (3 payloads, 10 campos del ingestor comprobados)`.

La prueba del servidor con datos simulados (sin nodo) está en `raspberry/README.md`.
