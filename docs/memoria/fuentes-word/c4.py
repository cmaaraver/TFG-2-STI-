from lib import *
from c1 import REPO, D, PLANOS

WEB = '/mnt/project-files/tfg/web/'

# ================================================================ 4. PLANOS
H(1, '4. Planos', salto=True)
P('Los planos se han dibujado sin escala, porque son esquemas de bloques y de conexiones. Los ficheros editables '
  'están en el repositorio. Faltan por añadir los de situación, que se hacen sobre una foto o un plano del centro.')
T(['Plano', 'Contenido'], [
    ['Plano 1', 'Esquema general del sistema'],
    ['Plano 2', 'Plano de red: VLAN 500, direcciones IP y accesos'],
    ['Plano 3', 'Esquema de conexionado del nodo'],
    ['Plano 3B', 'Montaje en la protoboard de la caja estanca, cable a cable'],
    ['Plano 4', 'Instalación de las sondas en el depósito'],
    ['Plano 5', 'Flujo de datos y servicios del servidor'],
    ['Plano 6', 'Situación: ubicación del nodo, del gateway y del servidor en el centro (por completar)'],
    ['Plano 7', 'Recorrido del cable del gateway desde el mástil hasta el switch (por completar)'],
], anchos=[2.5, 13.5], titulo='Relación de planos')

H(3, 'Plano 1. Esquema general del sistema')
FIG(PLANOS + 'plano-general.png', 'Plano 1. Esquema general del sistema', ancho=16.5)

H(3, 'Plano 2. Plano de red')
FIG(PLANOS + 'plano-red.png', 'Plano 2. Red: VLAN 500, direcciones IP y accesos', ancho=16.5)
T(['Equipo', 'Interfaz', 'Dirección', 'Notas'], [
    ['Router del instituto', 'VLAN 500', '172.16.50.1', 'Puerta de enlace. No hace de servidor DNS'],
    ['MikroTik wAP LR8', 'bridgeLocal (puerto Ethernet, PoE)', '172.16.50.2/24 fija', 'Hora y servidor LoRa en 172.16.50.3'],
    ['Raspberry Pi 5', 'eth0', '172.16.50.3/24 fija', 'DNS 1.1.1.1 y 192.168.2.1'],
    ['Raspberry Pi 5', 'tailscale0', '100.x.y.z', 'Acceso del equipo por SSH y a ChirpStack'],
], anchos=[3.6, 4.6, 3.2, 4.6], titulo='Direccionamiento')
T(['Puerto', 'Protocolo', 'Servicio', 'Quién puede entrar'], [
    ['1700', 'UDP', 'Paquetes LoRa del gateway', 'Solo el gateway (172.16.50.2)'],
    ['123', 'UDP', 'Hora (NTP)', 'Solo el gateway'],
    ['22', 'TCP', 'SSH', 'Solo la VLAN 500 y los equipos del grupo por Tailscale'],
    ['80', 'TCP', 'Web de los datos', 'La VLAN 500; desde Internet, a través de Tailscale Funnel (HTTPS, 443)'],
    ['8443', 'TCP', 'ChirpStack', 'Solo los equipos del grupo por Tailscale'],
], anchos=[1.8, 2.2, 5.0, 7.0], titulo='Puertos que usa el servidor')

H(3, 'Plano 3. Esquema de conexionado del nodo', salto=True)
FIG(REPO + 'docs/img/conexionado-simple.png', 'Plano 3. Conexionado del nodo: todo leído por la LILYGO', ancho=16.5)
T(['Señal', 'Pin de la LILYGO', 'Va a', 'Notas'], [
    ['Alimentación', 'USB', 'Cargador de 5 V con batería de respaldo', 'El pin de 5 V no se usa'],
    ['3,3 V', '3V3', 'Placa del pH, conversor de 4-20 mA y módulo RS485', 'Es una salida de la placa'],
    ['Masa', 'GND', 'Negativo de la fuente de 12 V', 'Masa común de todo'],
    ['pH', 'S_VP (GPIO36)', 'Salida A de la placa del pH (0-3,0 V)', 'Entrada analógica'],
    ['Nivel', 'S_VN (GPIO39)', 'Salida SIG del conversor SEN0262 del KIT0139 (0,48-2,40 V)', 'Entrada analógica'],
    ['Presencia de agua', 'IO4 (GPIO4)', 'Cable verde de la placa del SEN0204 por 27 kΩ en serie y 10 kΩ a masa', 'Sensibilidad con el botón SET de la placa'],
    ['Libre', 'GPIO34', 'Sin conectar', 'Era el caudalímetro, que no tenemos'],
    ['Calibración', 'IO15 (GPIO15)', 'Puente a masa', 'Puesto al arrancar = modo calibración'],
    ['RS485', 'IO13, IO14 e IO25', 'DI, RO y DE/RE del módulo RS485', 'Si no lee, cruzar 13 y 14'],
    ['Radio y pantalla', 'Internos', '—', 'No se tocan'],
    ['Sin usar', 'GPIO12 y pin de 5 V', '—', 'GPIO12 es un pin de arranque'],
], anchos=[2.8, 3.2, 6.0, 4.0], titulo='Tabla de conexiones del nodo', tam=9)
T(['Cable del SEN0681', 'Función', 'Va a'], [
    ['Marrón', 'Alimentación (10-30 V)', '+12 V'],
    ['Negro', 'Masa', 'GND'],
    ['Amarillo', 'RS485 A', 'Borna A del módulo'],
    ['Azul', 'RS485 B', 'Borna B del módulo'],
], anchos=[4.5, 6.0, 5.5], titulo='Colores del cable del sensor de oxígeno')

H(3, 'Plano 3B. Montaje en la protoboard', salto=True)
FIG(REPO + 'docs/img/montaje-visual.png', 'Plano 3B. Montaje cable a cable en la protoboard de la caja estanca', ancho=16.5)
P('Las columnas son las de la mitad de arriba de la protoboard (filas a-e). La + de arriba es 12 V, la + de abajo '
  '3V3 y las dos − son masa. Si la protoboard está numerada de otra forma no pasa nada: lo que importa es que cada '
  'grupo vaya en su propia columna.')

H(3, 'Plano 4. Instalación de las sondas en el depósito', salto=True)
FIG(PLANOS + 'plano-sondas.png', 'Plano 4. Bidón de 25 L: sondas, bomba y agujeros', ancho=16.5)

H(3, 'Plano 5. Flujo de datos y servicios del servidor')
FIG(PLANOS + 'plano-datos.png', 'Plano 5. Recorrido de un dato desde el nodo hasta la web', ancho=16.5)

H(3, 'Plano 6. Situación', salto=True)
FOTO('Vista aérea o plano del centro con tres marcas: dónde está el depósito con el nodo, dónde está el mástil con '
     'el gateway y dónde está la Raspberry. Indicar la distancia entre el nodo y el gateway.',
     'Plano 6. Situación del nodo, el gateway y el servidor en el centro', alto=10)
H(3, 'Plano 7. Recorrido del cable del gateway')
FOTO('Croquis o fotos del recorrido del cable de red: mástil, bajada, entrada al edificio, inyector PoE y toma del '
     'switch. Indicar los metros de cable.',
     'Plano 7. Recorrido del cable desde el gateway hasta el switch', alto=8)

# ================================================================ 5. SIMULACIÓN
H(1, '5. Simulación', salto=True)
P('Una buena parte del proyecto se ha probado antes de tener los sensores conectados. Eso nos ha permitido tener el '
  'servidor y la web terminados y comprobados mientras se cerraba el montaje, y que cuando llegue el primer dato '
  'real lo único nuevo sea el sensor. Las pruebas han ido de menos a más: primero solo en el ordenador, después con '
  'el servidor de verdad y al final con la placa y la radio reales mandando datos inventados.')
P('**Todos los datos que aparecen en las capturas de este apartado son simulados.** Los resultados con los sensores '
  'reales se añadirán en el apartado 5.6.')

H(3, '5.1 Prueba del formato del mensaje')
P('Esta prueba no necesita nada más que un ordenador. Compila en el PC el mismo código que usa el nodo para armar '
  'el mensaje, genera tres mensajes (uno normal, uno con temperatura negativa y uno con todos los sensores sin '
  'dato), se los pasa al decodificador que usa ChirpStack y comprueba que cada valor sale igual que entró. Así nos '
  'aseguramos de que el nodo y el servidor «hablan el mismo idioma» antes de encender nada.')
COD('''$ sh pruebas/payload/probar.sh
normal: 02010859034a02f9ffff019c339a0181
  {"version":2,"flags":1,"agua_presente":true,...,"temperatura_c":21.37,"oxigeno_mgl":8.42,"ph":7.61,
   "conductividad_uscm":null,"nivel_mm":412,"bateria_v":13.21,"caudal_lmin":3.85}
...
TODO OK (3 payloads, 10 campos del ingestor comprobados)''')

H(3, '5.2 Compilación del firmware')
P('El firmware se compiló sin errores con PlatformIO antes de tener la placa conectada (26-10-2026). Ocupaba el '
  '8,4 % de la memoria RAM y el 29,9 % de la memoria de programa, así que hay sitio de sobra para ampliarlo. '
  'Después se han ido compilando todos los entornos cada vez que se ha cambiado algo. La última vez fue el '
  '25-11-2026, con la versión real revisada pin a pin: compilan los cuatro entornos sin errores.')

H(3, '5.3 Nodo y gateway simulados contra el servidor')
P('El siguiente paso fue probar el servidor real sin radio. Un programa en Python hace de gateway y de nodo a la '
  'vez: hace el join igual que lo haría la LILYGO (OTAA, LoRaWAN 1.1), manda una medida y comprueba que acaba en la '
  'base de datos y en la web. También mandamos medidas sueltas directamente por MQTT.')
T(['Prueba', 'Cómo se hizo', 'Resultado'], [
    ['Tiempo real de punta a punta', 'Medida simulada mientras se miraba la web pública', 'Llega a la base de datos con la hora en UTC y aparece en la web al momento, sin recargar'],
    ['Cola persistente', 'Parar el ingestor, mandar 2 medidas y volver a arrancarlo', 'Con el ingestor parado había 1 fila; al arrancarlo, 3. No se pierde nada'],
    ['Copia de seguridad', 'Lanzar la copia igual que la lanza el sistema cada noche', 'Crea los dos ficheros de copia (uno por base de datos)'],
    ['Restauración', 'Restaurar la copia en una base de datos temporal', 'Salen las tres tablas con sus filas'],
    ['Privacidad de ChirpStack', 'Abrirlo desde Internet sin Tailscale', 'No conecta, que es lo que tiene que pasar'],
    ['Arranque tras un corte', 'Reiniciar la Raspberry sin tocar nada', 'Los 8 servicios vuelven solos; comprobado dos veces'],
], anchos=[3.8, 5.6, 6.6], titulo='Pruebas del servidor con datos simulados (29-10-2026)', tam=9)
FOTO('Captura del terminal de la Raspberry con `sudo docker compose ps` y los 8 servicios en marcha.',
     'Servicios del servidor en marcha', alto=5.0)

H(3, '5.4 Datos simulados enviados por la radio real')
P('La última simulación es la más completa, porque lo único que no es real son los valores. La LILYGO lleva grabado '
  'un firmware que inventa las medidas, pero las manda de verdad por la radio, las recibe el gateway de verdad y '
  'hacen todo el recorrido hasta la web. Los valores no son números al azar: siguen una curva diaria para que las '
  'gráficas se parezcan a las de un depósito real.')
T(['Magnitud', 'Cómo se simula'], [
    ['Temperatura', 'Entre 18 y 24 °C, con el máximo por la tarde, más un poco de ruido'],
    ['Oxígeno disuelto', 'Baja cuando sube la temperatura (unos 9,5 mg/L a 18 °C y 8,3 a 24 °C), como pasa en el agua de verdad'],
    ['pH', 'Entre 7,3 y 7,7'],
    ['Nivel', 'Oscila despacio alrededor de 420 mm'],
    ['Caudal', 'Hasta el 17-11-2026, unos 4 L/min. Desde que se quitó el caudalímetro va como «sin dato»'],
], anchos=[4.0, 12.0], titulo='Valores que genera el firmware de simulación')
P('Con esta prueba salió el problema más serio del proyecto hasta ahora: el nodo mandaba la petición de unirse a la '
  'red, el gateway la recibía, pero la respuesta no llegaba al nodo. Se resolvió el 12-11-2026 con dos cambios: '
  'hacer el join en SF12 y activar en ChirpStack la opción de contestar por la segunda ventana de recepción cuando '
  'el enlace va justo. Desde entonces el nodo entra en la red y los datos llegan a la web. La señal medida desde el '
  'aula fue de −134 dBm de RSSI y −14 dB de SNR, muy al límite.')
FIG(REPO + 'docs/img/pantalla-oled.png', 'Pantallas del nodo durante un ciclo (logo, fase y temporizador del envío)', ancho=15)

H(3, '5.5 La web con datos simulados')
P('Estas capturas son de la web pública tal como está ahora (13-11-2026), con los datos que manda la LILYGO con el '
  'firmware de simulación. Ese día la web marcaba una señal de −127 dBm de RSSI y −6,5 dB de SNR, con el nodo '
  'trabajando en SF11.')
FIG(D + 'webdoc/web-pc-claro.jpg', 'La web en un ordenador, en modo claro (datos simulados)', ancho=11.5)
FIG(D + 'webdoc/web-pc-oscuro.jpg', 'La web en modo oscuro (datos simulados)', ancho=11.5)
FIG(D + 'webdoc/web-movil-arriba.jpg', 'La web en un móvil: cabecera con el reloj y el estado «En directo»', ancho=6.5)
FIG(D + 'webdoc/web-movil-tarjetas.jpg', 'La web en un móvil: tarjetas en tiempo real (datos simulados)', ancho=6.5)
FIG(D + 'webdoc/web-movil-historico.jpg', 'La web en un móvil: selector de periodo y gráficas del histórico (datos simulados)', ancho=6.5)
FOTO('Un móvil con datos móviles (sin WiFi) enseñando la web fuera del instituto.',
     'La web vista desde fuera del centro con datos móviles', alto=6.0)

H(3, '5.6 Resultados con los sensores reales')
P('[COMPLETAR: cuando el sistema lleve una semana midiendo, describir aquí los resultados: si las lecturas son '
  'estables, si se ha perdido algún mensaje y cómo se comportan los valores a lo largo del día]')
T(['Comprobación', 'Valor esperado', 'Valor obtenido'], [
    ['pH en tampón de 7,00 después de calibrar', '7,00 ± 0,1', '[COMPLETAR: lectura]'],
    ['pH en tampón de 4,00 después de calibrar', '4,00 ± 0,1', '[COMPLETAR: lectura]'],
    ['Temperatura frente a un termómetro de referencia', 'Diferencia pequeña', '[COMPLETAR: lecturas]'],
    ['Oxígeno disuelto del depósito', 'Coherente con la temperatura del agua', '[COMPLETAR: lectura en mg/L]'],
    ['Nivel frente a la medida con una cinta métrica', 'Diferencia pequeña', '[COMPLETAR: lecturas]'],
    ['Nivel en % al echar el agua de 5 en 5 L', 'Sube unos 20 % cada vez', '[COMPLETAR: lecturas]'],
    ['Aviso de falta de agua al bajar el nivel', 'Aparece en la web', '[COMPLETAR: sí o no]'],
    ['Mensajes recibidos en 24 horas', '96', '[COMPLETAR: número]'],
    ['Mensajes recibidos en una semana', '672', '[COMPLETAR: número]'],
    ['La hora de las medidas es correcta', 'Sí', '[COMPLETAR: sí o no]'],
], anchos=[7.0, 4.5, 4.5], titulo='Comprobaciones con los sensores reales (por completar)')
FOTO('Captura de la web con datos reales del depósito, con una gráfica de al menos 24 horas.',
     'La web con datos reales', alto=7.0)

# ================================================================ 6. PLIEGO
H(1, '6. Pliego de Condiciones', salto=True)
H(3, '6.1 Objeto del pliego')
P('Este pliego recoge las condiciones que tienen que cumplir los materiales, el montaje y las pruebas del sistema '
  'para darlo por bueno, y lo que hay que respetar si se repara o se amplía.')
H(3, '6.2 Normativa de aplicación')
B([
    'Cuadro Nacional de Atribución de Frecuencias (CNAF), nota UN-39, y norma ETSI EN 300 220 para equipos de corto '
    'alcance en 868 MHz: potencia máxima de 25 mW y ciclo de trabajo máximo del 1 %.',
    'Real Decreto 188/2016 (transposición de la Directiva 2014/53/UE de equipos radioeléctricos): los equipos de '
    'radio tienen que llevar marcado CE.',
    'Especificación LoRaWAN 1.1 y parámetros regionales EU863-870 de la LoRa Alliance.',
    'Real Decreto 842/2002, Reglamento Electrotécnico para Baja Tensión.',
    'Normativa de prevención de riesgos y de residuos citada en los Anexos II y III.',
    'Normas del centro sobre el uso de la red y el acceso a la azotea.',
])
H(3, '6.3 Condiciones de los materiales')
B([
    'Los equipos de radio (LILYGO y gateway) serán para la banda de 868 MHz y con marcado CE.',
    'Los sensores serán los indicados en la memoria o equivalentes con la misma salida (RS485 Modbus, 4-20 mA, '
    'tensión de 0 a 3 V o pulsos), para no tener que cambiar el firmware.',
    'El módulo RS485 será de 3,3 V. No vale uno de 5 V, porque su salida dañaría el pin de la LILYGO.',
    'Las resistencias, de 1/4 W y, a ser posible, del 1 % de tolerancia.',
    'La protoboard tendrá las líneas de alimentación continuas de punta a punta (se comprueba con el polímetro) y '
    'las puntas de los cables de los sensores irán estañadas.',
    'La fuente de los sensores dará entre 12 y 13 V en continua y al menos 1 A.',
    'El cable del gateway será Cat6 para exterior, resistente al sol.',
    'La sonda de pH será de inmersión continua.',
    'El depósito será opaco y con tapa, con todos los agujeros por encima del agua.',
])
H(3, '6.4 Condiciones de ejecución')
B([
    'Ninguna entrada de la LILYGO recibirá más de 3,3 V. Se comprobará con el polímetro antes de conectarla.',
    'La LILYGO se alimenta solo por USB. El pin de 5 V queda sin conectar.',
    'La LILYGO no se encenderá nunca sin la antena puesta.',
    'El negativo de la fuente de 12 V y el GND de la LILYGO irán unidos (puente entre las dos líneas − de la protoboard).',
    'Las líneas + de la protoboard irán marcadas: la de arriba «12 V» y la de abajo «3V3».',
    'Se encenderá primero la LILYGO y después la fuente de 12 V, y se apagará al revés.',
    'La fuente de 12 V y el cargador irán en su propia caja estanca, separada de la del nodo.',
    'No entrará ningún cable de 230 V en la caja del nodo.',
    'No se pondrá tarjeta microSD en la LILYGO y el GPIO12 quedará libre.',
    'Los cables entrarán en la caja por abajo y la antena quedará vertical.',
    'Las sondas quedarán sujetas sin que el cable tire de ellas, lejos de la salida de la bomba, y la punta de la '
    'sonda de pH siempre por debajo del nivel mínimo.',
    'El gateway se montará vertical, con el conector hacia abajo y con bucle de goteo en el cable. El tramo de cable '
    'desde el switch no pasará de 100 m.',
    'El gateway y la Raspberry llevarán IP fija dentro de la VLAN 500 y fuera del rango del DHCP.',
    'No se abrirá ningún puerto en el router del centro.',
    'Las claves y contraseñas no se subirán al repositorio.',
    'Las horas se guardarán siempre en UTC.',
    'Todos los servicios del servidor se definirán en Docker Compose con reinicio automático.',
    'Antes de cambiar la configuración de red de la Raspberry por SSH se tendrá otra forma de entrar (teclado y '
    'monitor).',
])
H(3, '6.5 Pruebas de recepción')
P('El sistema se da por bueno cuando cumple todo esto:')
T(['Prueba', 'Criterio de aceptación'], [
    ['Lecturas en el banco', 'El monitor serie muestra valores coherentes con las soluciones patrón (pH con un error máximo de ±0,1)'],
    ['Radio', 'El nodo hace el join y los mensajes salen decodificados en ChirpStack'],
    ['Tiempo real', 'Cada medida aparece en la web al momento, sin recargar la página'],
    ['Base de datos', 'Hay 24 horas seguidas de datos con la hora correcta'],
    ['Cola', 'Con el ingestor parado no se pierde ningún mensaje'],
    ['Copias', 'La copia diaria se crea y se puede restaurar'],
    ['Acceso remoto', 'La web se ve desde un móvil con datos móviles, fuera del instituto'],
    ['Seguridad', 'ChirpStack no se puede abrir desde Internet sin Tailscale'],
    ['Arranque', 'Tras un corte de corriente todo vuelve a funcionar sin intervención'],
    ['Avisos', 'El aviso de falta de agua aparece cuando toca'],
    ['Estabilidad', 'Una semana de funcionamiento sin pérdidas significativas de mensajes'],
], anchos=[3.5, 12.5], titulo='Pruebas de recepción')
H(3, '6.6 Condiciones de uso y mantenimiento')
B([
    'La sonda de pH no puede quedarse en seco. Si se desmonta, se guarda con su capuchón y su líquido.',
    'El sensor de oxígeno no debe pasar de 40 °C: el bidón tiene que estar a la sombra.',
    'El mantenimiento se hará según el plan del Anexo IV.',
    'Si se cambia un sensor por otro distinto, hay que revisar el firmware y volver a hacer las pruebas de recepción '
    'que le afecten.',
    'El firmware de simulación no se dejará grabado en el nodo de la instalación.',
    'Cualquier cambio en la red (direcciones, VLAN o DNS) se hará de acuerdo con el coordinador TIC.',
])

# ================================================================ 7. PRESUPUESTO
from presu import CAPS, eur, totales
H(1, '7. Presupuesto', salto=True)
P('**Todo el material del proyecto lo ha proporcionado el instituto.** Los equipos principales (la LILYGO, el '
  'gateway, la Raspberry y los sensores) ya estaban en el centro y el resto ha salido del material del '
  'departamento, así que el proyecto no ha supuesto ninguna compra para nosotros. Aun así hemos valorado cada '
  'partida a precio de mercado, para saber cuánto costaría montar el sistema desde cero en otro sitio.')
P('Los precios son por unidad y con IVA, de tiendas que sirven en España, consultados en noviembre de 2026. En '
  'las tiendas que publican el precio sin IVA se ha sumado el 21 % y se indica entre paréntesis. No se incluyen '
  'los gastos de envío.')
for titulo, filas in CAPS:
    sub = sum(c * p for c, _, _, p in filas)
    T(['Ud.', 'Concepto', 'Tienda de referencia', 'Precio ud.', 'Importe', 'Origen'],
      [[str(c), d, t, eur(p), eur(c * p), 'Instituto'] for c, d, t, p in filas]
      + [['', '**Subtotal**', '', '', '**' + eur(sub) + '**', '']],
      anchos=[1.0, 5.3, 3.8, 1.9, 1.9, 2.1], titulo=titulo, tam=9)
P('Notas sobre algunas partidas:')
B([
    'La **bomba de recirculación** no se valora: va aparte, con su propia alimentación, y no forma parte del sistema '
    'de medida.',
    'La **fuente de 12 V** del montaje es una fuente de PC del centro reaprovechada. Se pone el precio de una nueva '
    'equivalente.',
    'El **cargador USB con batería de respaldo** se valora con un mini SAI con salida USB de 5 V. '
    '[COMPLETAR: modelo del cargador con batería que se ha usado de verdad]',
    'El **módulo RS485** es el único componente que no estaba en el centro a la fecha de redacción.',
    'El **cable de red** de la bajada se ha valorado con 20 m. No es de intemperie, así que tiene que ir bajo tubo. '
    '[COMPLETAR: metros reales de cable]',
    'Las piezas de la parte hidráulica y la caja son las de la lista de material del proyecto. '
    '[COMPLETAR: confirmar que coinciden con las montadas]',
    'La **instalación solar y el inversor** del centro, el mástil y la red del instituto ya existían y no se valoran.',
])
T(['Concepto', 'Coste'], [
    ['ChirpStack, Mosquitto, TimescaleDB, Redis, Caddy, Docker, Raspberry Pi OS, PlatformIO y RadioLib', '0,00 € (software libre)'],
    ['Tailscale, plan personal', '0,00 €'],
    ['Repositorio en GitHub', '0,00 €'],
], anchos=[12.0, 4.0], titulo='Capítulo 7. Software y servicios', tam=9)
T(['Concepto', 'Horas', 'Precio por hora', 'Importe'], [
    ['Diseño y documentación', '[COMPLETAR: horas]', '[COMPLETAR: €/h]', '[COMPLETAR: importe]'],
    ['Programación del nodo, el servidor y la web', '[COMPLETAR: horas]', '[COMPLETAR: €/h]', '[COMPLETAR: importe]'],
    ['Montaje, instalación y pruebas', '[COMPLETAR: horas]', '[COMPLETAR: €/h]', '[COMPLETAR: importe]'],
], anchos=[7.0, 3.0, 3.0, 3.0], titulo='Capítulo 8. Mano de obra (trabajo de los alumnos, no facturado)', tam=9)
H(3, 'Resumen del presupuesto')
tot = totales()
total = sum(s for _, s in tot)
T(['Capítulo', 'Importe (con IVA)', 'Procedencia'],
  [[t.replace('Capítulo ', ''), eur(s), 'Material del instituto'] for t, s in tot]
  + [['7. Software y servicios', '0,00 €', 'Software libre'],
     ['**TOTAL DEL MATERIAL A PRECIO DE MERCADO**', '**' + eur(total) + '**', ''],
     ['**Coste real de material para el proyecto**', '**0,00 €**', 'Todo aportado por el instituto'],
     ['8. Mano de obra', '[COMPLETAR: importe de la mano de obra, si se quiere valorar]', 'Trabajo de los alumnos']],
  anchos=[7.0, 4.5, 4.5], titulo='Resumen por capítulos')
P('Montar el sistema desde cero costaría, por tanto, unos ' + eur(total).replace(' €', '') + ' euros en material. Las tres '
  'partidas que más pesan son el gateway, el sensor de oxígeno y la Raspberry, que entre las tres suman casi la '
  'mitad. Como comparación, la primera lista de compra del diseño inicial (con panel solar, batería, regulador, '
  'cajas estancas y conectores) salía por 1.189,52 € sin contar ninguno de los equipos que ya tenía el centro. Con '
  'la simplificación ha desaparecido todo el capítulo de energía (unos 500 €) y buena parte del de electrónica.')

# ================================================================ 8. CONCLUSIONES
H(1, '8. Conclusiones', salto=True)
P('El proyecto nos ha servido para ver cómo encajan en un sistema real cosas que en clase se estudian por separado. '
  'Un dato sale de una sonda, pasa por un microcontrolador, viaja por radio, entra en una red de datos, llega a un '
  'servidor, se guarda en una base de datos y acaba en la pantalla de un móvil. Cada salto es una asignatura '
  'distinta, y cuando falla uno hay que saber en cuál mirar.')
P('A la fecha de escribir esto, la parte de servidor, red y web está terminada y funcionando: la Raspberry lleva en '
  'marcha desde finales de octubre, arranca sola tras un corte, hace sus copias de seguridad y la web se ve desde '
  'fuera del instituto. El gateway está configurado y el nodo se une a la red y manda datos. Lo que queda es el '
  'montaje de los sensores, subir el gateway al mástil y la semana de pruebas con datos reales. '
  '[COMPLETAR: actualizar este párrafo con el resultado final cuando esté todo montado]')
P('Lo que más nos ha enseñado han sido los problemas. El que más tiempo nos llevó fue el del join: el gateway '
  'recibía al nodo pero el nodo no recibía la respuesta, y hasta que no entendimos cómo funcionan las ventanas de '
  'recepción de LoRaWAN y lo justa que iba la señal desde el aula no dimos con la solución. También nos encontramos '
  'con que la red del centro tiene sus normas: no se pueden abrir puertos, el DNS que suponíamos no contestaba y '
  'algunos servidores de Internet no eran accesibles. En vez de pelearnos con eso buscamos soluciones que no '
  'obligaran al centro a cambiar nada, como Tailscale Funnel. Y con el gateway aprendimos que un equipo de fábrica '
  'no siempre viene configurado para lo que uno necesita.')
P('La otra lección ha sido simplificar. El primer diseño tenía panel solar propio, batería, convertidores, '
  'aisladores y conmutadores, y sobre el papel era mejor. Pero había que montarlo con el material que teníamos de '
  'verdad, y al final el nodo lee todo directamente, con dos resistencias y una protoboard. Se pierde algo de precisión en '
  'las medidas analógicas y el pH comparte masa con el resto de sensores, pero el montaje es mucho más fácil de '
  'hacer, de entender y de reparar. Si el pH diera lecturas inestables, lo primero que habría que probar es '
  'desenchufar la bomba para ver si el problema viene de ahí.')
P('También aprendimos a no fiarnos solo de los papeles: los pines que el esquema llamaba GPIO36 y GPIO39 en la '
  'placa aparecen como S_VP y S_VN, y al revisar el firmware contra la serigrafía real encontramos dos pines '
  'antiguos que chocaban con el montaje nuevo. Comprobar cada conexión con la placa delante y con el polímetro '
  'antes de encender nos ha ahorrado más de un susto.')
H(3, 'Limitaciones')
B([
    'Sin el módulo RS485 no hay ni oxígeno ni temperatura, que es justo la medida que queríamos añadir.',
    'Las entradas analógicas del ESP32 son menos precisas que un convertidor dedicado. Se compensa con la '
    'calibración en dos puntos, pero no es un equipo de laboratorio.',
    'El sensor de nivel está pensado para 5 m y nuestro bidón mide unos 40 cm, así que tiene poca resolución (unos ±1,5 L).',
    'No se mide el caudal ni la presión, que sí salen en el cartel de referencia, y el nodo no sabe si la bomba funciona.',
    'La batería de respaldo mantiene la LILYGO, pero no los sensores de 12 V.',
    'Los colores de la web están puestos con valores orientativos, a falta de datos reales.',
])
H(3, 'Posibles ampliaciones')
B([
    'Alarmas automáticas con Node-RED: aviso cuando el pH, el oxígeno o el nivel se salgan de rango, o cuando el nodo '
    'lleve más de una hora sin transmitir.',
    'Un segundo nodo con relé (el centro tiene un DFRobot DFR1120-868) que encienda una baliza o abra el llenado del '
    'depósito cuando se lo mande el servidor por radio.',
    'Cambiar el intervalo de envío desde el servidor, sin tener que ir a reprogramar el nodo. El firmware ya tiene '
    'previsto ese mensaje.',
    'Volver a poner el convertidor ADS1115 y el aislador del pH si se consiguen, para mejorar la precisión.',
    'Alimentar también los sensores con respaldo, o volver a la idea del panel y la batería propios para que el nodo '
    'sea totalmente independiente.',
    'Añadir más nodos en otros puntos del centro: el gateway y el servidor ya valen para todos.',
])
P('Al final, que un valor medido en un depósito en el patio aparezca unos segundos después en el móvil, con su '
  'gráfica y su hora, y saber qué pasa en cada tramo del camino, da bastante satisfacción. '
  '[COMPLETAR: valoración personal final de cada uno, si se quiere añadir]')

# ================================================================ LISTA FINAL
salto()
P('LISTA DE COSAS POR COMPLETAR (borrar estas páginas antes de entregar)', alin='i', tam=16, color=AZUL)
P('Esta página no forma parte de la memoria. Es un resumen de todo lo que está marcado en el documento para '
  'rellenar, para ir tachándolo.')
P('**Fotos y capturas**', alin='i')
T(['Foto', 'Figura', 'Apartado', 'Qué hay que poner'],
  [[str(n), str(f), s, d] for n, f, s, d in fotos], anchos=[1.2, 1.4, 4.4, 9.0], tam=9)
P('**Datos**', alin='i')
vistos = []
for s, d in completar:
    if (s, d) not in vistos and d not in ('precio', 'tienda', 'horas', '€/h', 'importe'):
        vistos.append((s, d))
T(['Apartado', 'Dato que falta'], [[s, d] for s, d in vistos], anchos=[5.0, 11.0], tam=9)
P('Además, en el presupuesto faltan las horas y el precio por hora de la mano de obra.')
