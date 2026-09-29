# Pruebas sin hardware

| Prueba | Comando | Qué comprueba |
|---|---|---|
| Formato del mensaje | `sh pruebas/payload/probar.sh` | Que el mensaje que arma el firmware (`payload.h`) lo decodifica bien ChirpStack (`decoder.js`) y trae todos los campos que guarda el ingestor. También el downlink de intervalo |

Necesita `g++` y `node`. Salida esperada: `TODO OK (3 payloads, 10 campos del ingestor comprobados)`.

La prueba del servidor con datos simulados (sin nodo) está en `raspberry/README.md`.
