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
], anchos=[4.0, 12.0], titulo='Características de la LILYGO T3 V1.6.1 que usamos')
FOTO('La placa LILYGO T3 V1.6.1 con la antena puesta y la pantalla encendida (logo de Los Viveros y temporizador).',
     'Nodo LILYGO T3 V1.6.1 con la pantalla en marcha')

H(3, 'Sensor de oxígeno disuelto y temperatura: DFRobot SEN0681')
P('Es el sensor principal del proyecto y el que añadimos respecto al sistema de referencia. Mide el oxígeno disuelto '
  'por fluorescencia, así que no lleva ni membrana que cambiar ni electrolito, y da también la temperatura del agua. '
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
  'que tiene encima y da una corriente de 4 a 20 mA proporcional a la altura, de 0 a 5 metros. El kit trae un '
  'conversor que pasa esa corriente a tensión con una resistencia de 120 Ω. El cable lleva por dentro un tubito de '
  'aire para compensar la presión atmosférica, así que no se puede aplastar ni doblar fuerte.')

H(3, 'Sensor de presencia de agua: DFRobot SEN0204')
P('Es un sensor sin contacto que se pega por fuera de la pared del depósito y detecta si hay agua al otro lado, a '
  'través de paredes no metálicas de hasta 13 mm. Lo usamos como alarma de nivel mínimo: se pega a la altura por '
  'debajo de la cual la sonda de pH se quedaría en seco. Tenemos un SEN0509 de repuesto.')

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
P('El 13-11-2026 cerramos el esquema de conexionado definitivo, con todo leído directamente por la LILYGO. A partir '
  'de ahí el trabajo es de taller: montar las resistencias, conectar cada sensor, colgar las sondas en el '
  'bidón, calibrar el pH, subir el gateway al mástil y dejar el sistema una semana midiendo.')
P('[COMPLETAR: contar aquí cómo fue el montaje real: en qué orden se conectaron los sensores, qué costó más y cuánto '
  'se tardó]')
FOTO('El conexionado del nodo terminado: la LILYGO con los cables de los sensores, las resistencias y el '
     'módulo RS485.', 'Conexionado del nodo terminado')
FOTO('El bidón de 25 L con las sondas colgadas del tapón (pH y oxígeno), el sensor de nivel en el fondo y el sensor de '
     'presencia pegado por fuera.', 'Sondas instaladas en el bidón')
FOTO('La bomba de recirculación fuera del bidón, con la manguera de aspiración y la de retorno entrando por arriba.',
     'Bomba de recirculación y sus dos mangueras', alto=5.5)
FOTO('La fuente de 12 V, el cargador USB con batería de respaldo y la regleta conectada a la línea del inversor.',
     'Alimentación del nodo', alto=5.5)
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
    ['1', 'Puente (jumper)', 'Entrar en modo calibración (GPIO15 a masa)'],
    ['—', 'Placa de montaje, bornas y cables [COMPLETAR: sobre qué se ha montado: placa de topos, protoboard o regletas]', 'Soporte del conexionado'],
    ['1', 'Caja del nodo [COMPLETAR: tipo de caja y grado de protección]', 'Proteger la electrónica'],
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
    ['Soldador, estaño, pelacables, alicates y destornilladores', 'Montaje del conexionado'],
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
  'encontramos, con resistencias (cálculos en el Anexo I y esquema en el plano 3).')
B([
    '**pH**: la placa de la sonda se alimenta a 3,3 V desde la LILYGO, así su salida nunca pasa de 3,0 V y entra '
    'directa a la entrada analógica GPIO36.',
    '**Nivel**: el conversor del KIT0139 se alimenta también a 3,3 V y entrega entre 0,48 y 2,40 V en GPIO39. El '
    'transmisor en sí va a 12 V.',
    '**Presencia de agua**: el SEN0204 necesita entre 5 y 24 V, y por USB el pin de 5 V de la LILYGO se queda en unos '
    '4,7 V, así que va a 12 V. Su salida vale lo mismo que su alimentación, y por eso pasa por un divisor de 27 kΩ y '
    '10 kΩ que la deja en unos 3,2 V antes de GPIO4.',
    '**Oxígeno**: el SEN0681 va a 12 V y sus dos hilos de datos (A y B) al módulo RS485, que se conecta a los pines '
    'GPIO13, GPIO14 y GPIO25 de la LILYGO.',
    '**Masa común**: el negativo de la fuente de 12 V se une al GND de la LILYGO. Sin eso las lecturas no tienen '
    'referencia.',
])
P('Antes de enchufar la LILYGO se hacen dos comprobaciones con el polímetro: que la fuente de PC da entre 12 y 13 V '
  'en las bornas, y, con todo conectado y la LILYGO fuera, que ningún cable de los que van a sus pines pasa de 3,3 V.')
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
H(3, 'Calibración del pH')
P('La sonda de pH hay que calibrarla, porque cada sonda da una tensión un poco distinta y además estamos leyendo '
  'con el convertidor del ESP32, que es menos fino que uno dedicado. Se hace en dos puntos. Se pone el puente de '
  'calibración y se reinicia el nodo; por el monitor serie se mete la sonda en el tampón de pH 7 y se escribe '
  '`ph7`, se enjuaga con agua destilada, se mete en el de pH 4 y se escribe `ph4`. Los dos puntos se quedan '
  'guardados en la memoria del nodo aunque se apague. En ese mismo modo hay comandos para leer todos los sensores '
  'una vez.')
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
