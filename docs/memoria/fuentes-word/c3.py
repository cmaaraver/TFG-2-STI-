from lib import *
from c1 import REPO, D, PLANOS

H(1, '3. Anexos de la Memoria Descriptiva', salto=True)

# ================================================================ ANEXO I
H(2, '3.1 Anexo I. Cálculos justificativos')
P('Aquí están los cálculos que justifican los valores del conexionado y de la radio. Son cuentas sencillas, pero '
  'cada una responde a una pregunta concreta que nos hicimos al montar el nodo.')

H(3, 'Divisor de tensión del sensor de presencia de agua')
P('El SEN0204 va a 12 V y su salida en alto vale lo mismo que su alimentación. El pin de la LILYGO admite 3,3 V como '
  'máximo, así que hay que bajarla con un divisor de 27 kΩ en serie y 10 kΩ a masa:')
COD('V(GPIO4) = 12 V × 10 kΩ / (27 kΩ + 10 kΩ) = 12 × 0,27 = 3,24 V')
P('Queda por debajo de 3,3 V y bastante por encima de los 2,48 V a partir de los cuales el ESP32 lee un «1» (el 75 % '
  'de 3,3 V). Aunque la fuente de PC diera 12,5 V saldrían 3,38 V, que sigue siendo admisible para el pin. La '
  'corriente que pasa por el divisor es muy pequeña:')
COD('I = 12 V / 37 kΩ = 0,32 mA')

H(3, 'Medida de nivel con el lazo de 4-20 mA')
P('El transmisor da 4 mA con el depósito vacío y 20 mA con 5 m de agua. El conversor pasa esa corriente por una '
  'resistencia de 120 Ω:')
COD('''V mínima = 4 mA × 120 Ω = 0,48 V
V máxima = 20 mA × 120 Ω = 2,40 V''')
P('Las dos están dentro de lo que lee el ESP32. Para pasar de tensión a milímetros el firmware hace:')
COD('nivel (mm) = (V / 120 Ω − 4 mA) / 16 mA × 5000 mm')
P('Por ejemplo, con 0,80 V: 0,80 / 120 = 6,67 mA; (6,67 − 4) / 16 = 0,167; 0,167 × 5000 = 833 mm. Como el margen '
  'del sensor (5 m) es mucho mayor que la altura de nuestro depósito, solo usamos la parte baja de la escala: cada '
  'milímetro de agua son 0,384 mV, así que la medida de nivel sirve para ver tendencias (evaporación, rellenos) más '
  'que para medir al milímetro. Con la precisión del sensor (±0,5 % de 5 m, unos ±25 mm) en el bidón de 25 L el '
  'error es de unos ±1,5 L. La web lo enseña en % del bidón. [COMPLETAR: altura real del bidón y tensión que da el '
  'conversor con el bidón lleno]')

H(3, 'Calibración del pH en dos puntos')
P('La placa de la sonda da una tensión que varía en línea recta con el pH. Con dos tampones se saca la recta:')
COD('''pendiente = (7,00 − 4,00) / (V7 − V4)
pH = 7,00 + pendiente × (V − V7)''')
P('donde V7 y V4 son las tensiones leídas en cada tampón. Después el firmware corrige con la temperatura que da el '
  'sensor de oxígeno. [COMPLETAR: tensiones V7 y V4 obtenidas en la calibración]')

H(3, 'Tiempo en el aire y ciclo de trabajo')
P('En la banda de 868 MHz cada equipo puede ocupar el canal como mucho el 1 % del tiempo, es decir, 36 segundos '
  'cada hora. Nuestro mensaje son 16 bytes de datos más 13 de cabeceras LoRaWAN, 29 bytes en total. Con un ancho de '
  'banda de 125 kHz, codificación 4/5 y preámbulo de 8 símbolos, el tiempo en el aire según la fórmula de Semtech es:')
T(['Factor de ensanchamiento', 'Tiempo de un mensaje', 'En una hora (4 mensajes)', 'Ocupación', 'Margen sobre el 1 %'], [
    ['SF7', '67 ms', '0,27 s', '0,007 %', 'Muy sobrado'],
    ['SF9', '226 ms', '0,91 s', '0,025 %', 'Muy sobrado'],
    ['SF10', '412 ms', '1,65 s', '0,046 %', 'Muy sobrado'],
    ['SF12', '1.647 ms', '6,59 s', '0,18 %', 'Cinco veces por debajo'],
], anchos=[3.6, 3.0, 3.6, 2.4, 3.4], titulo='Tiempo en el aire del mensaje de 29 bytes')
P('Incluso en el peor caso (SF12) con un mensaje cada 15 minutos usamos menos de la quinta parte de lo permitido. '
  'Donde sí hay que tener cuidado es con el firmware de simulación, que envía cada 2 minutos: en SF12 serían '
  '30 × 1,65 = 49 segundos por hora, por encima de los 36 permitidos. Por eso esa versión es solo para pruebas '
  'cortas y no se deja en la maqueta.')

H(3, 'Enlace de radio')
P('La potencia máxima permitida en esta banda es de 25 mW de potencia radiada aparente (14 dBm). La sensibilidad '
  'del SX1276 con SF12 y 125 kHz está en torno a −136 dBm (hoja de características de Semtech) y admite una relación '
  'señal/ruido de hasta −20 dB. La pérdida en espacio libre a 868 MHz es:')
COD('''L (dB) = 32,44 + 20·log(f en MHz) + 20·log(d en km)
a 100 m:  32,44 + 58,77 − 20,00 = 71,2 dB
a 200 m:  32,44 + 58,77 − 13,98 = 77,2 dB''')
P('Con visión directa a 200 m, y contando 2 dBi de la antena del gateway, la señal esperada sería de unos '
  '14 + 2 − 77 = −61 dBm, con muchísimo margen. Lo que medimos en las pruebas desde el aula, con el gateway todavía '
  'dentro del edificio, fue muy distinto:')
T(['Medida', 'Valor', 'Límite en SF12', 'Margen'], [
    ['RSSI (nivel de señal)', '−134 dBm', '−136 dBm', '2 dB'],
    ['SNR (señal/ruido)', '−14 dB', '−20 dB', '6 dB'],
], anchos=[5.0, 3.5, 4.0, 3.5], titulo='Señal medida desde el aula el 12-11-2026 (gateway dentro del edificio)')
P('Es decir, con paredes por medio la señal llegaba decenas de dB por debajo de lo que daría el espacio libre y el '
  'enlace funcionaba al límite, solo en SF12. Esa es la justificación de subir el gateway al mástil de la azotea, donde ve el depósito '
  'sin obstáculos.')
T(['Medida con el gateway en el mástil', 'Valor'], [
    ['Distancia entre el nodo y el gateway', '[COMPLETAR: distancia en metros]'],
    ['RSSI', '[COMPLETAR: RSSI en dBm]'],
    ['SNR', '[COMPLETAR: SNR en dB]'],
    ['Factor de ensanchamiento con el que trabaja', '[COMPLETAR: SF]'],
    ['Mensajes perdidos en una semana', '[COMPLETAR: recibidos / esperados (96 al día)]'],
], anchos=[8.0, 8.0], titulo='Señal con la instalación definitiva (por completar)')

H(3, 'Consumo')
P('Como el nodo se alimenta de la línea de 230 V del inversor, el consumo ya no decide el tamaño de un panel ni de '
  'una batería, pero conviene saber qué gasta cada cosa. Los datos de fabricante que tenemos son estos:')
T(['Equipo', 'Consumo', 'De dónde sale el dato'], [
    ['Sensor de oxígeno SEN0681', '0,2 W', 'Ficha del fabricante'],
    ['Transmisor de nivel KIT0139', 'Hasta 0,24 W (20 mA a 12 V)', 'Calculado'],
    ['Gateway wAP LR8', '7 W como máximo', 'Ficha de MikroTik'],
    ['LILYGO (activa y en reposo)', '[COMPLETAR: consumo medido]', 'Medida propia'],
    ['Raspberry Pi 5 con todos los servicios', '[COMPLETAR: consumo medido]', 'Medida propia'],
    ['Conjunto del nodo en la toma de 230 V', '[COMPLETAR: consumo medido con un medidor de enchufe]', 'Medida propia'],
], anchos=[6.0, 5.5, 4.5], titulo='Consumos')
P('En el montaje simple los sensores están siempre alimentados (no hay conmutadores), así que los de 12 V gastan como '
  'mucho (0,2 + 0,24) W × 24 h ≈ 10,6 Wh al día, más lo poco que consume el sensor de presencia.')
P('La batería de respaldo del cargador USB solo mantiene la LILYGO. Si se va la corriente de 230 V el nodo sigue '
  'encendido y transmitiendo, pero los sensores de 12 V se quedan sin alimentación, de modo que el oxígeno y la '
  'temperatura llegarían con el aviso de fallo y el nivel y la presencia de agua no serían válidos. '
  '[COMPLETAR: capacidad de la batería de respaldo y autonomía comprobada]')

H(3, 'Volumen de datos')
COD('''96 medidas al día × 365 días = 35.040 filas al año
96 mensajes × 16 bytes = 1.536 bytes de datos útiles al día por radio''')
P('Para una tarjeta de 64 GB es una cantidad muy pequeña. Además se guarda el mensaje original completo de cada '
  'envío por si algún día hay que volver a procesarlo, y la base de datos calcula sola las medias por hora para que '
  'las gráficas largas carguen rápido.')

# ================================================================ ANEXO II
H(2, '3.2 Anexo II. Consideraciones sobre seguridad y salud', salto=True)
P('El proyecto no es una obra grande, pero junta tres cosas con las que hay que tener cuidado: electricidad, agua y '
  'un trabajo en la azotea. Para no liar ninguna avería ni hacernos daño hemos tenido en cuenta lo siguiente.')
T(['Riesgo', 'Dónde aparece', 'Medidas'], [
    ['Contacto eléctrico (230 V)', 'Regleta, fuente de 12 V y cargador',
     'Dentro de la caja del nodo no entra nada a 230 V: solo los 12 V y el USB. La fuente, el cargador y la regleta '
     'van a cubierto y lejos del agua. La fuente de PC adaptada se usa cerrada, con su carcasa, sin tocar su interior. '
     'Se trabaja siempre con todo desenchufado'],
    ['Agua y electricidad juntas', 'Depósito con sondas alimentadas',
     'A las sondas solo les llega muy baja tensión (12 V y 3,3 V). Cables hacia abajo para que goteen. No se '
     'manipulan las conexiones con las manos mojadas'],
    ['Caída a distinto nivel', 'Montaje del gateway en el mástil de la azotea',
     'Subir solo con permiso y acompañados por un profesor, nunca uno solo. No acercarse al borde ni subirse al '
     'pretil. No subir con viento fuerte, lluvia o tormenta. El gateway se sube ya configurado para estar arriba el '
     'tiempo justo. [COMPLETAR: medidas concretas que se tomaron: arnés, línea de vida, escalera]'],
    ['Caída de objetos', 'Trabajo en el mástil', 'Herramienta sujeta y la zona de abajo despejada mientras se trabaja'],
    ['Rayos y sobretensiones', 'Mástil y cable de bajada', 'No trabajar con tormenta. El mástil mantiene su puesta a tierra'],
    ['Quemaduras y humos', 'Soldadura de las resistencias y el diodo',
     'Soldador en su soporte, sitio ventilado, gafas al cortar patillas y lavarse las manos después'],
    ['Cortes y pinchazos', 'Pelar cables, cortar bridas y manguera', 'Herramienta en buen estado y cortar siempre hacia fuera'],
    ['Productos químicos', 'Soluciones tampón de pH',
     'Son poco peligrosas, pero no se beben ni se dejan sin etiquetar. Si salpican a los ojos, lavar con agua. No se '
     'devuelve al bote lo que ya se ha usado'],
    ['Daños a los equipos', 'LILYGO y sensores',
     'Nunca encender la LILYGO sin antena. Nunca más de 3,3 V en sus pines: se mide con el polímetro antes de '
     'conectar. La sonda de pH, siempre mojada'],
    ['Posturas y pantallas', 'Horas de programación y configuración', 'Descansos y una postura correcta delante del ordenador'],
], anchos=[3.2, 3.8, 9.0], titulo='Riesgos y medidas de prevención', tam=9)
H(3, 'Normativa que se ha tenido en cuenta')
B([
    'Ley 31/1995, de Prevención de Riesgos Laborales.',
    'Real Decreto 614/2001, sobre protección frente al riesgo eléctrico.',
    'Real Decreto 842/2002, Reglamento Electrotécnico para Baja Tensión.',
    'Real Decreto 2177/2004, sobre trabajos temporales en altura.',
    'Real Decreto 1215/1997, sobre utilización de los equipos de trabajo.',
    'Real Decreto 773/1997, sobre equipos de protección individual.',
    'Normas internas del centro para el uso de los talleres y el acceso a la azotea.',
])
H(3, 'Seguridad de los datos y de la red')
P('Como el sistema está conectado a la red del instituto y tiene una parte pública, también hemos cuidado la '
  'seguridad informática:')
B([
    'No se abre ningún puerto en el router del centro. La web sale por una conexión que inicia la Raspberry.',
    'Solo es pública la web de los datos. ChirpStack y el acceso por SSH solo funcionan para equipos del grupo con '
    'Tailscale.',
    'El firewall de la Raspberry solo admite SSH desde la VLAN 500 y la consulta de hora solo desde el gateway.',
    'Las claves LoRaWAN y las contraseñas no están en el repositorio.',
    'El sistema no guarda ningún dato personal: solo medidas del agua.',
])

# ================================================================ ANEXO III
H(2, '3.3 Anexo III. Gestión ambiental y de residuos')
P('El impacto ambiental del proyecto es pequeño, y de hecho su finalidad es ayudar a vigilar el agua. Aun así se '
  'generan algunos residuos durante el montaje y los habrá cuando el sistema se desmonte.')
T(['Residuo', 'Cuándo se genera', 'Qué se hace con él'], [
    ['Restos de cable, bridas, plásticos y embalajes', 'Durante el montaje', 'Contenedor de envases o punto limpio según el material'],
    ['Restos de estaño y componentes electrónicos sobrantes', 'Durante el montaje', 'Contenedor de residuos electrónicos del taller del centro'],
    ['Soluciones tampón usadas', 'En cada calibración', 'En las cantidades que usamos (unos mililitros) se diluyen con abundante agua; los botes vacíos, al contenedor correspondiente'],
    ['Agua del depósito', 'Al vaciarlo para limpiar', 'Es agua de red sin productos añadidos: se puede aprovechar para riego'],
    ['Equipos electrónicos (LILYGO, sensores, gateway, Raspberry, fuentes)', 'Al final de su vida útil', 'Son residuos de aparatos eléctricos y electrónicos (RAEE): punto limpio o gestor autorizado, nunca a la basura'],
    ['Batería de respaldo del cargador USB', 'Al final de su vida útil', 'Punto de recogida de pilas y baterías'],
    ['Sonda de pH agotada', 'Cuando deje de calibrar bien', 'Punto limpio'],
], anchos=[5.0, 3.5, 7.5], titulo='Residuos y su gestión', tam=9)
H(3, 'Criterios ambientales del diseño')
B([
    '**Reutilización**: casi todo el material ya estaba en el centro, y la fuente de 12 V es una fuente de PC '
    'reaprovechada.',
    '**Energía**: el nodo se alimenta de la instalación solar del centro. Entre medidas la LILYGO está en reposo '
    'profundo.',
    '**Radio**: se emite con muy poca potencia (25 mW como máximo) y menos del 0,2 % del tiempo.',
    '**Sin consumibles agresivos**: el sensor de oxígeno es óptico y no lleva electrolito ni membranas que cambiar.',
    '**Agua**: el circuito es cerrado; el agua sale del depósito y vuelve al mismo depósito.',
    '**Durabilidad**: los sensores se pueden desmontar y cambiar uno a uno sin tirar el resto.',
])
H(3, 'Normativa')
B([
    'Real Decreto 110/2015, sobre residuos de aparatos eléctricos y electrónicos.',
    'Real Decreto 106/2008, sobre pilas y acumuladores y la gestión ambiental de sus residuos.',
    'Ley 7/2022, de residuos y suelos contaminados para una economía circular.',
    'Directiva 2011/65/UE (RoHS), sobre sustancias peligrosas en aparatos eléctricos y electrónicos.',
])

# ================================================================ ANEXO IV
H(2, '3.4 Anexo IV. Programación y configuración del sistema', salto=True)
P('En este anexo está lo necesario para entender cómo está programado y configurado el sistema y para volver a '
  'ponerlo en marcha. El código completo está en el repositorio del proyecto.')
H(3, 'Organización del repositorio')
T(['Carpeta', 'Qué hay'], [
    ['`docs/`', 'Documentación: material, red, conexionado, formato del mensaje, guía de instalación y acceso desde Internet'],
    ['`firmware/nodo-agua/`', 'Programa de la LILYGO (PlatformIO): configuración de pines, sensores, LoRaWAN y pantalla'],
    ['`raspberry/`', 'Todo el servidor: script de instalación, Docker Compose, ChirpStack, base de datos, ingestor, web, red y copias'],
    ['`pruebas/`', 'Pruebas que se pueden hacer sin hardware'],
], anchos=[4.0, 12.0], titulo='Carpetas del repositorio')
H(3, 'Configuraciones del firmware')
T(['Entorno', 'Para qué'], [
    ['`lilygo_t3_simple`', 'El del montaje real: todo leído por la LILYGO. pH en GPIO36, nivel en GPIO39, presencia de agua en GPIO4, GPIO34 libre (sin caudalímetro), puente de calibración en GPIO15 y RS485 en GPIO13, 14 y 25. Join en SF12'],
    ['`lilygo_t3_banco`', 'Para probar la placa suelta en la mesa: no mira el puente de calibración'],
    ['`lilygo_t3_simulado`', 'Inventa valores realistas de todos los sensores y los envía cada 2 minutos, para probar el servidor y la web'],
    ['`lilygo_t3_v1_6_1`', 'El del diseño completo inicial, con convertidor ADS1115 y conmutadores. No se usa en el montaje final'],
], anchos=[4.0, 12.0], titulo='Entornos de compilación del firmware')
COD('''pio run -e lilygo_t3_simple -t upload      (grabar el firmware del montaje real)
pio device monitor                         (ver el monitor serie)''')
H(3, 'Formato del mensaje')
P('El nodo manda un mensaje binario de 16 bytes por el puerto 1 de LoRaWAN. Se hizo binario, y no de texto, '
  'para que ocupe lo mínimo y esté menos tiempo en el aire. Los valores van multiplicados por 100 para no mandar '
  'decimales. Cuando un sensor no da dato se manda un valor especial (0xFFFF) y la base de datos lo guarda vacío.')
T(['Byte', 'Campo', 'Tipo', 'Escala', 'Ejemplo'], [
    ['0', 'Versión del formato', 'Entero de 8 bits', '—', '2'],
    ['1', 'Avisos', '8 bits', 'bit 0: hay agua · bit 1: fallo del RS485 · bit 4: temperatura por defecto · bit 5: bomba sin caudal, siempre a 0 sin caudalímetro (los bits 2 y 3 eran del ADS1115 y de la batería y no se usan)', '0x01'],
    ['2-3', 'Temperatura del agua', 'Entero con signo', '× 100 °C', '2150 → 21,50 °C'],
    ['4-5', 'Oxígeno disuelto', 'Entero sin signo', '× 100 mg/L', '812 → 8,12 mg/L'],
    ['6-7', 'pH', 'Entero sin signo', '× 100', '734 → 7,34'],
    ['8-9', 'Reservado', 'Entero sin signo', 'Siempre 0xFFFF (era la conductividad)', '—'],
    ['10-11', 'Nivel', 'Entero sin signo', 'mm', '1250 → 1.250 mm'],
    ['12-13', 'Batería', 'Entero sin signo', 'mV (sin dato en el montaje final)', '—'],
    ['14-15', 'Caudal de la bomba', 'Entero sin signo', 'Siempre 0xFFFF (no hay caudalímetro)', '—'],
], anchos=[1.3, 3.6, 3.0, 5.3, 2.8], titulo='Formato del mensaje LoRaWAN (versión 2, 16 bytes)', tam=9)
P('En el servidor, un pequeño programa en JavaScript (`decoder.js`) que se carga en ChirpStack hace el camino '
  'contrario: coge los 16 bytes y devuelve los valores ya con sus unidades y sus nombres.')
H(3, 'Base de datos')
P('Hay tres tablas: `nodos` (los nodos dados de alta), `medidas` (una fila por cada mensaje recibido, con su hora, '
  'todos los valores, los avisos y la calidad de la señal con la que llegó) y `uplinks_raw` (el mensaje completo tal '
  'como llega, por si hay que volver a procesarlo). La tabla de medidas lleva un identificador único de cada mensaje '
  'que impide que se guarde dos veces.')
H(3, 'Configuración del gateway')
P('Comandos que se pegan en el terminal de WinBox (están guardados en `raspberry/red/wap-lr8.rsc`):')
COD('''/system identity set name=wap-lr8-tfg
/ip route add dst-address=0.0.0.0/0 gateway=172.16.50.1
/ip dns set servers=1.1.1.1,192.168.2.1
/system ntp client set enabled=yes servers=172.16.50.3
/iot lora disable [find]
/iot lora servers add name=chirpstack address=172.16.50.3 protocol=UDP up-port=1700 down-port=1700
:delay 5s
/iot lora set [find] servers=chirpstack channel-plan=eu-868 network=public forward=crc-validation
/iot lora enable [find]
/ip address set [find address="172.16.50.2/24"] interface=bridgeLocal''')
H(3, 'Puesta en marcha y comprobación del servidor')
COD('''cd ~/TFG/raspberry
./instalar.sh                       (instalación completa; se puede repetir)
sudo docker compose ps              (los 8 servicios tienen que salir en marcha)
curl http://127.0.0.1/api/salud     (tiene que contestar {"estado":"ok"})
sudo tailscale funnel status        (web pública activa)
./backup.sh                         (copia de seguridad a mano)''')
H(3, 'Mantenimiento')
T(['Tarea', 'Cada cuánto'], [
    ['Mirar la web: que llegan datos y que no hay avisos', 'A diario (basta con abrirla en el móvil)'],
    ['Limpiar las sondas con agua y un cepillo suave', 'Cada 2-4 semanas'],
    ['Rellenar el depósito', 'Cuando baje el nivel o salte el aviso de falta de agua'],
    ['Calibrar el pH con los tampones de 7 y 4', '[COMPLETAR: periodicidad que se decida, por ejemplo una vez al mes]'],
    ['Revisar conexiones, bridas y el estado de la caja', 'Cada trimestre y después de temporales'],
    ['Revisar la sujeción del gateway y su cable', 'Una vez al año'],
    ['Comprobar que la copia de seguridad se sigue haciendo', 'Una vez al mes'],
    ['Actualizar el sistema de la Raspberry', 'Cada trimestre'],
], anchos=[9.5, 6.5], titulo='Plan de mantenimiento')
