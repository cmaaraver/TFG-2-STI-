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
| `<<IP_INICIAL>>` | IP que tiene la Raspberry **antes** de instalar: la que le da el DHCP de la VLAN 500 al primer arranque (`hostname -I` con teclado y monitor, o `ping rpi-lora.local`). Si ya se le puso a mano la fija, es `172.16.50.3` | 1 |
| `<<USUARIO_RASPBERRY>>` | Usuario creado en Raspberry Pi Imager | 1 |
| Cuenta de Tailscale | `docs/09-acceso-internet.md`, apartado 1. No se pega nada: durante la instalación Claude Code enseña un enlace y se inicia sesión en el navegador | 1 |
| `<<PUERTO_COM>>` | Administrador de dispositivos → *Puertos (COM y LPT)*, o `pio device list` | 2 |
| `<<MODELO_PLACA>>` | Serigrafía de la LILYGO. La nuestra es la **T3 V1.6.1** (`T3_V1.6.1 20210104`, confirmado el 2026-10-26) | 2 |
| `<<DEV_EUI>>`, `<<APP_KEY>>`, `<<NWK_KEY>>` | ChirpStack → dispositivo → *OTAA keys* (`docs/08-guia-instalacion.md`, apartado 6). Si aún no están, poner `AUN NO` | 2 |

La IP fija de la Raspberry (`172.16.50.3`), la del wAP (`172.16.50.2`) y la puerta de enlace (`172.16.50.1`, VLAN 500)
ya están en el prompt y en `raspberry/red/red.env`, no hay que rellenarlas. El PC con Claude Code tiene que llegar a
la VLAN 500 (estar conectado a ella o que el centro deje pasar el tráfico desde la red del aula).

## 2. Prompt 1: instalar la Raspberry Pi 5 por SSH

Antes: la microSD grabada con **Raspberry Pi OS Lite 64 bits** (Bookworm o posterior, que traen NetworkManager),
el puerto integrado (eth0) en una toma del switch de la **VLAN 500** (sin etiquetar) y teclado y monitor a mano
por si acaso (CLAUDE.md, regla 8). Ya no se usa adaptador USB-Ethernet.

````text
Eres mi ayudante para instalar el servidor de mi TFG en una Raspberry Pi 5 por SSH. Estás abierto en la carpeta
del repositorio https://github.com/cmaaraver/TFG-2-STI- (rama main) en mi PC con Windows. Responde siempre en español.

DATOS
- Red: VLAN 500 del instituto, máscara /24, puerta de enlace 172.16.50.1. Raspberry con IP fija 172.16.50.3 y gateway
  LoRa (wAP LR8) con IP fija 172.16.50.2. Estos datos están en raspberry/red/red.env; no los cambies sin preguntarme.
- Raspberry: usuario <<USUARIO_RASPBERRY>>. Ahora mismo tiene la IP <<IP_INICIAL>>; después de la instalación será
  172.16.50.3 (la llamo IP_ACTUAL: al principio <<IP_INICIAL>>, y 172.16.50.3 cuando la red esté configurada).
- Web pública: el instituto no abre puertos, así que no hay DuckDNS. La web sale a Internet con Tailscale Funnel,
  que configura instalar.sh (docs/09-acceso-internet.md).
- Sistema de la Raspberry: Raspberry Pi OS Lite 64 bits (Bookworm o posterior), en microSD de 64 GB, sin NVMe.

LEE PRIMERO (enteros) y sigue lo que dicen, sin inventar pasos ni parámetros:
CLAUDE.md, raspberry/README.md, raspberry/instalar.sh, raspberry/red/red.env, raspberry/red/configurar-red.sh, raspberry/.env.example,
docs/02-arquitectura-red.md, docs/08-guia-instalacion.md (apartados 4, 5 y 7) y docs/09-acceso-internet.md.

REGLAS
1. Todos los comandos en la Raspberry van por: ssh -o BatchMode=yes <<USUARIO_RASPBERRY>>@IP_ACTUAL '...'
   Para transferir archivos, scp. No cambies la configuración SSH de la Raspberry.
2. Nunca toques la red a mano (nmcli, ip) ni cortes la interfaz por la que estamos conectados. El cambio a la IP
   fija lo hace instalar.sh: si entramos con otra IP, prepara la red, se para y pide reiniciar. No hay adaptador USB:
   solo eth0.
3. Los secretos (raspberry/.env, claves LoRaWAN) no se enseñan, no se copian al repo y no se suben
   a git. El .env lo genera instalar.sh en la Raspberry con contraseñas aleatorias.
4. instalar.sh tarda (actualiza el sistema, descarga las imágenes de Docker y construye las propias). Nunca lo lances en primer plano: déjalo corriendo en
   segundo plano en la Raspberry con su salida en un log y revísalo cada poco.
5. Si algo falla, lee el log, explícame la causa y proponme el arreglo antes de tocar nada fuera del repo.
   No cambies parámetros de ChirpStack, RouterOS ni del hardware que no estén en el repo (CLAUDE.md, regla 2).
6. Pídeme confirmación antes de reiniciar la Raspberry.

PASOS
0. Comprobación inicial (un solo ssh): uname -m (tiene que ser aarch64), cat /etc/os-release, nmcli -v,
   sudo -n true && echo SUDO_OK, ip -br a, ip route, echo $SSH_CONNECTION. Dime qué IP tiene eth0 y si ya es la
   fija 172.16.50.3, y comprueba que la puerta de enlace es 172.16.50.1. Si sudo pide contraseña, instalar.sh no puede
   ir desatendido: explícame cómo dar sudo sin contraseña a mi usuario o si lo lanzo yo con ssh -t.
1. En la Raspberry: sudo apt-get update && sudo apt-get install -y git. Si no existe ~/TFG-2-STI-, git clone del
   repositorio; si existe, git -C ~/TFG-2-STI- pull.
2. Respuestas de instalar.sh. Solo pregunta una cosa: "¿Batería RTC oficial?" (pregúntamelo a mí; si no lo sé, n).
   Crea el fichero de respuestas en la Raspberry:
     printf '<s|n>\n' | ssh ... 'cat > ~/respuestas-instalar.txt'
3. Lanza la instalación en segundo plano:
     ssh ... 'cd ~/TFG-2-STI-/raspberry && setsid nohup ./instalar.sh < ~/respuestas-instalar.txt > ~/instalar.log 2>&1 &'
   Si el puerto integrado no se llama eth0, añade delante IF_RED=...
   Revisa con: ssh ... 'tail -n 25 ~/instalar.log; pgrep -f instalar.sh >/dev/null && echo SIGUE || echo TERMINADO'
   Cuando en el log salga el enlace de Tailscale (login.tailscale.com/...), enséñamelo para que inicie sesión
   con la cuenta del equipo, y sigue esperando. Después puede salir otro enlace para activar HTTPS y Funnel en
   el tailnet: enséñamelo también.
   Si <<IP_INICIAL>> no es 172.16.50.3, el script se para después del paso 6 con "Red preparada ... sudo reboot".
   Entonces: pídeme permiso, sudo reboot, espera a que responda ssh <<USUARIO_RASPBERRY>>@172.16.50.3 (a partir de
   aquí IP_ACTUAL = 172.16.50.3), vuelve a lanzar el script igual que antes. Si tras reiniciar no responde en 172.16.50.3, para y avísame: lo
   miro con teclado y monitor.
4. Al terminar: borra ~/respuestas-instalar.txt y dime si salió "INSTALACIÓN TERMINADA" o en qué paso falló.
   Enséñame el resumen del final del log (web, IP, qué pedir al coordinador TIC).
5. Comprobaciones (las de docs/08-guia-instalacion.md apartado 4 y raspberry/README.md), con su salida resumida:
   - cd ~/TFG-2-STI-/raspberry && sudo docker compose ps → todo running, y healthy los que tienen healthcheck.
   - curl -fsS http://127.0.0.1/api/salud → {"estado":"ok"}
   - sudo tailscale funnel status → https://rpi-lora.<red>.ts.net (Funnel on) hacia http://127.0.0.1:80, y
     sudo tailscale serve status → ChirpStack en el puerto 8443 solo para el tailnet. Dime la dirección pública.
   - chronyc tracking, ip -br a (172.16.50.3/24 en eth0), ip route (default via 172.16.50.1), getent hosts tailscale.com,
     sudo ufw status verbose, sudo iptables -L DOCKER-USER -n (UDP 1700 solo desde 172.16.50.2), crontab -l.
   - Prueba de la web sin el nodo: el comando mosquitto_pub del apartado "Probar la web sin el nodo" de
     raspberry/README.md, luego comprobar que la fila entra en la tabla medidas y borrar los datos de prueba
     (dev_eui 0000000000000001 en medidas, nodos y uplinks_raw), como dice ese mismo apartado.
6. Con mi permiso: sudo reboot, espera a que vuelva la SSH y repite docker compose ps y /api/salud.
7. Copia del .env: propónme el comando scp para guardarlo en una carpeta de mi PC FUERA del repositorio
   (tiene todas las contraseñas). No lo ejecutes sin que te diga la carpeta.
8. Resumen final para mí: qué ha quedado funcionando, qué ha fallado y lo que queda a mano, que NO debes hacer tú:
   - configurar el wAP LR8 (raspberry/README.md, apartado 4),
   - si GATEWAY_EUI quedó vacío en el .env: ponerlo y lanzar sudo docker compose run --rm provisionar (apartado 5;
     el resto del alta en ChirpStack ya lo hizo instalar.sh),
   - copiar firmware/nodo-agua/include/secrets.h de la Raspberry a mi PC (propónme el scp, no lo ejecutes),
   - pedir al coordinador TIC que 172.16.50.2 y 172.16.50.3 queden fuera del DHCP de la VLAN 500 y permiso para
     Tailscale (docs/09-acceso-internet.md); no hay que abrir puertos,
   - desactivar "key expiry" de rpi-lora en la consola de Tailscale y probar la web desde un móvil con datos.
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
   (CLAUDE.md, regla 2). Lo que esté como TODO VERIFICAR se queda así. Los registros del SEN0681 ya están
   (wiki del SEN0680, 4800 baudios) y MODBUS_REGISTROS_OK vale 1: si rs485_err=1, dímelo antes de tocarlos.
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
3. Claves: si te he pasado el secrets.h que generó la Raspberry (contenedor provisionar), cópialo a
   firmware/nodo-agua/include/secrets.h y no toques nada más de este punto. Si no, copia
   firmware/nodo-agua/include/secrets.example.h a secrets.h (solo si no existe). Si te he dado
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

- Prompt 1: quitar "con Windows".
- Prompt 2: el puerto es `/dev/ttyUSB0` o `/dev/ttyACM0` (`pio device list`). El usuario tiene que estar en el
  grupo `dialout` (`sudo usermod -aG dialout $USER` y volver a iniciar sesión) y conviene instalar las reglas udev
  de PlatformIO (https://docs.platformio.org/en/latest/core/installation/udev-rules.html). El script
  temporal va en `/tmp` y el Python de PlatformIO es `~/.platformio/penv/bin/python`.

## 5. Qué no hacen los prompts (a propósito)

- No configuran el **wAP LR8** ni dan de alta nada en **ChirpStack**: dependen del EUI del gateway y de las
  claves del nodo, y se hacen desde el navegador (`raspberry/README.md`, apartados 4 y 5).
- No piden nada al coordinador TIC: eso lo hacéis vosotros (`docs/09-acceso-internet.md`).
- No rellenan los registros Modbus del SEN0681: siguen pendientes de copiarlos de la wiki de DFRobot.

Orden recomendado: prompt 1 (Raspberry) → wAP y ChirpStack a mano → prompt 2 con las claves del dispositivo.
El prompt 2 también se puede usar antes con `AUN NO` para probar solo la placa (fase 2).
