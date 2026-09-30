# Prompts para Claude Code: Raspberry por SSH y LILYGO por USB

Dos prompts para pegar en **Claude Code** en el PC del aula o de casa. Con el primero, Claude Code entra por SSH
en la Raspberry Pi 5 y deja todo el servidor instalado con `raspberry/instalar.sh`. Con el segundo, compila y
graba el firmware en la LILYGO conectada por USB y lo comprueba por el monitor serie.

Los dos prompts se basan en lo que ya hay en este repositorio (`main`). No hacen nada que no esté en
`raspberry/README.md`, `docs/08-guia-instalacion.md` y `firmware/nodo-agua/README.md`: solo le dicen a
Claude Code en qué orden hacerlo y qué comprobar.

## 0. Preparar el PC (una vez)

Pensado para **Windows 10/11 con PowerShell**. Para Linux, ver el apartado 4.

1. Instalar **Git for Windows** (https://git-scm.com). Claude Code en Windows lo necesita porque usa su Git Bash
   para ejecutar comandos. Trae también `ssh`, `scp` y `sh`.
2. Instalar **Python 3** (https://www.python.org, marcar *Add python.exe to PATH*) y después PlatformIO:
   `pip install platformio`. Si ya se usa la extensión PlatformIO de VS Code, vale su `pio`
   (`%USERPROFILE%\.platformio\penv\Scripts\pio.exe`).
3. Instalar **Claude Code** (https://docs.claude.com/es/docs/claude-code) e iniciar sesión.
4. Bajar el repositorio:
   ```powershell
   cd $HOME\Documents
   git clone https://github.com/cmaaraver/TFG-2-STI-.git
   cd TFG-2-STI-
   ```
5. Clave SSH para la Raspberry (si no se tiene ya): `ssh-keygen -t ed25519`. El contenido de
   `$HOME\.ssh\id_ed25519.pub` se pega en Raspberry Pi Imager al grabar la microSD (opción *SSH con clave pública*).

Para usar un prompt: abrir PowerShell **dentro de la carpeta `TFG-2-STI-`**, escribir `claude`, pegar el prompt
entero con los huecos `<<...>>` ya rellenados y pulsar Intro. Claude Code pide permiso antes de cada comando;
leer lo que va a ejecutar antes de aceptar.

## 1. Datos que hay que tener a mano

| Hueco | Dónde se saca | Prompt |
|---|---|---|
| `<<IP_RASPBERRY>>` | IP que da el instituto al **adaptador USB-Ethernet** de la Raspberry (router, `hostname -I` con teclado y monitor, o `ping rpi-lora.local`) | 1 |
| `<<USUARIO_RASPBERRY>>` | Usuario creado en Raspberry Pi Imager | 1 |
| `<<SUBDOMINIO_DUCKDNS>>` | `docs/09-guia-duckdns.md`, apartado 1 (solo el nombre, sin `.duckdns.org`) | 1 |
| Token de DuckDNS | Página de DuckDNS. **No se pega en el prompt**: se mete en una variable de entorno antes de abrir Claude Code (ver abajo) | 1 |
| `<<PUERTO_COM>>` | Administrador de dispositivos → *Puertos (COM y LPT)*, o `pio device list` | 2 |
| `<<MODELO_PLACA>>` | Serigrafía de la LILYGO. El firmware está preparado para la **T3 V1.6.1** (la T3-S3 aún tiene pines sin confirmar) | 2 |
| `<<DEV_EUI>>`, `<<APP_KEY>>`, `<<NWK_KEY>>` | ChirpStack → dispositivo → *OTAA keys* (`docs/08-guia-instalacion.md`, apartado 6). Si aún no están, poner `AUN NO` | 2 |

El token de DuckDNS se pasa así, en la misma ventana de PowerShell, justo antes de escribir `claude`:

```powershell
$env:DUCKDNS_TOKEN = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
claude
```

Claude Code hereda la variable y la usa como `$DUCKDNS_TOKEN` sin tener que verla ni escribirla en el chat.

## 2. Prompt 1: instalar la Raspberry Pi 5 por SSH

Antes: la microSD grabada con **Raspberry Pi OS Lite 64 bits** (Bookworm o posterior, que traen NetworkManager),
el **cable del instituto en el adaptador USB-Ethernet**, el puerto integrado (eth0) al inyector PoE del wAP y
teclado y monitor a mano por si acaso (CLAUDE.md, regla 8).

````text
Eres mi ayudante para instalar el servidor de mi TFG en una Raspberry Pi 5 por SSH. Estás abierto en la carpeta
del repositorio https://github.com/cmaaraver/TFG-2-STI- (rama main) en mi PC con Windows. Responde siempre en español.

DATOS
- Raspberry: usuario <<USUARIO_RASPBERRY>>, IP <<IP_RASPBERRY>> (es la IP del adaptador USB-Ethernet, red del instituto).
- Subdominio de DuckDNS: <<SUBDOMINIO_DUCKDNS>>
- El token de DuckDNS está en la variable de entorno DUCKDNS_TOKEN. Úsala como "$DUCKDNS_TOKEN" en los comandos;
  no la imprimas nunca, no me la pidas y no la escribas en ningún archivo del repositorio.
- Sistema de la Raspberry: Raspberry Pi OS Lite 64 bits (Bookworm o posterior), en microSD de 64 GB, sin NVMe.

LEE PRIMERO (enteros) y sigue lo que dicen, sin inventar pasos ni parámetros:
CLAUDE.md, raspberry/README.md, raspberry/instalar.sh, raspberry/red/configurar-red.sh, raspberry/.env.example,
docs/02-arquitectura-red.md, docs/08-guia-instalacion.md (apartados 4, 5 y 7) y docs/09-guia-duckdns.md.

REGLAS
1. Todos los comandos en la Raspberry van por: ssh -o BatchMode=yes <<USUARIO_RASPBERRY>>@<<IP_RASPBERRY>> '...'
   Para transferir archivos, scp. No cambies la configuración SSH de la Raspberry.
2. Nunca toques eth0 a mano ni cortes la interfaz por la que estamos conectados. La SSH tiene que entrar por el
   adaptador USB (red del instituto). Si compruebas que entramos por eth0, para y avísame.
3. Los secretos (raspberry/.env, token de DuckDNS, claves LoRaWAN) no se enseñan, no se copian al repo y no se suben
   a git. El .env lo genera instalar.sh en la Raspberry con contraseñas aleatorias.
4. instalar.sh tarda (actualiza el sistema y compila Caddy). Nunca lo lances en primer plano: déjalo corriendo en
   segundo plano en la Raspberry con su salida en un log y revísalo cada poco.
5. Si algo falla, lee el log, explícame la causa y proponme el arreglo antes de tocar nada fuera del repo.
   No cambies parámetros de ChirpStack, RouterOS ni del hardware que no estén en el repo (CLAUDE.md, regla 2).
6. Pídeme confirmación antes de reiniciar la Raspberry.

PASOS
0. Comprobación inicial (un solo ssh): uname -m (tiene que ser aarch64), cat /etc/os-release, nmcli -v,
   sudo -n true && echo SUDO_OK, ip -br a, echo $SSH_CONNECTION. Dime por qué interfaz entramos y cómo se llaman
   las dos interfaces (la integrada va al wAP; la USB, al instituto). Si sudo pide contraseña, instalar.sh no puede
   ir desatendido: explícame cómo dar sudo sin contraseña a mi usuario o si lo lanzo yo con ssh -t.
1. En la Raspberry: sudo apt-get update && sudo apt-get install -y git. Si no existe ~/TFG-2-STI-, git clone del
   repositorio; si existe, git -C ~/TFG-2-STI- pull.
2. Respuestas de instalar.sh. Pregunta, en este orden: subdominio, token (solo si no existe raspberry/.env),
   "¿Instalar Tailscale?" (responder s) y "¿Batería RTC oficial?" (pregúntamelo a mí; si no lo sé, n).
   Crea el fichero de respuestas en la Raspberry sin que el token pase por el chat ni por el repo:
     printf '%s\n%s\ns\n<s|n>\n' "<<SUBDOMINIO_DUCKDNS>>" "$DUCKDNS_TOKEN" | ssh ... 'umask 077; cat > ~/respuestas-instalar.txt'
   (si ~/TFG-2-STI-/raspberry/.env ya existe, el fichero solo lleva las dos últimas respuestas).
3. Lanza la instalación en segundo plano:
     ssh ... 'cd ~/TFG-2-STI-/raspberry && setsid nohup ./instalar.sh < ~/respuestas-instalar.txt > ~/instalar.log 2>&1 &'
   Si las interfaces no se llaman eth0/eth1, añade delante IF_LORA=... IF_INSTITUTO=...
   Revisa con: ssh ... 'tail -n 25 ~/instalar.log; pgrep -f instalar.sh >/dev/null && echo SIGUE || echo TERMINADO'
   Cuando en el log salga el enlace de Tailscale (login.tailscale.com/...), enséñamelo para que inicie sesión
   con la cuenta del equipo, y sigue esperando.
4. Al terminar: borra ~/respuestas-instalar.txt y dime si salió "INSTALACIÓN TERMINADA" o en qué paso falló.
   Enséñame el resumen del final del log (web, IP, MAC, qué pedir al coordinador TIC).
5. Comprobaciones (las de docs/08-guia-instalacion.md apartado 4 y raspberry/README.md), con su salida resumida:
   - cd ~/TFG-2-STI-/raspberry && sudo docker compose ps → todo running, y healthy los que tienen healthcheck.
   - curl -fsS http://127.0.0.1/api/salud → {"estado":"ok"}
   - sudo docker compose logs caddy | grep -i certificate → certificado de <<SUBDOMINIO_DUCKDNS>>.duckdns.org
     (se saca por DNS de DuckDNS, no necesita el puerto 443 abierto).
   - chronyc tracking, ip -br a (192.168.50.1 en la interfaz del wAP), sudo ufw status verbose, crontab -l.
   - Prueba de la web sin el nodo: el comando mosquitto_pub del apartado "Probar la web sin el nodo" de
     raspberry/README.md, luego comprobar que la fila entra en la tabla medidas y borrar los datos de prueba
     (dev_eui 0000000000000001 en medidas, nodos y uplinks_raw), como dice ese mismo apartado.
6. Con mi permiso: sudo reboot, espera a que vuelva la SSH y repite docker compose ps y /api/salud.
7. Copia del .env: propónme el comando scp para guardarlo en una carpeta de mi PC FUERA del repositorio
   (tiene todas las contraseñas). No lo ejecutes sin que te diga la carpeta.
8. Resumen final para mí: qué ha quedado funcionando, qué ha fallado y lo que queda a mano, que NO debes hacer tú:
   - configurar el wAP LR8 (raspberry/README.md, apartado 4),
   - entrar en ChirpStack por Tailscale o con túnel ssh -L 8080:127.0.0.1:8080 <<USUARIO_RASPBERRY>>@<<IP_RASPBERRY>>,
     cambiar admin/admin y dar de alta gateway, perfil con codec/decoder.js y dispositivo (apartado 5),
   - pedir al coordinador TIC la reserva de IP y el TCP 443 (docs/09-guia-duckdns.md).
   Apunta también los problemas que hayas encontrado y cómo se resolvieron, para la memoria (CLAUDE.md, regla 7).
````

## 3. Prompt 2: compilar, grabar y comprobar la LILYGO por USB

Antes: **antena puesta** (nunca encenderla sin antena), **sin tarjeta microSD** en la placa y cable USB de datos
(no solo de carga).

````text
Eres mi ayudante para grabar el firmware del nodo de mi TFG en una LILYGO conectada por USB a este PC con Windows.
Estás abierto en la carpeta del repositorio https://github.com/cmaaraver/TFG-2-STI- (rama main). Responde siempre
en español.

DATOS
- Placa: <<MODELO_PLACA>> (el firmware está preparado para LILYGO T3 V1.6.1, entorno lilygo_t3_v1_6_1).
- Puerto: <<PUERTO_COM>>
- Claves LoRaWAN de ChirpStack (o "AUN NO"): DevEUI <<DEV_EUI>>, Application key <<APP_KEY>>, Network key <<NWK_KEY>>.
  JoinEUI: todo ceros.

LEE PRIMERO (enteros) y sigue lo que dicen, sin inventar nada:
CLAUDE.md, firmware/nodo-agua/README.md, firmware/nodo-agua/platformio.ini, firmware/nodo-agua/include/config.h,
firmware/nodo-agua/include/secrets.example.h, docs/03-conexionado-nodo.md y docs/08-guia-instalacion.md
(apartados 1, 3, 6 y 7).

REGLAS
1. Antes de grabar, pregúntame si la antena está puesta y si no hay microSD en la placa. Sin mi "sí", no grabes.
2. No cambies pines, registros Modbus, factores de sondas ni nada de config.h sin fuente oficial
   (CLAUDE.md, regla 2). Lo que esté como TODO VERIFICAR se queda así; MODBUS_REGISTROS_OK sigue a 0 hasta que
   le pasemos los registros de la wiki de DFRobot.
3. Si la placa es una T3-S3, config.h tiene un #error a propósito: para y dime qué pines faltan. No los inventes.
4. include/secrets.h no se sube nunca a git (ya está en .gitignore). Compruébalo con git status antes de terminar.
5. No uses el monitor serie interactivo (pio device monitor) porque se queda bloqueado: lee el puerto con el
   script de Python del paso 5, con tiempo límite.

PASOS
1. Herramientas: pio --version (si no está: pip install platformio, o usa
   $HOME/.platformio/penv/Scripts/pio.exe si tengo la extensión de VS Code). pio device list para confirmar que
   <<PUERTO_COM>> existe. Si no aparece ningún puerto, dime qué chip USB-serie lleva la placa según el
   Administrador de dispositivos o la serigrafía y qué driver oficial me falta; no instales drivers tú.
2. Opcional, si hay g++ y node: sh pruebas/payload/probar.sh → tiene que acabar en
   "TODO OK (3 payloads, 10 campos del ingestor comprobados)".
3. Claves: copia firmware/nodo-agua/include/secrets.example.h a secrets.h (solo si no existe). Si te he dado
   claves, ponlas como dice docs/08-guia-instalacion.md apartado 6: MSB primero, tal cual se leen en ChirpStack,
   DevEUI como 0x...ULL y las claves de 2 en 2 cifras {0x..,0x..,...} (16 bytes cada una; comprueba que son 32
   cifras hex). Si es "AUN NO", deja los ceros. No me repitas las claves en el chat.
4. Compilar y grabar desde firmware/nodo-agua:
     pio run -e lilygo_t3_v1_6_1
     pio run -e lilygo_t3_v1_6_1 -t upload --upload-port <<PUERTO_COM>>
   Tiene que acabar en [SUCCESS]. Si la subida no conecta, dime que mantenga pulsado BOOT al empezar a subir
   y reintenta una vez. Si el puerto está ocupado, algún monitor serie lo tiene abierto: dímelo.
5. Comprobar por el monitor serie. Crea un script temporal FUERA del repo (en %TEMP%) con pyserial (viene con
   PlatformIO: usa el Python de $HOME/.platformio/penv/Scripts/python.exe si el del sistema no lo tiene) que:
   - abra <<PUERTO_COM>> a 115200 con DTR y RTS a False ANTES de abrir el puerto (para no dejar el ESP32 en
     modo arranque), dé un pulso de reinicio (RTS True 0,1 s y luego False),
   - lea y muestre durante N segundos (argumento, por defecto 150) y lo guarde también en un .log en %TEMP%,
   - opcionalmente, tras una espera, envíe comandos terminados en "\n" (para el modo calibración).
   Lánzalo y compara con lo que dice docs/08-guia-instalacion.md:
   - Siempre: "--- Nodo calidad agua, ciclo 1 ---" y que NO salga "Error de radio".
   - Con claves a cero: "Fallo de join" es normal en este punto (luego duerme 5 min).
   - Con claves buenas y el gateway y ChirpStack ya funcionando: "Join OK (sesion nueva)" o "Sesion restaurada",
     la línea "T=... O2=... pH=... nivel=... bat=... caudal=... agua=..." y
     "Uplink enviado: fcnt=N SFx, X ms en el aire, Y ms en total".
   Pregúntame qué enseña la pantalla OLED (logo de Los Viveros y fase del ciclo con contador).
6. Modo calibración, solo si te lo pido: yo pongo el puente MODO_CAL a GND. Lanza el script con reinicio,
   espera los 60 s de calentamiento y envía "leer" y "ver". "ph7" y "ph4" solo cuando yo te confirme que la
   sonda está en el tampón correspondiente (y enjuagada entre uno y otro). Al acabar, "salir".
   Criterio de la fase 2: pH 7,00 ± 0,1 y 4,00 ± 0,1 en los tampones y rs485_err=0.
7. Resumen para mí: versión grabada (git log -1 --oneline), resultado de compilación y subida, qué salió por
   el monitor serie (las líneas importantes, sin claves), qué está bien, qué falla y el siguiente paso.
   Borra el script temporal y el log, y comprueba con git status que no se ha quedado secrets.h preparado
   para subir.
````

## 4. Si el PC es Linux

Los dos prompts valen igual con estos cambios:

- Prompt 1: la variable se pone con `export DUCKDNS_TOKEN=...` antes de `claude`, y quitar "con Windows".
- Prompt 2: el puerto es `/dev/ttyUSB0` o `/dev/ttyACM0` (`pio device list`). El usuario tiene que estar en el
  grupo `dialout` (`sudo usermod -aG dialout $USER` y volver a iniciar sesión) y conviene instalar las reglas udev
  de PlatformIO (https://docs.platformio.org/en/latest/core/installation/udev-rules.html). El script
  temporal va en `/tmp` y el Python de PlatformIO es `~/.platformio/penv/bin/python`.

## 5. Qué no hacen los prompts (a propósito)

- No configuran el **wAP LR8** ni dan de alta nada en **ChirpStack**: dependen del EUI del gateway y de las
  claves del nodo, y se hacen desde el navegador (`raspberry/README.md`, apartados 4 y 5).
- No abren el puerto 443: eso lo hace el coordinador TIC (`docs/09-guia-duckdns.md`).
- No rellenan los registros Modbus del SEN0681: siguen pendientes de copiarlos de la wiki de DFRobot.

Orden recomendado: prompt 1 (Raspberry) → wAP y ChirpStack a mano → prompt 2 con las claves del dispositivo.
El prompt 2 también se puede usar antes con `AUN NO` para probar solo la placa (fase 2).
