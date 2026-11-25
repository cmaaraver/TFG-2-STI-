# Presupuesto: capítulos con precios comprobados (13-11-2026). Se inserta en c4.py
CAPS = [
 ('Capítulo 1. Nodo y sensores', [
  (1, 'LILYGO T3 V1.6.1 868 MHz con antena', 'TinyTronics (envía a España)', 22.00),
  (1, 'Sensor de oxígeno disuelto y temperatura DFRobot SEN0681', 'Mouser España (133,04 € + IVA)', 160.98),
  (1, 'Kit de pH DFRobot SEN0169-V2 (sonda y placa)', 'Farnell España (55,97 € + IVA)', 67.72),
  (1, 'Transmisor de nivel DFRobot KIT0139 con conversor', 'RobotShop Europa', 48.29),
  (1, 'Sensor de presencia de agua DFRobot SEN0204', 'RobotShop Europa', 13.09),
  (1, 'Módulo RS485 a TTL de 3,3 V (MAX3485)', 'Desertcart España', 26.46),
  (1, 'Kit de 600 resistencias del 1 % (incluye 10 kΩ y 27 kΩ)', 'Leantec', 4.27),
  (1, 'Protoboard de 830 puntos (pegada en la caja estanca)', 'Estimación (material de taller)', 5.00),
  (1, 'Juego de cables dupont macho-hembra y macho-macho', 'Estimación (material de taller)', 5.00),
  (1, 'Cable USB de datos de 1 m', 'Electrónica Embajadores', 5.83),
  (1, 'Caja estanca IP66 de 255 × 250 × 120 mm', 'Electrónica Embajadores', 56.55),
  (3, 'Prensaestopas PG9 IP68', 'Electrónica Embajadores', 0.84),
  (1, 'Cables y estaño', 'Estimación (material de taller)', 5.00),
 ]),
 ('Capítulo 2. Alimentación del nodo', [
  (1, 'Fuente de alimentación ATX de 500 W (salida de 12 V)', 'PcComponentes', 16.98),
  (1, 'Mini SAI de continua con salida USB de 5 V, 10.000 mAh (Salicru SPS NET2)', 'PcComponentes', 44.95),
  (1, 'Regleta de 4 tomas con interruptor', 'PcComponentes', 9.20),
 ]),
 ('Capítulo 3. Gateway y red', [
  (1, 'Gateway MikroTik wAP LR8 kit (con fuente e inyector PoE)', 'NASstore (139,00 € + IVA, envía a España)', 168.19),
  (2, 'Latiguillo de red Cat6 de 1 m', 'Electrónica Embajadores', 1.38),
  (1, 'Cable de red FTP Cat6 de 20 m (bajante, bajo tubo)', 'PcComponentes', 15.98),
  (1, 'Bridas negras resistentes al sol (100 uds)', 'Todoeléctrico', 6.21),
 ]),
 ('Capítulo 4. Servidor', [
  (1, 'Raspberry Pi 5 de 4 GB', 'RS España (121,50 € + IVA)', 147.02),
  (1, 'Tarjeta microSD de 64 GB SanDisk Ultra', 'PcComponentes', 13.72),
  (1, 'Fuente oficial Raspberry Pi de 27 W', 'Kubii', 12.90),
  (1, 'Ventilador oficial (Active Cooler)', 'Kubii', 6.00),
 ]),
 ('Capítulo 5. Parte hidráulica', [
  (1, 'Bidón de plástico de 25 L con tapón (reaprovechado del centro, sin coste)', 'Reaprovechado', 0.00),
  (3, 'Manguera reforzada de 12 × 18 mm (metro)', 'Suministros Urquiza', 1.39),
  (8, 'Abrazadera de acero inoxidable de 12-22 mm', 'Agrogomas', 1.45),
 ]),
 ('Capítulo 6. Calibración', [
  (1, 'Solución tampón de pH 4,01 (230 ml)', 'Hanna Instruments', 12.10),
  (1, 'Solución tampón de pH 7,01 (230 ml)', 'Hanna Instruments', 12.10),
  (3, 'Vaso de precipitado de 100 ml', 'Daselab', 1.45),
  (1, 'Agua destilada (garrafa de 5 L)', 'Estimación (compra local)', 2.00),
 ]),
]
def eur(x):
    s = f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s + ' €'
def totales():
    return [(t, round(sum(c * p for c, _, _, p in f), 2)) for t, f in CAPS]
if __name__ == '__main__':
    for t, s in totales(): print(t, eur(s))
    print(eur(sum(s for _, s in totales())))
