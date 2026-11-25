from lib import *
from c1 import REPO, D, PLANOS

H(2, '2.7 Componentes Principales Utilizados')
P('En este apartado van los equipos que forman el sistema, uno por uno, con lo que hace cada uno y los datos que más '
  'nos han importado al montarlo. El listado completo, con el material pequeño, está en el apartado 2.9.')

H(3, 'Nodo: LILYGO T3 V1.6.1')
P('Es la placa que lo lee todo y lo manda por radio. La nuestra lleva la serigrafía `T3_V1.6.1 20210104`. Tiene un '
  'ESP32 (el microcontrolador), la radio LoRa SX1276 para 868 MHz, una pantalla OLED de 0,96 pulgadas, conector USB '
  'para alimentarla y programarla, y un conector para la antena. La elegimos porque trae la radio y la pantalla ya '
  'integradas y porque el centro la tenía.')
T(['Característica', 'Valor'], [
    ['Microcontrolador', 'ESP32, entradas y salidas a 3,3 V (no admiten 5 V)'],
    ['Radio', 'Semtech SX1276, 868 MHz, con antena de 868 MHz por conector SMA'],
    ['Pantalla', 'OLED de 128 × 64 puntos, bus I2C (dirección 0x3C)'],
    ['Alimentación', 'Por USB a 5 V. El pin de 5 V de la placa no se usa'],
    ['Salida de 3,3 V', 'Regulador de 500 mA compartido con la radio; de ahí se alimentan la placa del pH, el conversor de 4-20 mA y el módulo RS485'],
    ['Programación', 'PlatformIO con la librería RadioLib (LoRaWAN) y U8g2 (pantalla)'],
    ['Pines', 'Dos tiras de 13 pines que vienen sin soldar. GPIO36 y GPIO39 no salen con su número: en la serigrafía se llaman S_VP y S_VN'],
], anchos=[4.0, 12.0], titulo='Características de la LILYGO T3 V1.6.1 que usamos')
P('Al preparar el montaje nos encontramos con que en la placa no aparecían «GPIO36» ni «GPIO39», que eran los pines '
  'previstos para el pH y el nivel. Comparando el esquema oficial de LilyGO (`T3_V1.6.1.pdf`, conectores JP1 y JP2) '
  'con una foto de nuestra placa vimos que son los dos primeros de la tira izquierda, **S_VP** (GPIO36) y **S_VN** '
  '(GPIO39). Desde entonces en las guías y en el esquema ponemos los nombres tal como salen en la serigrafía.')
T(['Tira izquierda (de arriba abajo)', 'Uso', 'Tira derecha (de arriba abajo)', 'Uso'], [
    ['S_VP (GPIO36)', 'pH', 'IO21', 'Pantalla'],
    ['S_VN (GPIO39)', 'Nivel', 'TxD / RXD', 'USB'],
    ['RST', '—', 'IO22', 'Pantalla'],
    ['IO34 / IO35', 'Libre / batería de la placa', 'IO23 / IO19', 'Radio LoRa'],
    ['IO14', 'RS485 RO', 'LoRa2 / LoRa1', 'Radio LoRa (IO32 / IO33)'],
    ['IO12', 'No se usa (pin de arranque)', 'IO26', 'Radio LoRa'],
    ['IO13', 'RS485 DI', 'GND', 'Masa común'],
    ['IO15', 'Puente de calibración', '3.3V', 'Línea de 3V3 de la protoboard'],
    ['IO2 / IO0', 'microSD / botón de arranque', 'GND', 'Otra masa'],
    ['IO4', 'Presencia de agua', '5V', 'No se usa'],
    ['IO25', 'RS485 DE/RE', '', ''],
], anchos=[3.8, 4.2, 3.8, 4.2], titulo='Pines de la T3 V1.6.1 según la serigrafía de nuestra placa', tam=9)
FOTO('La placa LILYGO T3 V1.6.1 con la antena puesta y la pantalla encendida (logo de Los Viveros y temporizador).',
     'Nodo LILYGO T3 V1.6.1 con la pantalla en marcha')

H(3, 'Sensor de oxígeno disuelto y temperatura: DFRobot SEN0681')
P('Es el sensor principal del proyecto y el que añadimos respecto al sistema de referencia. Mide el oxígeno disuelto '
  'por fluorescencia, así que no lleva ni membrana que cambiar ni electrolito, y da también la temperatura del agua. '
  'Su cable trae cuatro hilos: marrón (+12 V), negro (masa), amarillo (A) y azul (B). '
  'Se comunica por RS485 con protocolo Modbus RTU: el nodo le pregunta y él contesta con los valores. Se alimenta '
  'entre 10 y 30 V (nosotros a 12 V) y consume unos 0,2 W. Tarda hasta 60 segundos en dar un valor estable, y por '
  'eso el nodo espera ese tiempo antes de leer.')
P('Como la LILYGO no habla RS485 directamente, hace falta un **módulo conversor de RS485 a TTL de 3,3 V** (tipo '
  'MAX3485) entre los dos. A la fecha de escribir esto ese módulo está por conseguir, y sin él no hay ni oxígeno ni '
  'temperatura. [COMPLETAR: modelo del módulo RS485 que se ha usado al final]')
P('Un detalle a tener en cuenta: el SEN0681 es la versión para agua de mar y trae un ajuste de salinidad. Como '
  'nuestra agua es de red (dulce), ese ajuste tiene que estar a 0 ‰. [COMPLETAR: valor de salinidad que traía de '
  'fábrica y cómo se dejó a 0]')

H(3, 'Sonda de pH: DFRobot SEN0169-V2')
P('Es una sonda de pH de tipo industrial, que aguanta estar sumergida de forma continua (la de laboratorio que '
  'también había en el centro no lo aguanta, y se queda como referencia para comprobar la calibración). Viene con '
  'una placa que convierte la señal de la sonda, que es muy débil, en una tensión de 0 a 3,0 V que el nodo puede '
  'leer. Alimentamos la placa a 3,3 V desde la propia LILYGO y la sonda se conecta a la placa con un conector BNC.')

H(3, 'Sensor de nivel: DFRobot KIT0139')
P('Es un transmisor de nivel de los que se dejan caer al fondo del depósito. Mide la presión de la columna de agua '
  'que tiene encima y da una corriente de 4 a 20 mA proporcional a la altura, de 0 a 5 metros. En la misma caja '
  'viene el conversor de corriente a tensión, el **SEN0262**: una placa azul pequeña con dos bornas de tornillo '
  '(**I+** e **I−**) para el lazo y un conector de tres pines (**GND**, **VCC** y **SIG**) para la LILYGO. Pasa la '
  'corriente por una resistencia de 120 Ω. El cable de la sonda trae un hilo rojo fino (+12 V), uno negro (salida '
  'del lazo) y uno rojo grueso, que en realidad es un tubito de aire para compensar la presión atmosférica: no se '
  'conecta, no se puede aplastar ni doblar y su punta tiene que quedar seca.')

H(3, 'Sensor de presencia de agua: DFRobot SEN0204')
P('Es un sensor sin contacto que se pega por fuera de la pared del depósito y detecta si hay agua al otro lado, a '
  'través de paredes no metálicas de hasta 13 mm. Lo usamos como alarma de nivel mínimo: se pega a la altura por '
  'debajo de la cual la sonda de pH se quedaría en seco. Tenemos un SEN0509 de repuesto.')
P('El sensor saca cuatro hilos que van a una **placa adaptadora** que viene con él. De esa placa sale un cable de '
  'tres hilos: **rojo** (alimentación), **negro** (masa) y **verde** (salida). La placa tiene además un botón '
  '**SET** para elegir entre cuatro niveles de sensibilidad. La salida vale lo mismo que la alimentación cuando hay '
  'agua, y por eso lleva un divisor de tensión antes de llegar a la LILYGO (Anexo I).')

P('No hay caudalímetro ni sensor de presión de tubería, aunque los dos salen en el cartel de referencia: no los '
  'tenemos. El mensaje LoRaWAN deja reservado el hueco del caudal por si algún día se añade uno.')
FOTO('Los sensores sobre la mesa antes de montarlos: SEN0681, sonda de pH con su placa, KIT0139 con su conversor, '
     'y SEN0204.', 'Sensores utilizados en el proyecto')

H(3, 'Gateway LoRaWAN: MikroTik wAP LR8 kit')
P('Es el equipo que recibe por radio lo que manda el nodo y lo pasa a la red. Lleva una tarjeta LoRa de 8 canales '
  'para la banda de 863-870 MHz, antena interna de 2 dBi (admite una externa), un puerto Ethernet y caja de '
  'exterior. Funciona con RouterOS, el sistema de MikroTik, que ya trae el reenviador de paquetes LoRa, así que no '
  'hay que instalarle nada.')
T(['Dato', 'Valor'], [
    ['Sistema', 'RouterOS 7.20.7'],
    ['Identificador del gateway (EUI)', '04F41CFFFFC15CEB'],
    ['Nombre', 'wap-lr8-tfg'],
    ['Tarjeta LoRa', 'Firmware 1.4.4, banda 863-870 MHz, plan de canales eu-868'],
    ['Dirección IP', '172.16.50.2/24 (fija), puerta de enlace 172.16.50.1'],
    ['Servidor LoRaWAN al que reenvía', '172.16.50.3, UDP, puerto 1700'],
    ['Alimentación', 'PoE pasivo a 24 V con el inyector del kit (7 W como máximo)'],
    ['Caja', 'De exterior, IP54'],
], anchos=[5.5, 10.5], titulo='Datos del gateway MikroTik wAP LR8')
FOTO('El gateway MikroTik wAP LR8 montado en el mástil de la azotea, con el cable de red bajando y el conector '
     'hacia abajo.', 'Gateway LoRaWAN en el mástil de la azotea del instituto')

H(3, 'Servidor: Raspberry Pi 5')
P('Una Raspberry Pi 5 de 4 GB con una tarjeta microSD de 64 GB, Raspberry Pi OS Lite de 64 bits (basado en Debian 13) '
  'y sin pantalla ni teclado: se administra por SSH. Se llama `rpi-lora` y todo lo que hace va en contenedores '
  'Docker definidos en un único fichero, de manera que montarla desde cero es lanzar un script.')
FOTO('La Raspberry Pi 5 en su sitio definitivo, conectada a la toma de red de la VLAN 500 y a su fuente.',
     'Servidor Raspberry Pi 5')

H(3, 'Programas que forman el sistema')
T(['Programa', 'Dónde corre', 'Para qué sirve'], [
    ['Firmware del nodo (C++, PlatformIO)', 'LILYGO', 'Leer los sensores, armar el mensaje, enviarlo por LoRaWAN y dormir'],
    ['RadioLib', 'LILYGO', 'Librería que implementa LoRaWAN 1.1 sobre el SX1276'],
    ['RouterOS', 'wAP LR8', 'Sistema del gateway, con el reenviador de paquetes LoRa'],
    ['ChirpStack v4', 'Raspberry', 'Servidor LoRaWAN: da de alta el nodo, comprueba claves, descifra y decodifica'],
    ['ChirpStack Gateway Bridge', 'Raspberry', 'Recibe los paquetes UDP del gateway y los pasa a MQTT'],
    ['Mosquitto', 'Raspberry', 'Broker MQTT interno, con cola persistente y calidad de servicio 1'],
    ['Redis', 'Raspberry', 'Memoria rápida que necesita ChirpStack'],
    ['TimescaleDB (PostgreSQL 16)', 'Raspberry', 'Base de datos de las medidas, pensada para series de tiempo'],
    ['Ingestor (Python)', 'Raspberry', 'Programa propio: recoge cada medida de MQTT y la guarda en la base de datos'],
    ['Web (FastAPI y ECharts)', 'Raspberry', 'Programa propio: la página con las tarjetas, las gráficas y la descarga en CSV'],
    ['Caddy', 'Raspberry', 'Sirve la web en el puerto 80'],
    ['Tailscale', 'Raspberry', 'Publica la web en Internet (Funnel) y da acceso privado al equipo'],
    ['chrony y ufw', 'Raspberry', 'Servidor de hora para el gateway y firewall'],
], anchos=[4.8, 2.4, 8.8], titulo='Programas utilizados')

H(2, '2.8 Etapas de Construcción')
P('El trabajo se organizó por fases. Algunas se han ido haciendo en paralelo (la documentación, por ejemplo, desde '
  'el primer día) y el orden real no ha sido exactamente el previsto: el servidor estuvo listo bastante antes que '
  'los sensores, así que durante unas semanas trabajamos con datos simulados.')
T(['Fase', 'Qué se hace', 'Fechas', 'Estado'], [
    ['1. Organización', 'Revisar el material del centro, decidir qué se mide y repartir el trabajo', 'Septiembre-octubre de 2026', 'Hecha. Cronograma: [COMPLETAR: reparto de tareas entre los dos]'],
    ['2. Banco de pruebas del nodo', 'Identificar la placa, compilar el firmware, probar la radio y leer los sensores en la mesa', 'Desde el 26-10-2026', 'En curso: radio probada; sensores pendientes'],
    ['3. Red y servidor', 'Raspberry en la VLAN 500, Docker, ChirpStack, firewall y gateway', '29-10-2026 y 12-11-2026', 'Hecha'],
    ['4. Base de datos y web', 'Guardar las medidas, web en tiempo real, gráficas, CSV y copias de seguridad', 'Del 29-10-2026 al 12-11-2026', 'Hecha con datos simulados; falta ajustar colores con datos reales'],
    ['5. Acceso remoto', 'Tailscale, web pública y permisos del coordinador TIC', '26-10-2026 y 29-10-2026', 'Hecha'],
    ['6. Montaje e instalación exterior', 'Conexionado de los sensores, sondas en el depósito, gateway en el mástil y pruebas de campo', 'Desde el 13-11-2026', '[COMPLETAR: fechas reales del montaje]'],
    ['7. Ampliaciones', 'Alarmas con actuador por LoRaWAN y cambio de intervalo por radio', '—', 'No realizadas (ver conclusiones)'],
    ['8. Documentación', 'Memoria, planos y guías', 'Todo el proyecto', 'En curso'],
], anchos=[3.4, 5.6, 3.2, 3.8], titulo='Fases del proyecto', tam=9)

H(3, 'Fase 1. Organización y decisiones de diseño')
P('Lo primero fue ver qué material había en el centro y qué queríamos medir. De esas primeras reuniones salieron '
  'las decisiones que marcan el proyecto: no medir la conductividad, colgar las sondas directamente dentro del '
  'depósito en vez de hacer una cámara de medida, y meter todo el servidor en la Raspberry con una web propia en '
  'vez de usar un PC con Grafana (29-09-2026). Más adelante se cerraron la red (23-10-2026) y el acceso desde fuera '
  '(26-10-2026).')

H(3, 'Fase 2. Banco de pruebas del nodo')
P('Antes de tener nada montado comprobamos todo lo que se podía comprobar sin hardware: que el firmware compilaba '
  'y que el mensaje que arma el nodo lo entiende el servidor (apartado 5). Después identificamos la placa por su '
  'serigrafía y la probamos suelta en la mesa. Para eso hubo que hacer una versión del firmware «de banco», porque '
  'con la placa suelta el pin del puente de calibración quedaba al aire y el nodo entraba siempre en modo '
  'calibración.')
P('La primera prueba de radio fue ver si los intentos de unirse a la red llegaban al gateway: llegaban con el '
  'CRC correcto, así que la parte de radio funcionaba. Lo que costó más fue que el nodo recibiera la respuesta, '
  'como se cuenta en la fase 3.')
P('El 25-11-2026 dejamos lista la versión real del firmware (entorno `lilygo_t3_simple`). Revisamos sus pines uno '
  'a uno contra la serigrafía de la placa y encontramos un fallo: dos pines de los antiguos conmutadores de '
  'sensores seguían apuntando a IO4 e IO25, que en el montaje simple son la presencia de agua y el control del '
  'RS485, y al «encender los sensores» dejaban el RS485 transmitiendo. Se corrigió y los cuatro entornos compilan. '
  'Además se amplió el modo calibración con comandos nuevos (apartado 2.10) y se añadió un pequeño programa en el PC '
  '(`calibrar.py`) que manda esos comandos por el puerto serie.')
FOTO('La LILYGO en el banco de pruebas conectada al PC por USB, con el monitor serie en la pantalla.',
     'Pruebas del nodo en el aula')
FOTO('Captura del monitor serie de la LILYGO con el mensaje «Join OK» y un envío.',
     'Monitor serie del nodo: join correcto y envío', alto=5.0)

H(3, 'Fase 3. Red y servidor en la Raspberry Pi 5')
P('El 29-10-2026 pusimos en marcha la Raspberry en el aula, conectada a una toma de la VLAN 500. Al principio había '
  'cogido una dirección por DHCP (172.16.50.27) y la localizamos mirando la tabla ARP del PC. Le pusimos la IP fija '
  '172.16.50.3 con un script que lee los datos de red de un único fichero, comprobando antes que nadie usaba esa '
  'dirección, y con teclado y monitor a mano por si nos quedábamos fuera.')
P('Después lanzamos el script de instalación, que lo hace todo de una vez: actualiza el sistema, instala Docker, '
  'configura la red y el servidor de hora, genera las contraseñas, arranca los contenedores, da de alta la '
  'aplicación y el nodo en ChirpStack, pone el firewall, programa la copia diaria e instala Tailscale.')
P('El gateway lo configuramos el 12-11-2026 con WinBox, la herramienta de MikroTik. Venía de fábrica preparado para '
  'otra cosa (red privada y filtrado por dirección) y hubo que cambiarle tres o cuatro parámetros. Ese mismo día '
  'conseguimos el primer join completo del nodo, después de tocar un ajuste de ChirpStack y de hacer el join en SF12.')
FOTO('Captura de WinBox con la tarjeta LoRa del wAP LR8 activa (status Active, servidor chirpstack, network public).',
     'Configuración LoRa del gateway en WinBox', alto=5.5)
FOTO('Captura de ChirpStack con el gateway en línea y el nodo dado de alta, con los últimos mensajes recibidos.',
     'ChirpStack: gateway y nodo dados de alta', alto=5.5)

H(3, 'Fase 4. Base de datos y web')
P('Con el servidor en marcha probamos la cadena completa con mensajes simulados: llegaban a la base de datos con la '
  'hora en UTC y aparecían en la web al momento. También probamos que no se perdía nada parando a propósito el '
  'programa que guarda los datos, y que la copia de seguridad se podía restaurar. La web se rediseñó el 12-11-2026: '
  'selector de periodos, descarga en CSV, modo claro y oscuro, el logo del centro y la hora de Madrid.')

H(3, 'Fase 5. Acceso remoto')
P('La idea inicial era usar un nombre de DuckDNS y abrir el puerto 443 en el router del instituto, pero el centro no '
  'puede abrir puertos. Lo resolvimos con Tailscale Funnel: la Raspberry abre ella una conexión hacia fuera y por '
  'esa conexión entra la web. El coordinador TIC nos dio permiso para usarlo y dejó las dos direcciones IP fuera del '
  'DHCP (29-10-2026). La parte de administración (ChirpStack y SSH) no se publica: solo se llega con Tailscale '
  'instalado y con la cuenta del equipo.')

H(3, 'Fase 6. Montaje e instalación exterior')
P('El 13-11-2026 cerramos el esquema de conexionado definitivo, con todo leído directamente por la LILYGO. El '
  '17-11-2026 se decidió el depósito (bidón de 25 L) y que no habría caudalímetro, con la bomba fuera del bidón. El '
  '24-11-2026 pasamos el montaje a la protoboard que tenemos pegada dentro de la caja estanca y escribimos una guía '
  'cable a cable, con los colores reales de cada sensor y qué medir con el polímetro en cada paso. Ese mismo día, '
  'con la foto de la placa, ajustamos los nombres de los pines a su serigrafía. El 25-11-2026 se preparó la guía '
  'de calibración de todos los sensores.')
P('A partir de ahí el trabajo es de taller: soldar las tiras de pines de la LILYGO, pinchar cada sensor en la '
  'protoboard, colgar las sondas en el bidón, grabar el firmware real, calibrar, subir el gateway al mástil y dejar '
  'el sistema una semana midiendo.')
P('[COMPLETAR: contar aquí cómo fue el montaje real: en qué orden se conectaron los sensores, qué costó más y cuánto '
  'se tardó]')
FOTO('El conexionado del nodo terminado: la protoboard dentro de la caja estanca, con la LILYGO, el conversor del '
     'nivel, la placa del pH, la del SEN0204, las resistencias y el módulo RS485.', 'Conexionado del nodo terminado')
FOTO('El bidón de 25 L con las sondas colgadas del tapón (pH y oxígeno), el sensor de nivel en el fondo y el sensor de '
     'presencia pegado por fuera.', 'Sondas instaladas en el bidón')
FOTO('La bomba de recirculación fuera del bidón, con la manguera de aspiración y la de retorno entrando por arriba.',
     'Bomba de recirculación y sus dos mangueras', alto=5.5)
FOTO('La caja estanca de la alimentación con la fuente de 12 V y el cargador USB con batería de respaldo, y la '
     'regleta conectada a la línea del inversor.', 'Alimentación del nodo', alto=5.5)
FOTO('Vista desde la azotea hacia el depósito (o al revés), para que se vea que hay visión directa entre el gateway '
     'y el nodo.', 'Visión directa entre el gateway y el punto de medida', alto=5.5)

H(2, '2.9 Materiales Usados')
P('Estos son los materiales que se usan de verdad en el montaje final. Todo estaba ya en el centro o se ha '
  'reaprovechado, menos el módulo RS485 y algún componente pequeño.')
T(['Cant.', 'Material', 'Modelo', 'Uso'], [
    ['1', 'Placa del nodo', 'LILYGO T3 V1.6.1 (ESP32 + SX1276, 868 MHz) con su antena', 'Lee los sensores y envía por LoRaWAN'],
    ['1', 'Gateway LoRaWAN', 'MikroTik wAP LR8 kit (con fuente de 24 V e inyector PoE)', 'Recibe la radio y reenvía a la Raspberry'],
    ['1', 'Servidor', 'Raspberry Pi 5 de 4 GB', 'Servidor LoRaWAN, base de datos y web'],
    ['1', 'Tarjeta de memoria', 'microSD de 64 GB', 'Sistema y datos de la Raspberry'],
    ['1', 'Fuente de la Raspberry', 'Fuente oficial Raspberry Pi de 27 W USB-C', 'Alimentación del servidor'],
], anchos=[1.2, 3.4, 6.6, 4.8], titulo='Equipos principales')
T(['Cant.', 'Material', 'Modelo', 'Uso'], [
    ['1', 'Sensor de oxígeno disuelto y temperatura', 'DFRobot SEN0681 (RS485, 10-30 V)', 'Oxígeno y temperatura del agua'],
    ['1', 'Sonda de pH con su placa', 'DFRobot SEN0169-V2', 'pH, en inmersión continua'],
    ['1', 'Transmisor de nivel con conversor', 'DFRobot KIT0139 (4-20 mA, 0-5 m)', 'Nivel del depósito'],
    ['1', 'Sensor de presencia de agua', 'DFRobot SEN0204 (sin contacto)', 'Alarma de nivel mínimo'],
], anchos=[1.2, 4.6, 5.4, 4.8], titulo='Sensores')
T(['Cant.', 'Material', 'Uso'], [
    ['1', 'Módulo conversor RS485 a TTL de 3,3 V (tipo MAX3485) [COMPLETAR: modelo]', 'Leer el SEN0681 desde la LILYGO'],
    ['1', 'Resistencia de 27 kΩ', 'Divisor de la salida del SEN0204 (en serie)'],
    ['1', 'Resistencia de 10 kΩ', 'A masa en el divisor del SEN0204'],
    ['1', 'Cable dupont hembra-hembra', 'Puente de calibración (IO15 a GND al arrancar)'],
    ['1', 'Protoboard (de las de Arduino), pegada dentro de la caja estanca', 'Soporte del conexionado: + de arriba 12 V, + de abajo 3V3, las dos − a masa'],
    ['8', 'Cables dupont macho-hembra', 'De la protoboard a los pines de la LILYGO'],
    ['—', 'Cables dupont macho-macho y cable rígido', 'Puentes y bornas del conversor del nivel'],
    ['1', 'Caja estanca del nodo [COMPLETAR: medidas y grado de protección]', 'Proteger la electrónica'],
    ['1', 'Caja estanca de la alimentación [COMPLETAR: medidas y grado de protección]', 'Fuente de 12 V y cargador USB, aparte del nodo'],
], anchos=[1.2, 8.8, 6.0], titulo='Pequeño material del nodo')
T(['Cant.', 'Material', 'Uso'], [
    ['1', 'Fuente de 12 V de PC adaptada (más de 1 A)', 'Alimentar el SEN0681, el KIT0139 y el SEN0204'],
    ['1', 'Cargador USB de 5 V con batería de respaldo [COMPLETAR: modelo]', 'Alimentar la LILYGO por su conector USB'],
    ['1', 'Cable USB de datos', 'Alimentación y programación de la LILYGO'],
    ['1', 'Regleta de enchufes', 'Conexión a la línea de 230 V del inversor solar del centro'],
    ['2', 'Latiguillos de red Cat6', 'Raspberry al switch e inyector PoE al switch'],
    ['[COMPLETAR: metros]', 'Cable de red Cat6 de exterior', 'Bajada desde el gateway del mástil hasta el inyector'],
    ['—', 'Abrazaderas o bridas de acero inoxidable', 'Sujetar el gateway al mástil'],
], anchos=[2.2, 7.3, 6.5], titulo='Alimentación y red')
T(['Cant.', 'Material', 'Uso'], [
    ['1', 'Bidón de plástico de 25 L con tapón de rosca (reaprovechado)', 'Contiene el agua y todas las sondas'],
    ['1', 'Bomba de recirculación [COMPLETAR: modelo]', 'Mueve el agua. Va aparte, fuera del bidón y con su propia alimentación'],
    ['—', 'Manguera y abrazaderas', 'Aspiración y retorno de la bomba, entrando al bidón por arriba'],
    ['1', 'Silicona neutra', 'Sellar por fuera los pasos de cable del tapón'],
], anchos=[1.2, 8.3, 6.5], titulo='Parte hidráulica')
T(['Material', 'Uso'], [
    ['Soluciones tampón de pH 7 y pH 4', 'Calibrar la sonda de pH en dos puntos'],
    ['Agua destilada y vasos', 'Enjuagar la sonda entre un tampón y otro'],
    ['Polímetro', 'Comprobar tensiones antes de conectar nada a la LILYGO'],
    ['Soldador, estaño, pelacables, alicates y destornilladores', 'Soldar las tiras de pines de la LILYGO y estañar las puntas de los cables de los sensores'],
    ['Cinta aislante o de carrocero', 'Marcar las líneas de 12 V y 3V3 de la protoboard y etiquetar los dupont'],
    ['PC con PlatformIO, WinBox y cliente SSH', 'Programar la LILYGO y configurar el gateway y la Raspberry'],
    ['Herramientas y equipos de protección para el trabajo en la azotea [COMPLETAR: los que se usaron]', 'Montaje del gateway en el mástil'],
], anchos=[8.5, 7.5], titulo='Consumibles, herramientas e instrumentos')
H(3, 'Material previsto que al final no se usa')
P('Del diseño inicial se han quedado fuera varias cosas. Las dejamos anotadas porque explican la diferencia entre '
  'los primeros esquemas y lo que hay montado:')
B([
    'Convertidor analógico-digital ADS1115 y aislador de señal para el pH: se leen el pH y el nivel con las entradas '
    'analógicas del propio ESP32.',
    'Reductor de 12 V a 5 V y conmutadores con MOSFET para apagar los sensores: la LILYGO va por USB y los sensores '
    'están siempre alimentados.',
    'Panel solar de 50 W, regulador MPPT y batería LiFePO4 propios: se usa la corriente del inversor solar del centro.',
    'Sonda de conductividad y su placa.',
    'MOSFET y diodo para controlar la bomba desde el nodo.',
    'Medida de la tensión de batería: como el nodo ya no va con batería propia, ese campo del mensaje va vacío.',
])

H(2, '2.10 Técnicas Constructivas')
H(3, 'Conexionado del nodo')
P('La regla que hemos seguido en todo el conexionado es que a ningún pin de la LILYGO le puede llegar más de 3,3 V. '
  'El problema es que varios sensores trabajan a 12 V, así que cada señal se adapta de la forma más sencilla que '
  'encontramos, con resistencias (cálculos en el Anexo I y esquemas en los planos 3 y 3B).')
P('Todo se monta sobre una protoboard de las de Arduino pegada dentro de la caja estanca del nodo. Las líneas de '
  'alimentación se reparten así: la **+ de arriba** lleva los 12 V de la fuente, la **+ de abajo** los 3,3 V de la '
  'LILYGO y las dos **−** son masa, unidas con un puente. Cada señal va en su propia columna y la LILYGO queda fuera '
  'de la protoboard, conectada con cables dupont macho-hembra. Las dos líneas + se marcan con cinta («12 V» y '
  '«3V3»), porque un cable de 3V3 pinchado en la de 12 V quemaría la placa del pH, el conversor o la LILYGO.')
FIG(REPO + 'docs/img/montaje-visual.png', 'Montaje en la protoboard cable a cable, con los colores reales de cada '
    'sensor (plano 3B)', ancho=16.5)
T(['Dónde en la protoboard', 'Qué se pincha', 'Pin de la LILYGO'], [
    ['+ de arriba (12 V)', 'Fuente amarillo · SEN0681 marrón · KIT0139 rojo fino · SEN0204 rojo', '—'],
    ['− de arriba (GND)', 'Fuente negro · SEN0681 negro · RS485 GND · conversor I− y GND · pH − · SEN0204 negro · 10 kΩ', '—'],
    ['+ de abajo (3V3)', 'RS485 VCC · conversor VCC · placa del pH +', '3.3V (dupont naranja)'],
    ['− de abajo (GND)', 'Puente desde la − de arriba', 'GND (dupont negro)'],
    ['Columnas 6, 7 y 8', 'RS485 DI, RO y DE+RE', 'IO13, IO14 e IO25'],
    ['Columna 11', 'KIT0139 negro + conversor I+', '—'],
    ['Columna 15', 'Conversor SIG', 'S_VN (GPIO39)'],
    ['Columna 19', 'Placa del pH, salida A', 'S_VP (GPIO36)'],
    ['Columnas 23 y 27', 'SEN0204 verde, divisor 27 kΩ / 10 kΩ', 'IO4 (desde la 27)'],
], anchos=[3.6, 8.6, 3.8], titulo='Reparto de la protoboard', tam=9)
B([
    '**pH**: la placa de la sonda se alimenta a 3,3 V desde la LILYGO, así su salida nunca pasa de 3,0 V y entra '
    'directa a la entrada analógica GPIO36 (S_VP).',
    '**Nivel**: el conversor SEN0262 se alimenta también a 3,3 V y entrega entre 0,48 y 2,40 V en GPIO39 (S_VN). El '
    'transmisor en sí va a 12 V.',
    '**Presencia de agua**: el SEN0204 necesita entre 5 y 24 V, y por USB el pin de 5 V de la LILYGO se queda en unos '
    '4,7 V, así que va a 12 V. Su salida vale lo mismo que su alimentación, y por eso pasa por un divisor de 27 kΩ y '
    '10 kΩ que la deja en unos 3,2 V antes de GPIO4.',
    '**Oxígeno**: el SEN0681 va a 12 V y sus dos hilos de datos (A y B) al módulo RS485, que se conecta a los pines '
    'GPIO13, GPIO14 y GPIO25 de la LILYGO.',
    '**Masa común**: el negativo de la fuente de 12 V se une al GND de la LILYGO. Sin eso las lecturas no tienen '
    'referencia.',
])
P('Los cables de los sensores son de hilos sueltos y no agarran en la protoboard, así que se estaña la punta de cada '
  'uno. El montaje se hace por pasos, un sensor cada vez y con todo desenchufado, y después de cada paso se mide '
  'con el polímetro: 12-13 V en la línea de arriba, unos 12 V en la columna 23 y unos 3,2 V en la 27 con agua '
  'delante del SEN0204. Antes de pinchar la LILYGO se comprueba en continuidad que no hay cortos entre las líneas y, '
  'con la fuente enchufada, que ningún dupont de los que van a sus pines pasa de 3,3 V. La guía completa paso a '
  'paso está en el repositorio (`docs/12-guia-montaje.md`, también en PDF).')
P('Hay dos cosas más que conviene saber de esta placa. No se le puede poner tarjeta microSD, porque el lector usa '
  'los mismos pines que el RS485. Y el GPIO12 se deja sin conectar, porque es un pin que el ESP32 mira al arrancar.')
H(3, 'Instalación de las sondas en el bidón')
B([
    'Las sondas entran de una en una por la boca del bidón y sus cables salen por tres agujeros del tapón, sellados '
    'con silicona por fuera. La de pH y la de oxígeno cuelgan con la punta a 8-10 cm del fondo, lejos del retorno '
    'de la bomba: el chorro y las burbujas falsean la medida del oxígeno.',
    'La sonda de oxígeno, con la parte sensible hacia abajo.',
    'El sensor de nivel, apoyado en el fondo y colgado de su propio cable.',
    'El sensor de presencia, pegado por fuera a unos 12 cm del fondo (nivel mínimo), sin metal cerca.',
    'Todos los agujeros van arriba, por encima del agua: tres en el tapón, dos para las mangueras de la bomba y '
    'cuatro respiraderos pequeños junto al asa, que hacen falta para que el KIT0139 mida bien.',
    'Los cables, sujetos con bridas para que no tiren de las sondas, y entrando en la caja siempre desde abajo, para '
    'que el agua de lluvia gotee y no entre.',
    'Cada cable, etiquetado en los dos extremos.',
])
H(3, 'Montaje del gateway en el mástil')
P('El gateway se configura y se prueba abajo, en la mesa, y a la azotea se sube solo a fijarlo y conectarlo. Va en '
  'lo alto del mástil, vertical (la antena interna es vertical), por encima del pretil y con el conector de red '
  'hacia abajo. El cable es Cat6 de exterior, con un bucle de goteo antes del conector, y baja protegido hasta el '
  'inyector PoE, que se queda dentro del edificio. El tramo completo desde el switch no puede pasar de 100 m. Antes '
  'de apretar del todo las abrazaderas se mira la señal que llega del nodo (RSSI y SNR) por si conviene girarlo o '
  'subirlo un poco.')
H(3, 'Configuración del gateway')
P('Se hace con WinBox, pegando los comandos en un terminal. Lo que se cambia es: el nombre del equipo, la ruta por '
  'defecto, los DNS, el servidor de hora (la Raspberry), y en la parte LoRa el servidor al que reenvía, el plan de '
  'canales europeo, el tipo de red (pública, que es la palabra de sincronización que usa LoRaWAN) y que reenvíe todo '
  'lo que llegue con el CRC correcto. Los comandos están en el Anexo IV.')
H(3, 'Puesta en marcha del servidor')
P('La Raspberry se instala con un único script que se puede volver a lanzar las veces que haga falta, porque se '
  'salta lo que ya está hecho. Las contraseñas se generan solas y se guardan en un fichero que no se sube al '
  'repositorio. Todos los servicios van en Docker Compose con reinicio automático, volúmenes con nombre para los '
  'datos y comprobaciones de salud.')
H(3, 'Programación del nodo')
P('El firmware se compila y se graba con PlatformIO por el cable USB. Hay varias configuraciones (entornos) del '
  'mismo código: la del montaje real, una para probar la placa suelta en la mesa y una que inventa datos realistas '
  'para probar el servidor y la web sin sensores. Las claves LoRaWAN van en un fichero aparte que tampoco se sube '
  'al repositorio.')
H(3, 'Calibración de los sensores')
P('Para calibrar se pone el puente de calibración (un dupont hembra-hembra entre IO15 y GND), se enciende y se '
  'abre el monitor serie. El nodo espera 60 segundos a que se estabilicen los sensores y luego acepta comandos. Lo '
  'que se calibra se guarda en la memoria flash del ESP32, así que no se pierde al apagar ni al volver a grabar el '
  'firmware. Los comandos se pueden escribir a mano o mandarlos con `calibrar.py` desde el PC: así una persona hace '
  'la parte física (mover la sonda, vaciar el bidón) y otra, o Claude Code en el PC, va mandando los comandos. '
  'Para el taller hicimos una checklist con dibujos de cada paso y una hoja de resultados '
  '(`docs/14-checklist-calibracion.md`, también en PDF); la explicación larga está en `docs/13-guia-calibracion.md`.')
FIG(REPO + 'docs/img/calib-flujo.png', 'Los siete pasos de la calibración en el taller', ancho=16)
FIG(REPO + 'docs/img/calib-puente-io15.png', 'Dónde va el puente de calibración (IO15 a GND) en la serigrafía de la placa', ancho=15)
FIG(REPO + 'docs/img/calib-pantallas.png', 'Lo que enseñan la pantalla OLED y el monitor serie en el modo calibración', ancho=15)
T(['Comando', 'Qué hace'], [
    ['`leer`', 'Una medida completa de todos los sensores'],
    ['`mv`', 'Tensiones crudas en los pines (pH en mV, nivel en mV y mA, presencia de agua 0/1), para comprobar el cableado'],
    ['`ph7` / `ph4`', 'Guarda el punto del tampón de pH 7 / pH 4'],
    ['`nivel0`', 'Guarda el cero del nivel con el bidón vacío'],
    ['`sal` / `sal0`', 'Lee la salinidad del SEN0681 / la pone a 0 (agua dulce)'],
    ['`o2_100` / `o2_cero`', 'Calibración del oxígeno al 100 % / a cero'],
    ['`ver` / `reset`', 'Enseña lo guardado / vuelve a la calibración de fábrica'],
    ['`salir`', 'Sale del modo calibración (después se quita el puente y se pulsa RST)'],
], anchos=[4.0, 12.0], titulo='Comandos del modo calibración', tam=9.5)
B([
    '**pH (dos puntos)**: la sonda en el tampón de pH 7, se espera a que `mv` no cambie y se escribe `ph7` (unos '
    '1500 mV); se enjuaga con agua destilada, se mete en el de pH 4 y se escribe `ph4` (unos 2000 mV). Se comprueba '
    'volviendo a cada tampón: tiene que dar 7,00 y 4,00 con ±0,1. Si la diferencia entre los dos puntos baja mucho '
    'de unos 450 mV, la sonda está gastada. Se repite cada mes.',
    '**Nivel**: con el bidón vacío y la sonda de pie en el fondo se escribe `nivel0`, y después se echa agua de 5 en '
    '5 L apuntando la lectura para ajustar el % de la web.',
    '**Presencia de agua**: solo se comprueba que da 1 con agua detrás de la pared y 0 sin ella; si no, se cambia la '
    'sensibilidad con el botón SET de su placa.',
    '**Oxígeno**: cuando tengamos el módulo RS485, se pone la salinidad a 0 (`sal0`), porque usamos agua de red, y '
    'se hace el punto del 100 % (`o2_100`) con la sonda al aire saturado de humedad. Se repite cada tres meses.',
])
FIG(REPO + 'docs/img/calib-ph.png', 'Calibración del pH con los tampones 7 y 4', ancho=15)
FIG(REPO + 'docs/img/calib-nivel.png', 'Cero del nivel con el bidón vacío y tabla de 5 en 5 L (con el SEN0204)', ancho=15)
FIG(REPO + 'docs/img/calib-oxigeno.png', 'Salinidad a 0 y punto del 100 % del sensor de oxígeno', ancho=15)
FOTO('Calibración del pH: la sonda dentro del vaso con la solución tampón y el monitor serie con la lectura.',
     'Calibración de la sonda de pH con soluciones tampón', alto=5.5)

H(2, '2.11 Bibliografía')
B([
    'DFRobot. Wiki del sensor de oxígeno disuelto por fluorescencia RS485 (SEN0681). https://wiki.dfrobot.com/sen0681/',
    'DFRobot. Tabla de registros Modbus del SEN0680 (versión de agua dulce del mismo sensor). https://wiki.dfrobot.com/sen0680/docs/21672',
    'DFRobot. Wikis del medidor de pH SEN0169-V2, del transmisor de nivel KIT0139 y del sensor de nivel sin contacto SEN0204. https://wiki.dfrobot.com',
    'LilyGO. Repositorio oficial de las placas LoRa, con el esquema T3_V1.6.1 y la definición de pines. https://github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series',
    'MikroTik. Ficha del wAP LR8 kit. https://mikrotik.com/product/wap_lr8_kit',
    'MikroTik. Documentación de RouterOS (apartado IoT, LoRa). https://help.mikrotik.com/docs/',
    'ChirpStack. Documentación del servidor LoRaWAN de código abierto, versión 4. https://www.chirpstack.io/docs/',
    'RadioLib. Librería de radio para microcontroladores, con LoRaWAN. https://github.com/jgromes/RadioLib',
    'LoRa Alliance. Especificación LoRaWAN 1.1 y parámetros regionales (EU863-870). https://lora-alliance.org',
    'Semtech. Hoja de características del SX1276/77/78/79. https://www.semtech.com',
    'ETSI EN 300 220. Dispositivos de corto alcance en la banda de 25 MHz a 1000 MHz.',
    'Cuadro Nacional de Atribución de Frecuencias (CNAF), nota de utilización nacional UN-39.',
    'Tailscale. Documentación de Funnel. https://tailscale.com/kb/1223/funnel',
    'Raspberry Pi. Documentación oficial. https://www.raspberrypi.com/documentation/',
    'Docker. Documentación de Docker Compose. https://docs.docker.com/compose/',
    'Timescale. Documentación de TimescaleDB. https://docs.timescale.com',
    'Eclipse Mosquitto. https://mosquitto.org',
    'FastAPI. https://fastapi.tiangolo.com',
    'Apache ECharts. https://echarts.apache.org',
    'Caddy. https://caddyserver.com/docs/',
    'PlatformIO. https://docs.platformio.org',
    'Repositorio del proyecto, con el código, los esquemas y las guías. https://github.com/cmaaraver/TFG-2-STI-',
    '[COMPLETAR: apuntes de los módulos del ciclo que se hayan consultado]',
])
