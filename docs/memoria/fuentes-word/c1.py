from lib import *
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

import os
# Rutas relativas a esta carpeta (docs/memoria/fuentes-word dentro del repositorio)
D = os.path.dirname(os.path.abspath(__file__)) + '/'
REPO = os.path.abspath(D + '../../..') + '/'
PLANOS = os.path.abspath(D + '../planos') + '/'

preparar()
cabecera_y_pie('Carlos Maraver Román y Rubén Trillo García   2ºSTI')

# ---------------------------------------------------------------- PORTADA
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(REPO + 'raspberry/web/static/logo-viveros.png', width=Cm(6))
P('C.P.I.F.P. LOS VIVEROS — SEVILLA', alin='c', tam=13)
P('Técnico Superior en Sistemas de Telecomunicaciones e Informáticos', alin='c', tam=12)
P('Proyecto final de ciclo · Curso 2026/2027', alin='c', tam=12)
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('SISTEMA DE TELEMETRÍA LoRaWAN PARA LA MONITORIZACIÓN DE LA CALIDAD DEL AGUA')
r.bold = True; r.font.size = Pt(24); r.font.color.rgb = AZUL
P('Oxígeno disuelto, pH, temperatura y nivel, con los datos en una web propia accesible desde fuera del centro',
  alin='c', tam=12, cursiva=True)
doc.add_paragraph()
FOTO('Foto general del proyecto para la portada: el depósito con las sondas y el nodo, o un montaje con el nodo, '
     'el gateway y la Raspberry.', 'Vista general del sistema montado', alto=7.5)
doc.add_paragraph()
T(['', ''], [
    ['Autores', 'Carlos Maraver Román y Rubén Trillo García'],
    ['Curso y grupo', '2º STI'],
    ['Tutor del proyecto', '[COMPLETAR: nombre del tutor]'],
    ['Fecha de entrega', '[COMPLETAR: fecha de entrega]'],
], anchos=[4.5, 11.5], tam=11)

# ---------------------------------------------------------------- 1. ÍNDICE
H(1, '1. Índice', salto=True)
indice()

# ---------------------------------------------------------------- 2. MEMORIA DESCRIPTIVA
H(1, '2. Memoria Descriptiva', salto=True)

H(2, '2.1 Datos del Proyecto')
T(['Dato', 'Descripción'], [
    ['Título', 'Sistema de telemetría LoRaWAN para la monitorización de la calidad del agua'],
    ['Autores', 'Carlos Maraver Román (responsable técnico) y Rubén Trillo García'],
    ['Ciclo formativo', 'Técnico Superior en Sistemas de Telecomunicaciones e Informáticos (2º curso)'],
    ['Centro', 'C.P.I.F.P. Los Viveros, Sevilla'],
    ['Destinatario', 'El propio centro: el sistema se queda instalado en Los Viveros'],
    ['Curso académico', '2026/2027'],
    ['Tutor', '[COMPLETAR: nombre del tutor]'],
    ['Emplazamiento', 'Nodo de medida en la zona exterior del centro donde está el tratamiento de aguas '
                      '[COMPLETAR: sitio exacto]; gateway en el mástil de la azotea; servidor en '
                      '[COMPLETAR: aula o rack donde está la Raspberry]'],
    ['Magnitudes medidas', 'Oxígeno disuelto, pH, temperatura del agua, nivel del depósito y presencia de agua'],
    ['Tecnología de radio', 'LoRaWAN 1.1 privado, banda EU868, activación OTAA, clase A'],
    ['Web de los datos', 'https://rpi-lora.tailc40e5c.ts.net (pública) y http://172.16.50.3 (dentro del instituto)'],
    ['Repositorio', 'https://github.com/cmaaraver/TFG-2-STI-'],
], anchos=[4.0, 12.0], titulo='Datos generales del proyecto')

H(2, '2.2 Objeto del Proyecto')
P('El objeto de este proyecto es diseñar, montar y poner en marcha un sistema que mide de forma continua la calidad '
  'del agua en el C.P.I.F.P. Los Viveros y que deja los datos guardados y a la vista de cualquiera que tenga el '
  'enlace, sin tener que ir hasta el depósito con un medidor de mano.')
P('Lo que hace el sistema, de principio a fin, es esto: un nodo colocado junto al depósito lee las sondas '
  '(oxígeno disuelto, pH, temperatura y nivel), manda las medidas por radio con LoRaWAN hasta un gateway '
  'situado en la azotea del instituto, y un servidor (una Raspberry Pi 5) las recibe, las guarda con su fecha y su '
  'hora en una base de datos y las enseña en una página web con tarjetas en tiempo real y gráficas del histórico. '
  'Esa web se puede abrir desde dentro del centro y también desde fuera, con el móvil y datos móviles.')
P('Además del sistema en sí, el proyecto tiene un objetivo de aprendizaje bastante claro: tocar en un solo trabajo '
  'casi todo lo que hemos visto en el ciclo (radiocomunicaciones, redes de datos, sistemas informáticos, '
  'instalaciones y algo de electrónica) y dejarlo documentado para que otro grupo o el propio centro lo pueda '
  'mantener o ampliar.')
B([
    'Medir oxígeno disuelto, pH, temperatura y nivel del depósito.',
    'Enviar las medidas por LoRaWAN en la banda libre de 868 MHz, sin depender de la WiFi del centro.',
    'Guardar cada medida con fecha y hora (siempre en UTC) en una base de datos propia.',
    'Enseñar los datos en una web propia, en tiempo real y con gráficas del histórico, y poder descargarlos en CSV.',
    'Que la web se vea desde fuera del instituto sin abrir ningún puerto en el router del centro.',
    'Avisar cuando algo va mal: depósito sin agua o fallo de un sensor.',
])

H(2, '2.3 Alcance del Proyecto')
P('El proyecto cubre la cadena completa, desde la sonda hasta la pantalla del móvil. Para que quede claro qué entra '
  'y qué no, lo separamos en tres bloques.')
H(3, 'Lo que incluye')
B([
    '**Nodo de medida**: una placa LILYGO T3 V1.6.1 (ESP32 con radio LoRa SX1276) con su firmware, que lee todos los '
    'sensores directamente, sin módulos intermedios salvo el del RS485.',
    '**Sensores**: oxígeno disuelto y temperatura (DFRobot SEN0681), pH (SEN0169-V2), nivel (KIT0139), presencia de '
    'agua (SEN0204).',
    '**Gateway LoRaWAN**: MikroTik wAP LR8 configurado con RouterOS y colocado en el mástil de la azotea.',
    '**Servidor**: Raspberry Pi 5 con todo en Docker (ChirpStack, Mosquitto, TimescaleDB, el programa que guarda '
    'los datos, la web y Caddy), con copia de seguridad diaria y arranque automático.',
    '**Red**: integración en la VLAN 500 del instituto con direcciones fijas, firewall y servidor de hora.',
    '**Acceso remoto**: web pública con Tailscale Funnel y acceso de administración solo para el equipo.',
    '**Documentación**: esta memoria, los planos, la guía de instalación y el código, todo en el repositorio.',
])
H(3, 'Lo que no incluye')
B([
    '**La conductividad** del agua. Estaba en el planteamiento inicial y se quitó (decisión del 29-09-2026).',
    '**El control de la bomba**. La bomba de recirculación va aparte, con su propia alimentación, y el nodo no la '
    'enciende ni la apaga. Tampoco se mide el caudal, porque no tenemos caudalímetro (decisión del 17-11-2026).',
    '**La presión** del agua en la tubería, que sí sale en el cartel de referencia: no tenemos ese sensor.',
    '**La instalación solar y el inversor** de los que sale la corriente de 230 V. Son del centro y ya estaban; '
    'nosotros solo enchufamos a esa línea.',
    '**La red del instituto** (switches, router, VLAN). La administra el coordinador TIC; nosotros solo usamos dos '
    'tomas y dos direcciones IP.',
    'Las **alarmas automáticas con actuador** (relé por LoRaWAN) y el cambio del intervalo de envío por radio. Están '
    'pensados como ampliación y se explican en las conclusiones.',
])
H(3, 'Estado a la fecha de redacción')
P('Esta memoria se ha empezado a escribir con el proyecto a medias (13-11-2026), así que hay partes terminadas y '
  'partes que todavía hay que cerrar. Las que faltan están marcadas en amarillo a lo largo del documento para '
  'completarlas con los datos reales.')
T(['Parte', 'Estado', 'Comentario'], [
    ['Servidor en la Raspberry Pi 5', 'Hecho', 'En marcha desde el 29-10-2026. Arranca solo tras un reinicio (comprobado dos veces)'],
    ['Red (VLAN 500, IP fijas, firewall)', 'Hecho', 'Confirmado con el coordinador TIC el 29-10-2026'],
    ['Web pública y acceso remoto', 'Hecho', 'Tailscale Funnel funcionando; comprobada desde fuera del centro'],
    ['Gateway wAP LR8 configurado', 'Hecho', 'Configurado y dado de alta el 12-11-2026; falta subirlo al mástil'],
    ['Enlace de radio nodo → gateway', 'Hecho en pruebas', 'Join y envíos correctos desde el aula, con la señal muy justa'],
    ['Firmware del nodo', 'Hecho', 'Compila en todos los entornos; ahora mismo está grabada la versión con datos simulados'],
    ['Conexionado de los sensores', 'En curso', 'Esquema cerrado el 13-11-2026; falta conseguir el módulo RS485'],
    ['Calibración del pH', 'Pendiente', 'Con tampones de pH 7 y pH 4'],
    ['Gateway en el mástil de la azotea', 'Pendiente', '[COMPLETAR: fecha de montaje en la azotea]'],
    ['Pruebas de una semana con sensores reales', 'Pendiente', '[COMPLETAR: fechas y resultado de la semana de pruebas]'],
], anchos=[5.3, 2.7, 8.0], titulo='Estado de cada parte del proyecto')

H(2, '2.4 Antecedentes')
P('El punto de partida es el cartel «Proyecto de innovación colaborativo en digitalización aplicada» que nos dio el '
  'propio centro como referencia. Dibuja un depósito con sensores de nivel (ultrasónico), temperatura, presión, pH y '
  'flujo, conectados a un sistema de adquisición y control con una pantalla local opcional, que manda los datos a '
  'Internet (en el cartel, con un símbolo de WiFi) para verlos en una aplicación móvil y en una plataforma web y '
  'guardarlos en un servidor con base de datos para el histórico y el análisis.')
FIG(REPO + 'docs/img/cartel-referencia.jpg', 'Cartel de referencia del centro: «Proyecto de innovación colaborativo '
    'en digitalización aplicada»', ancho=16.0)
P('Nuestro TFG sigue esa misma idea, pero no es una copia exacta del cartel. Lo hemos llevado a una instalación real '
  'en el exterior con el material que tenemos y con las limitaciones de la red del centro, y preferimos explicar las '
  'diferencias que hacer como que no existen. Los dos cambios de fondo son sustituir la WiFi por una red LoRaWAN '
  'privada y añadir la medida del oxígeno disuelto. La tabla compara cada bloque del cartel con lo que hemos hecho.')
T(['Bloque del cartel', 'Nuestro sistema', '¿Coincide?'], [
    ['Depósito con tubería de salida', 'Bidón de plástico de 25 L con las sondas colgadas dentro; la bomba, aparte y '
     'fuera del bidón, recircula el agua con dos mangueras', 'En parte'],
    ['Sensor de nivel ultrasónico', 'KIT0139: transmisor sumergible de 4-20 mA en el fondo, que mide la presión del '
     'agua y la pasa a nivel (en la web, en % del bidón). El SEN0204 avisa además del nivel mínimo', 'El dato sí, el '
     'tipo de sensor no'],
    ['Sensor de temperatura', 'La da el SEN0681, en el mismo cuerpo que el oxígeno', 'Sí'],
    ['Sensor de presión', 'No hay sensor de presión de tubería. El KIT0139 mide presión, pero solo se usa para sacar '
     'el nivel', 'No'],
    ['Sensor de pH', 'SEN0169-V2, sonda industrial de inmersión continua', 'Sí'],
    ['Sensor de flujo', 'No hay caudalímetro (17-11-2026). El mensaje deja el caudal como «sin dato» por si se añade', 'No'],
    ['(no aparece)', 'Oxígeno disuelto con el SEN0681', 'Lo añadimos'],
    ['Sistema de adquisición y control', 'LILYGO T3 V1.6.1 (ESP32 con radio LoRa). Lee y envía, pero no controla '
     'nada: la bomba va aparte', 'Adquisición sí, control no'],
    ['Pantalla local (opcional)', 'Pantalla OLED de la LILYGO con el logo, la fase del ciclo y el estado del envío, '
     'no las medidas', 'En parte'],
    ['Comunicación por WiFi', 'LoRaWAN en 868 MHz hasta el gateway de la azotea y cable hasta la red del centro', 'Cambiado a propósito'],
    ['Internet', 'Salida del instituto con Tailscale Funnel, sin abrir puertos', 'Sí, por otro camino'],
    ['Servidor y base de datos', 'Raspberry Pi 5 en el instituto con TimescaleDB y copia diaria', 'Sí'],
    ['Plataforma web', 'Web propia en tiempo real con gráficas del histórico y descarga en CSV', 'Sí'],
    ['Aplicación móvil', 'No hay app: la misma web se adapta al móvil y se abre sin instalar nada', 'En parte'],
], anchos=[4.0, 8.9, 3.1], titulo='El cartel de referencia comparado con nuestro sistema', tam=9)
P('El motivo del cambio a LoRaWAN es práctico. El punto de medida está fuera del edificio, y allí la WiFi llega mal o '
  'no llega. LoRa trabaja en 868 MHz, atraviesa mejor los obstáculos y con muy poca potencia cubre distancias que '
  'para la WiFi son imposibles, a cambio de mandar muy pocos datos. Como nosotros solo mandamos 16 bytes cada 15 '
  'minutos, nos sobra. Además es una banda de uso libre, así que no hay que pagar ninguna tarifa ni depender de un '
  'operador, y al ser una red privada (con nuestro propio gateway y nuestro propio servidor) los datos no salen a '
  'ningún servicio de terceros.')
FOTO('Localización del punto de medida: zona del centro donde está el tratamiento de aguas y el depósito, vista '
     'general del sitio.', 'Zona del centro donde se instala el nodo de medida')
P('[COMPLETAR: dos o tres líneas describiendo el sitio: qué instalación de tratamiento de aguas hay, para qué se usa '
  'esa agua en el centro y por qué interesa vigilarla]')

H(3, 'Cómo ha cambiado el diseño por el camino')
P('El primer diseño era bastante más ambicioso que lo que se ha montado al final. Según íbamos viendo el material '
  'que había de verdad en el centro y las limitaciones de la red, lo fuimos simplificando. Creemos que merece la '
  'pena dejarlo escrito, porque casi todas las decisiones tienen un motivo y explican por qué el montaje es como es.')
T(['Tema', 'Diseño inicial', 'Lo que se ha hecho al final', 'Motivo'], [
    ['Conductividad', 'Sonda de conductividad con su placa', 'No se mide (29-09-2026)',
     'Se decidió no medirla. El hueco del mensaje se deja reservado por si se añade más adelante'],
    ['Sitio de las sondas', 'Cámara de medida aparte', 'Sondas colgadas dentro del depósito',
     'Menos piezas, menos fugas y nada que vaciar'],
    ['Servidor y gráficas', 'PC de datos con Grafana', 'Todo en la Raspberry Pi 5, con web propia (29-09-2026)',
     'Un solo equipo que mantener y una web hecha a nuestra medida'],
    ['Red', 'Red privada detrás de la Raspberry', 'VLAN 500 del instituto con IP fijas (23-10-2026)',
     'El centro nos dio una VLAN; ya no hace falta que la Raspberry haga de router'],
    ['Acceso desde fuera', 'DuckDNS abriendo el puerto 443', 'Tailscale Funnel (26-10-2026)',
     'El centro no puede abrir puertos en su router'],
    ['Bomba', 'Controlada por el nodo con un MOSFET', 'Aparte, con su alimentación (26-10-2026)',
     'Menos electrónica y menos riesgo'],
    ['Caudal', 'Caudalímetro YF-S201 en la tubería de la bomba', 'Sin caudalímetro; la bomba va fuera del bidón '
     'con dos mangueras (17-11-2026)', 'No lo tenemos. El hueco del caudal se queda reservado en el mensaje'],
    ['Depósito', 'Depósito opaco de unos 60 L', 'Bidón de plástico de 25 L con todos los agujeros arriba (17-11-2026)',
     'Es el que tenemos; el nivel se enseña en % del bidón'],
    ['Lectura analógica', 'Convertidor ADS1115 y aislador para el pH', 'Entradas analógicas de la propia LILYGO (13-11-2026)',
     'No disponíamos de esos módulos'],
    ['Alimentación', 'Panel de 50 W, regulador MPPT y batería LiFePO4 propios', 'Corriente de 230 V del inversor solar '
     'del centro: fuente de 12 V para los sensores y cargador USB con batería de respaldo para la LILYGO',
     'Se aprovecha la instalación solar que ya existe en vez de montar otra'],
], anchos=[2.4, 3.6, 4.6, 5.4], titulo='Cambios entre el diseño inicial y el montaje final', tam=9)

H(2, '2.5 Definición del Proyecto')
P('El sistema tiene cuatro partes que se ven bien en el esquema general: el nodo con las sondas, que está fuera; el '
  'gateway, en la azotea; el servidor, dentro del edificio, y el acceso desde Internet.')
FIG(PLANOS + 'plano-general.png', 'Esquema general del sistema (plano 1)', ancho=16.5)
H(3, 'Nodo de medida')
P('Es una placa LILYGO T3 V1.6.1, que lleva en la misma placa un microcontrolador ESP32, la radio LoRa SX1276 y una '
  'pantallita OLED. A ella llegan todas las sondas. El pH y el nivel entran por dos entradas analógicas, la presencia '
  'de agua por una entrada digital, y el sensor de oxígeno (que también da la temperatura) por '
  'RS485 con protocolo Modbus. Cada 15 minutos el nodo se despierta, mide, manda un mensaje de 16 bytes y se vuelve '
  'a dormir. En la pantalla se ve el logo de Los Viveros, en qué fase del ciclo está y cuánto falta para el '
  'siguiente envío.')
H(3, 'Gateway')
P('Un MikroTik wAP LR8, que es un gateway LoRaWAN de 8 canales en caja de exterior. Escucha lo que manda el nodo y lo '
  'reenvía por la red del instituto a la Raspberry (protocolo UDP, puerto 1700). No decide nada: es un puente entre '
  'la radio y la red de datos. Va en el mástil de la azotea para ver el bidón sin paredes por medio, y se '
  'alimenta por el mismo cable de red (PoE).')
H(3, 'Servidor')
P('Una Raspberry Pi 5 que hace todo el trabajo de servidor. Dentro lleva ChirpStack, que es el servidor LoRaWAN '
  '(comprueba las claves del nodo, descifra el mensaje y lo decodifica); Mosquitto, el broker MQTT por el que '
  'circulan los mensajes; un programa nuestro, el ingestor, que recoge cada medida y la guarda; la base de datos '
  'TimescaleDB, y la web. Todo va en contenedores Docker que arrancan solos si se va la luz.')
H(3, 'Web y acceso remoto')
P('La web es propia: tarjetas con el último valor de cada magnitud, que cambian de color según esté bien o haya que '
  'vigilarlo, y gráficas del histórico (1 hora, 5 horas, 24 horas, 1 semana, 30 días o un periodo a elegir), con '
  'descarga en CSV y modo claro y oscuro. Los datos nuevos aparecen sin recargar la página. Para verla desde fuera '
  'del instituto se usa Tailscale Funnel, que publica la web con HTTPS sin tocar el router del centro.')

H(2, '2.6 Condiciones de Funcionamiento del Sistema')
H(3, 'Ciclo de medida')
P('El nodo trabaja por ciclos. Entre uno y otro está en reposo profundo (deep sleep), que es cuando menos consume.')
N([
    'Se despierta y se une a la red LoRaWAN (join OTAA) o recupera la sesión que tenía guardada.',
    'Espera 60 segundos a que los sensores den un valor estable. El de oxígeno es el más lento: tarda hasta 60 s.',
    'Lee el resto de sensores, arma el mensaje de 16 bytes y lo envía.',
    'Enseña el resultado 5 segundos en la pantalla y se duerme hasta el siguiente ciclo.',
])
P('El intervalo por defecto es de **15 minutos**, lo que da 96 medidas al día.')
H(3, 'Magnitudes y márgenes')
T(['Magnitud', 'Sensor', 'Cómo llega al nodo', 'Resolución en el mensaje', 'Condiciones'], [
    ['Oxígeno disuelto', 'SEN0681', 'RS485, Modbus RTU (4800 baudios, 8N1, dirección 1)', '0,01 mg/L',
     'Alimentado a 12 V (admite 10-30 V). Trabaja de 0 a 40 °C'],
    ['Temperatura del agua', 'SEN0681', 'La da el mismo sensor de oxígeno', '0,01 °C', 'Se usa también para compensar el pH'],
    ['pH', 'SEN0169-V2', 'Tensión de 0 a 3,0 V en GPIO36', '0,01 pH', 'Placa alimentada a 3,3 V. La sonda tiene que estar siempre mojada'],
    ['Nivel', 'KIT0139', 'Lazo 4-20 mA convertido a 0,48-2,40 V en GPIO39', '1 mm', 'Margen de 0 a 5 m. Alimentado a 12 V. La web lo enseña en % del bidón de 25 L'],
    ['Presencia de agua', 'SEN0204', 'Entrada digital GPIO4 (divisor 27 kΩ / 10 kΩ)', 'Sí / no', 'Alimentado a 12 V. Detecta a través de paredes de hasta 13 mm'],
], anchos=[2.6, 1.9, 4.6, 2.4, 4.5], titulo='Magnitudes que mide el sistema', tam=9)
H(3, 'Avisos que da el sistema')
B([
    '**Depósito sin agua**: el sensor de presencia no detecta agua a la altura del nivel mínimo. Hay que rellenar, '
    'porque si el nivel baja más la punta de la sonda de pH se queda al aire y se estropea.',
    '**Fallo del sensor de oxígeno**: no contesta por RS485. En ese caso el pH se compensa con 25 °C fijos y se marca '
    'en el mensaje que la temperatura es la de por defecto.',
])
P('En la web, cada tarjeta se pone en verde («Correcto»), en naranja («Vigilar») o en rojo («Fuera de rango»). Los '
  'márgenes que hay puestos ahora son orientativos para agua de red y hay que ajustarlos cuando tengamos datos '
  'reales del depósito:')
T(['Magnitud', 'Correcto', 'Vigilar', 'Fuera de rango'], [
    ['Temperatura', 'Hasta 30 °C', 'De 30 a 35 °C', 'Más de 35 °C'],
    ['Oxígeno disuelto', '6 mg/L o más', 'De 4 a 6 mg/L', 'Menos de 4 mg/L'],
    ['pH', 'De 6,5 a 8,5', 'De 6 a 6,5 y de 8,5 a 9', 'Menos de 6 o más de 9'],
    ['Señal de radio (RSSI)', 'Mejor que −110 dBm', 'De −110 a −120 dBm', 'Peor que −120 dBm'],
    ['Relación señal/ruido (SNR)', 'Mejor que −7 dB', 'De −7 a −15 dB', 'Peor que −15 dB'],
], anchos=[4.4, 3.8, 4.0, 3.8], titulo='Márgenes de colores de la web (orientativos, pendientes de ajustar con datos reales)')
H(3, 'Radio')
B([
    'Banda **EU868**, LoRaWAN 1.1, activación **OTAA** (las claves no viajan nunca por el aire) y clase A (el nodo '
    'solo escucha justo después de transmitir, que es lo que menos gasta).',
    'El join se hace con el factor de ensanchamiento más robusto (**SF12**), porque desde el aula la cobertura iba al '
    'límite.',
    'En esta banda cada equipo puede transmitir como mucho el **1 % del tiempo**. Con un mensaje cada 15 minutos '
    'estamos muy por debajo (cálculo en el Anexo I).',
    'La LILYGO **nunca se enciende sin la antena puesta**: sin antena la radio se puede estropear.',
])
H(3, 'Alimentación')
P('El nodo no lleva ni panel ni batería propios. Se alimenta de la corriente de 230 V que saca el inversor de la '
  'instalación solar del centro, que tiene sus baterías. De una regleta salen dos cosas: una fuente de 12 V (una '
  'fuente de PC adaptada, de más de 1 A) para los sensores, y un cargador USB de 5 V con batería de respaldo para la '
  'LILYGO, que entra por su conector USB. Dentro de la caja del nodo no hay nada a 230 V: solo llegan los 12 V y el '
  'cable USB.')
P('El gateway se alimenta por PoE pasivo a 24 V con el inyector y la fuente que trae el kit, y la Raspberry con su '
  'fuente oficial de 27 W.')
H(3, 'Red y servidor')
B([
    'La Raspberry (172.16.50.3) y el gateway (172.16.50.2) tienen **IP fija** en la VLAN 500 del instituto, fuera del '
    'rango del DHCP para que nadie más las coja.',
    'La Raspberry necesita salida a Internet para la web pública, pero **no necesita ningún puerto abierto** hacia '
    'dentro.',
    'La hora se guarda **siempre en UTC** en la base de datos y la web la enseña en hora de Madrid. La Raspberry '
    'hace además de servidor de hora (NTP) para el gateway.',
    'Si el programa que guarda los datos se para, los mensajes **no se pierden**: se quedan en cola en el broker '
    'MQTT y entran en la base de datos cuando vuelve a arrancar.',
    'Todos los servicios arrancan solos después de un corte de luz y cada noche a las 3:00 se hace una copia de '
    'seguridad de las dos bases de datos.',
])
H(3, 'Condiciones ambientales')
B([
    'El sensor de oxígeno trabaja de 0 a 40 °C. En verano, en Sevilla, un bidón de 25 L al sol pasa de ahí enseguida, así '
    'que tiene que estar a la sombra.',
    'El gateway es de exterior (caja IP54, de −40 a +60 °C según la ficha de MikroTik).',
    'El bidón es opaco y va tapado, para que no entre luz y no salgan algas. Las sondas se limpian cada 2-4 semanas.',
    'La fuente de 12 V, el cargador y la regleta van a cubierto, protegidos de la lluvia.',
])
