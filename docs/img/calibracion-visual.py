# Genera los dibujos de la guía de calibración (docs/14-checklist-calibracion.md).
# Uso: python3 calibracion-visual.py carpeta_salida
# Salen 6 SVG: calib-flujo, calib-puente-io15, calib-pantallas, calib-ph, calib-nivel y calib-oxigeno.
# Pines de la LILYGO: serigrafía de nuestra T3 V1.6.1 (docs/12, apartado 1.5).
import os, sys

SAL = sys.argv[1] if len(sys.argv) > 1 else '.'
ESTILO = '''<style>
.t{fill:#17201d}.m{fill:#4f5b57;font-size:14px}.h{font-weight:700;font-size:22px;fill:#17201d}
.b{font-weight:700;fill:#17201d}.s{font-size:13px;fill:#17201d}.w{fill:#fff;font-weight:700}
.mono{font-family:DejaVu Sans Mono,monospace;font-size:14px;fill:#d8f5d0}
.monob{font-family:DejaVu Sans Mono,monospace;font-size:14px;fill:#ffffff;font-weight:700}
.pin{font-family:DejaVu Sans Mono,monospace;font-size:13px;fill:#ffe07a;font-weight:700}
.oled{font-family:DejaVu Sans Mono,monospace;font-size:13px;fill:#9fe0ff}
.warn{fill:#b3261e;font-size:14px;font-weight:700}.ok{fill:#1f7a3c;font-size:14px;font-weight:700}
</style>'''

class Lienzo:
    def __init__(s, w, h, titulo, sub=''):
        s.w, s.h, s.o = w, h, []
        s.a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            'font-family="DejaVu Sans, Arial, sans-serif" font-size="15">')
        s.a(ESTILO)
        s.a('<defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#4f5b57"/></marker></defs>')
        s.a(f'<rect width="{w}" height="{h}" fill="#f6f8f7"/>')
        s.t(28, 38, titulo, 'h', 'start')
        if sub: s.t(28, 62, sub, 'm', 'start')
    def a(s, x): s.o.append(x)
    def t(s, x, y, txt, cls='t', anc='middle', st=''):
        s.a(f'<text x="{x:.0f}" y="{y:.0f}" class="{cls}" text-anchor="{anc}"' + (f' style="{st}"' if st else '') + f'>{txt}</text>')
    def r(s, x, y, w, h, fill='#fff', stroke='#9aa8a2', rx=10, sw=1.5, extra=''):
        s.a(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
    def flecha(s, x1, y1, x2, y2, col='#4f5b57', w=2.5, dash=''):
        s.a(f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}" stroke="{col}" stroke-width="{w}" fill="none" marker-end="url(#fl)"'
            + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
    def guardar(s, nombre):
        s.a('</svg>')
        with open(os.path.join(SAL, nombre + '.svg'), 'w') as f: f.write('\n'.join(s.o))

def etiqueta_quien(L, x, y, quien):
    """Pastilla 'PERSONA' (naranja) o 'CLAUDE' (morado)."""
    col = '#e07a1f' if quien == 'PERSONA' else '#6d4bd1'
    w = 92 if quien == 'PERSONA' else 80
    L.r(x, y - 16, w, 22, col, col, 11)
    L.t(x + w / 2, y, quien, 'w', 'middle', 'font-size:12px')

def terminal(L, x, y, w, lineas, titulo='Monitor serie · COM7 · 115200'):
    h = 34 + 21 * len(lineas)
    L.r(x, y, w, h, '#13201b', '#13201b', 8)
    L.r(x, y, w, 24, '#2c3a34', '#2c3a34', 8)
    L.t(x + 12, y + 17, titulo, 's', 'start', 'fill:#c9d6d0')
    for i, (txt, cls) in enumerate(lineas):
        L.t(x + 12, y + 44 + 21 * i, txt.replace('<', '&lt;'), cls, 'start')
    return h

def oled(L, x, y, l1, l2, w=250):
    L.r(x - 14, y - 14, w + 28, 132, '#20262a', '#20262a', 10)
    L.r(x, y, w, 104, '#05121a', '#3b5563', 4, 2)
    L.t(x + w / 2, y + 40, l1, 'oled', 'middle', 'font-weight:700;font-size:16px')
    L.t(x + w / 2, y + 70, l2, 'oled', 'middle')
    L.t(x + w / 2, y + 140, 'Pantalla OLED de la LILYGO', 'm')

# ---------------------------------------------------------------- 1. Flujo general
def flujo():
    L = Lienzo(1500, 430, 'Calibración en 7 pasos · unos 45 min (65 min con el oxígeno)',
               'Naranja = lo hace la persona (Carlos o Rubén). Morado = lo hace Claude con calibrar.py. Cada paso termina con una comprobación.')
    pasos = [('1', 'Preparación', '10 min', 'Grabar firmware real.\nPuente IO15–GND.', '#2f7d6d'),
             ('2', 'Comprobar', '5 min', 'mv y leer:\n¿cableado bien?', '#2f7d6d'),
             ('3', 'pH', '20 min', 'Tampón 7 → ph7\nTampón 4 → ph4', '#8e3fd1'),
             ('4', 'Cero nivel', '5 min', 'Bidón vacío\n→ nivel0', '#1e5fd0'),
             ('5', '5 en 5 L', '15 min', 'Nivel cada 5 L.\nSEN0204 cambia a 1', '#1e5fd0'),
             ('6', 'Oxígeno', '20 min', 'Solo con RS485:\nsal0 y o2_100', '#0e8fb5'),
             ('7', 'Cerrar', '5 min', 'Quitar puente.\nComprobar la web', '#2f7d6d')]
    x0, wc, gap = 28, 196, 12
    for i, (n, nom, tmp, desc, col) in enumerate(pasos):
        x = x0 + i * (wc + gap)
        opc = (n == '6')
        L.r(x, 100, wc, 250, '#fff', col, 12, 2.5, 'stroke-dasharray="8 5"' if opc else '')
        L.r(x, 100, wc, 54, col, col, 12)
        L.a(f'<rect x="{x}" y="138" width="{wc}" height="16" fill="{col}"/>')
        L.a(f'<circle cx="{x+30}" cy="127" r="17" fill="#fff"/>')
        L.t(x + 30, 133, n, 'b', 'middle', f'fill:{col};font-size:18px')
        L.t(x + 56, 133, nom, 'w', 'start', 'font-size:17px')
        L.t(x + wc / 2, 190, tmp, 'b', 'middle', 'font-size:20px')
        for k, lin in enumerate(desc.split('\n')):
            L.t(x + wc / 2, 228 + 22 * k, lin, 's', 'middle', 'font-size:14px')
        etiqueta_quien(L, x + 10, 315, 'PERSONA'); etiqueta_quien(L, x + 108, 315, 'CLAUDE')
        if opc: L.t(x + wc / 2, 372, 'opcional hasta tener el RS485', 'warn', 'middle', 'font-size:12px')
        if i < len(pasos) - 1: L.flecha(x + wc + 2, 225, x + wc + gap - 2, 225)
    L.t(28, 410, 'El orden importa: el pH va antes que el nivel, porque el comando reset (por si el pH sale mal) también borra el cero del nivel.', 'm', 'start')
    L.guardar('calib-flujo')

# ---------------------------------------------------------------- 2. Puente IO15
IZQ = ['S_VP', 'S_VN', 'RST', 'IO34', 'IO35', 'IO14', 'IO12', 'IO13', 'IO15', 'IO2', 'IO0', 'IO4', 'IO25']
DER = ['IO21', 'TxD', 'RXD', 'IO22', 'IO23', 'IO19', 'LoRa2', 'LoRa1', 'IO26', 'GND', '3.3V', 'GND', '5V']
USO = {'S_VP': ('pH', '#1e5fd0'), 'S_VN': ('nivel', '#1f9d48'), 'IO14': ('RS485 RO', '#8a8f94'),
       'IO13': ('RS485 DI', '#8e3fd1'), 'IO4': ('agua', '#c9a000'), 'IO25': ('RS485 DE', '#8a8f94'),
       '3.3V': ('3V3', '#f07c00')}
PROHIBIDO = {'IO12', 'IO2', 'IO0', 'RST', '5V'}

def puente():
    L = Lienzo(1500, 830, 'Puente de calibración: un dupont hembra-hembra entre IO15 y GND',
               'Con el puente puesto al arrancar, la LILYGO entra en el menú de calibración. Sin el puente, funciona normal y envía cada 15 min.')
    bx, by, bw, bh = 520, 110, 420, 600
    L.r(bx, by, bw, bh, '#1b3b8f', '#0f2560', 14, 3)            # placa azul
    # antena (conector) arriba y USB abajo
    L.r(bx + bw / 2 - 40, by - 30, 80, 40, '#c7a14a', '#7a6125', 6, 2)
    L.t(bx + bw / 2 + 52, by - 4, 'antena (siempre puesta)', 's', 'start', 'font-weight:700')
    L.r(bx + bw / 2 - 45, by + bh - 10, 90, 40, '#b8bcbf', '#6b7074', 6, 2)
    L.t(bx + bw / 2, by + bh + 50, 'USB al PC (COM7)', 's', 'middle', 'font-weight:700')
    # OLED, chip y botones
    L.r(bx + 110, by + 70, 200, 120, '#05121a', '#3b5563', 4, 3)
    L.t(bx + 210, by + 125, 'MODO', 'oled', 'middle', 'font-weight:700')
    L.t(bx + 210, by + 147, 'CALIBRACION', 'oled', 'middle', 'font-weight:700')
    L.r(bx + 130, by + 250, 160, 130, '#9aa1a6', '#5f666b', 6, 2)
    L.t(bx + 210, by + 320, 'ESP32', 'b', 'middle', 'fill:#333')
    L.r(bx + 130, by + 410, 160, 100, '#c9ccce', '#6b7074', 6, 2)
    L.t(bx + 210, by + 465, 'SX1276', 'b', 'middle', 'fill:#333')
    for k, (nom, xx) in enumerate((('RST', bx + 110), ('BOOT', bx + 270))):
        L.r(xx, by + 530, 40, 30, '#e0e0e0', '#555', 4, 2)
        L.a(f'<circle cx="{xx+20}" cy="{by+545}" r="8" fill="#333"/>')
        L.t(xx + 20, by + 580, nom, 'pin', 'middle', 'fill:#fff')
    L.t(bx + 210, by + 30, 'T3_V1.6.1 · cara de los componentes', 'pin', 'middle', 'fill:#cfd8ff')
    # tiras de pines
    paso, y0 = 40, by + 60
    def pin_xy(lado, i): return (bx + 28 if lado == 'i' else bx + bw - 28, y0 + i * paso)
    for lado, lista in (('i', IZQ), ('d', DER)):
        for i, nom in enumerate(lista):
            x, y = pin_xy(lado, i)
            dest = nom in ('IO15', 'GND') and (lado == 'i' and nom == 'IO15' or lado == 'd' and i == 9)
            L.r(x - 11, y - 11, 22, 22, '#e8c35a' if not dest else '#ff5a4f', '#7a6125' if not dest else '#8b0000', 3, 2)
            L.a(f'<circle cx="{x}" cy="{y}" r="5" fill="#333"/>')
            tx = x + 20 if lado == 'i' else x - 20
            L.t(tx, y + 5, nom, 'pin', 'start' if lado == 'i' else 'end', 'fill:#ff8a80' if dest else '')
            # etiqueta exterior de uso
            ex = bx - 16 if lado == 'i' else bx + bw + 16
            anc = 'end' if lado == 'i' else 'start'
            if dest:
                L.t(ex, y + 5, '◀ PUENTE' if lado == 'd' else 'PUENTE ▶', 'warn', anc, 'font-size:16px')
            elif nom in USO:
                L.t(ex, y + 5, USO[nom][0], 's', anc, f'fill:{USO[nom][1]};font-weight:700')
            elif nom in PROHIBIDO:
                L.t(ex, y + 5, 'no tocar', 's', anc, 'fill:#999')
    # cable del puente (rojo) por fuera, de IO15 (izq, i=8) a GND (der, i=9)
    x1, y1 = pin_xy('i', 8); x2, y2 = pin_xy('d', 9)
    yb = by + bh + 78                                           # el cable pasa por debajo de la placa
    d = (f'M{x1},{y1} L{bx+8},{y1+12} L{bx+8},{yb-20} Q{bx+8},{yb} {bx+28},{yb} L{bx+bw-28},{yb} '
         f'Q{bx+bw-8},{yb} {bx+bw-8},{yb-20} L{bx+bw-8},{y2+12} L{x2},{y2}')
    L.a(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>')
    L.a(f'<path d="{d}" fill="none" stroke="#d32f2f" stroke-width="7" stroke-linecap="round"/>')
    for (x, y) in ((x1, y1), (x2, y2)):
        L.r(x - 9, y - 14, 18, 28, '#222', '#000', 3, 1)
    # cuadros laterales de explicación
    L.r(28, 110, 380, 300, '#fff', '#9aa8a2')
    L.t(46, 140, 'Cómo ponerlo', 'b', 'start')
    for k, lin in enumerate(['1. Fuente de 12 V apagada.', '2. Hembra del dupont en IO15 (tira', '    izquierda, 9.º pin desde arriba).',
                             '3. La otra hembra en GND (tira', '    derecha, 10.º pin desde arriba).', '4. Encender la fuente y pulsar RST.',
                             '5. La OLED pone MODO CALIBRACION.']):
        L.t(46, 172 + 30 * k, lin, 's', 'start', 'font-size:15px')
    L.r(28, 430, 380, 170, '#fff3f2', '#e0a19b')
    L.t(46, 460, 'Errores típicos', 'warn', 'start')
    for k, lin in enumerate(['✗ En IO12 o IO2: la placa no arranca.', '✗ En IO13 (justo encima): es el RS485.',
                             '✗ Olvidarlo puesto al acabar: el nodo', '    se queda en el menú y no envía.']):
        L.t(46, 492 + 28 * k, lin, 's', 'start', 'font-size:15px')
    L.r(1092, 110, 380, 250, '#fff', '#9aa8a2')
    L.t(1110, 140, 'Colores de los otros pines', 'b', 'start')
    for k, (nom, (uso, col)) in enumerate(USO.items()):
        L.a(f'<rect x="1110" y="{158+28*k}" width="18" height="18" rx="3" fill="{col}"/>')
        L.t(1138, 172 + 28 * k, f'{nom}: {uso}', 's', 'start', 'font-size:15px')
    L.r(1092, 380, 380, 120, '#f1fbf4', '#9cc9a8')
    L.t(1110, 410, 'Cómo saber que ha entrado', 'ok', 'start')
    L.t(1110, 440, 'OLED: «MODO CALIBRACION».', 's', 'start', 'font-size:15px')
    L.t(1110, 468, 'Monitor: «=== MODO CALIBRACION ===».', 's', 'start', 'font-size:15px')
    L.guardar('calib-puente-io15')

# ---------------------------------------------------------------- 3. Pantallas
def pantallas():
    L = Lienzo(1500, 600, 'Qué sale en la pantalla y en el monitor serie',
               'Izquierda: modo calibración (con el puente). Derecha: funcionamiento normal (sin puente). Los números son de ejemplo.')
    oled(L, 60, 110, 'MODO CALIBRACION', 'Monitor serie 115200')
    terminal(L, 380, 96, 560, [
        ('=== MODO CALIBRACION ===', 'monob'),
        ('Comandos: leer | mv | ph7 | ph4 | nivel0 | sal |', 'mono'),
        ('  sal0 | o2_100 | o2_cero | ver | reset | salir', 'mono'),
        ('Esperando calentamiento de sensores (60 s)...', 'mono'),
        ('> mv', 'monob'),
        ('pH: 1512 mV   nivel: 483 mV (4.03 mA, 9 mm ...)', 'mono'),
        ('   agua: pin=0', 'mono'),
        ('> leer', 'monob'),
        ('T=nan C  O2=nan mg/L  pH=6.98  nivel=0 mm', 'mono'),
        ('   bat=0 mV  agua=0  rs485_err=1', 'mono'),
        ('> ph7', 'monob'),
        ('pH7 guardado: 1512.0 mV', 'mono'),
    ], 'Monitor serie · COM7 · 115200 · modo calibración')
    L.r(60, 300, 280, 250, '#fff', '#9aa8a2')
    L.t(76, 328, 'Cómo leer «leer»', 'b', 'start')
    for k, lin in enumerate(['T y O2 = nan: sin RS485', '   (normal por ahora)', 'rs485_err=1: lo mismo', 'bat=0 mV: no se mide',
                             '   en este montaje (normal)', 'agua=1: hay agua delante', '   del SEN0204']):
        L.t(76, 360 + 26 * k, lin, 's', 'start', 'font-size:14px')
    oled(L, 1000, 110, 'Enviando...', 'Siguiente: 14:59', 230)
    terminal(L, 960, 330, 510, [
        ('--- Nodo calidad agua, ciclo 1 ---', 'monob'),
        ('Sesion restaurada', 'mono'),
        ('(o "Join OK (sesion nueva)")', 'mono'),
        ('... a los 60 s mide y envía ...', 'mono'),
        ('NUNCA debe salir [SIMULADO]', 'monob'),
    ], 'Monitor serie · funcionamiento normal')
    L.t(1215, 330 + 34 + 21 * 5 + 30, 'Si sale [SIMULADO], está grabado el firmware de prueba:', 'warn')
    L.t(1215, 330 + 34 + 21 * 5 + 52, 'pio run -e lilygo_t3_simple -t upload --upload-port COM7', 'm')
    L.guardar('calib-pantallas')

# ---------------------------------------------------------------- 4. pH
def vaso(L, x, y, col, txt, sonda=True):
    L.a(f'<path d="M{x},{y} L{x+12},{y+170} L{x+128},{y+170} L{x+140},{y} Z" fill="#eef6fb" stroke="#7d8f99" stroke-width="2.5"/>')
    L.a(f'<path d="M{x+6},{y+60} L{x+12},{y+170} L{x+128},{y+170} L{x+134},{y+60} Z" fill="{col}" opacity=".75"/>')
    L.t(x + 70, y + 198, txt, 'b', 'middle', 'font-size:18px')
    if sonda:
        L.r(x + 58, y - 140, 24, 270, '#2b2b2b', '#111', 6)
        L.a(f'<ellipse cx="{x+70}" cy="{y+138}" rx="14" ry="18" fill="#cfe7f3" stroke="#6b8794" stroke-width="2"/>')
        L.a(f'<path d="M{x+70},{y-140} C{x+70},{y-190} {x+150},{y-190} {x+160},{y-220}" stroke="#2b2b2b" stroke-width="6" fill="none"/>')

def ph():
    L = Lienzo(1500, 760, 'pH en dos puntos: tampón 7 y tampón 4',
               'Antes de cada vaso: enjuagar la sonda y secarla con papel, sin frotar el bulbo. Esperar a que el valor no cambie más de 2 mV.')
    cols = [(50, 'Enjuagar y secar', None), (330, 'Tampón 7', ('#f3e27a', 'pH 7,00', '≈ 1500 mV', 'ph7')),
            (610, 'Enjuagar y secar', None), (890, 'Tampón 4', ('#f39a8a', 'pH 4,00', '≈ 2000 mV', 'ph4')),
            (1170, 'Comprobar', None)]
    for i, (x, tit, dat) in enumerate(cols):
        L.r(x, 90, 260, 560, '#fff', '#9aa8a2', 12)
        L.t(x + 130, 122, f'{i+1}. {tit}', 'b', 'middle', 'font-size:18px')
        if dat:
            col, et, mv, cmd = dat
            vaso(L, x + 60, 330, col, et)
            etiqueta_quien(L, x + 20, 560, 'PERSONA'); L.t(x + 120, 560, 'mete la sonda', 's', 'start')
            L.t(x + 130, 590, f'espera 1-2 min · {mv}', 's', 'middle', 'font-weight:700')
            etiqueta_quien(L, x + 20, 628, 'CLAUDE'); L.t(x + 110, 628, f'mv … y luego {cmd}', 'mono', 'start', 'fill:#6d4bd1;font-weight:700')
        elif i in (0, 2):
            # frasco lavador y chorro
            L.r(x + 40, 260, 70, 130, '#e6f3fb', '#7d8f99', 10, 2.5)
            L.a(f'<path d="M{x+75},{260} L{x+75},{225} L{x+140},{205}" stroke="#7d8f99" stroke-width="5" fill="none"/>')
            L.a(f'<path d="M{x+142},{205} Q{x+170},{215} {x+175},{270}" stroke="#53a7d8" stroke-width="3" fill="none" stroke-dasharray="6 4"/>')
            L.r(x + 165, 180, 22, 220, '#2b2b2b', '#111', 6)
            L.a(f'<ellipse cx="{x+176}" cy="{405}" rx="13" ry="17" fill="#cfe7f3" stroke="#6b8794" stroke-width="2"/>')
            L.t(x + 75, 420, 'agua destilada', 's', 'middle')
            L.r(x + 30, 470, 200, 40, '#faf6ee', '#c9bfa9', 4)
            L.t(x + 130, 495, 'papel: secar a toques', 's', 'middle')
            etiqueta_quien(L, x + 20, 560, 'PERSONA'); L.t(x + 120, 560, 'enjuaga y seca', 's', 'start')
            L.t(x + 130, 600, 'nunca frotar el bulbo', 'warn', 'middle')
        else:
            terminal(L, x + 12, 160, 236, [('> leer', 'monob'), ('pH=7.02  (en tampón 7)', 'mono'),
                                         ('> leer', 'monob'), ('pH=3.97  (en tampón 4)', 'mono'),
                                         ('> ver', 'monob'), ('ph7=1512 ph4=2018', 'mono')], 'Monitor')
            L.t(x + 130, 380, 'Bien si:', 'ok', 'middle')
            for k, lin in enumerate(['tampón 7 → 6,90 a 7,10', 'tampón 4 → 3,90 a 4,10', 'ph4 − ph7 ≈ 450-550 mV']):
                L.t(x + 130, 410 + 26 * k, lin, 's', 'middle', 'font-size:15px')
            L.t(x + 130, 520, 'Si no: repetir desde 2', 'warn', 'middle')
            L.t(x + 130, 560, 'Al acabar: sonda en agua', 's', 'middle', 'font-weight:700')
            L.t(x + 130, 582, 'o con su capuchón.', 's', 'middle', 'font-weight:700')
            L.t(x + 130, 610, 'Nunca seca.', 'warn', 'middle')
        if i < 4: L.flecha(x + 262, 370, x + 278, 370)
    L.t(28, 700, 'La calibración se guarda en la flash de la LILYGO: no se pierde al apagar ni al grabar otra vez el firmware. Repetir cada mes.', 'm', 'start')
    L.t(28, 724, 'Sin el SEN0681 el pH se compensa como si el agua estuviera a 25 °C: el error es de menos de 0,05 pH entre 15 y 30 °C.', 'm', 'start')
    L.guardar('calib-ph')

# ---------------------------------------------------------------- 5. Nivel
def nivel():
    L = Lienzo(1500, 800, 'Nivel: cero con el bidón vacío y tabla de 5 en 5 L',
               'El KIT0139 va de pie en el fondo. El SEN0204 va pegado por FUERA, a unos 12 cm del fondo. El tubo de aire, sin doblar y con la punta seca.')
    # bidón en corte
    x, y, w, h = 200, 130, 330, 520
    L.a(f'<path d="M{x},{y+40} Q{x},{y} {x+40},{y} L{x+110},{y} L{x+110},{y-30} L{x+220},{y-30} L{x+220},{y} L{x+w-40},{y} '
        f'Q{x+w},{y} {x+w},{y+40} L{x+w},{y+h-20} Q{x+w},{y+h} {x+w-20},{y+h} L{x+20},{y+h} Q{x},{y+h} {x},{y+h-20} Z" '
        'fill="#f9fbfc" stroke="#6f8390" stroke-width="4"/>')
    lleno = y + 70
    L.a(f'<rect x="{x+4}" y="{lleno}" width="{w-8}" height="{y+h-4-lleno}" fill="#8ccbef" opacity=".55"/>')
    # marcas de litros (el bidón se supone recto: es para orientarse)
    for k, lit in enumerate((5, 10, 15, 20, 25)):
        yy = y + h - (y + h - lleno) * (k + 1) / 5
        L.a(f'<path d="M{x+w+6},{yy:.0f} H{x+w+40}" stroke="#1e5fd0" stroke-width="2"/>')
        L.t(x + w + 46, yy + 5, f'{lit} L', 's', 'start', 'fill:#1e5fd0;font-weight:700')
        L.a(f'<path d="M{x+4},{yy:.0f} H{x+w-4}" stroke="#1e5fd0" stroke-width="1" stroke-dasharray="6 6" opacity=".6"/>')
    # sonda KIT0139 en el fondo
    L.r(x + 150, y + h - 90, 34, 84, '#c0c6ca', '#5d666b', 6, 2)
    L.t(x + 194, y + h - 50, 'KIT0139', 'b', 'start', 'font-size:14px')
    L.a(f'<path d="M{x+167},{y+h-90} C{x+167},{y+200} {x+150},{y-10} {x+165},{y-60}" stroke="#222" stroke-width="5" fill="none"/>')
    L.t(x + 190, y - 50, 'cable + tubo de aire (a la caja)', 's', 'start')
    # SEN0204 fuera
    s_y = y + h - 115
    L.r(x - 36, s_y - 22, 32, 44, '#2f3a8f', '#1b2363', 4, 2)
    L.t(x - 20, s_y - 32, 'SEN0204', 'b', 'middle', 'font-size:14px')
    L.t(x - 20, s_y + 40, '(por fuera)', 's', 'middle')
    L.a(f'<path d="M{x-60},{s_y+50} V{y+h}" stroke="#b3261e" stroke-width="2" marker-end="url(#fl)"/>')
    L.a(f'<path d="M{x-70},{s_y} H{x-38}" stroke="#b3261e" stroke-width="2"/>')
    L.t(x - 66, s_y + 90, '≈ 12 cm', 'warn', 'end')
    # garrafa
    gx, gy = 640, 170
    L.a(f'<path d="M{gx},{gy+40} L{gx+20},{gy+20} L{gx+50},{gy+20} L{gx+50},{gy} L{gx+80},{gy} L{gx+80},{gy+20} L{gx+120},{gy+20} '
        f'L{gx+140},{gy+40} L{gx+140},{gy+200} L{gx},{gy+200} Z" fill="#e9f5fd" stroke="#6f8390" stroke-width="3"/>')
    L.t(gx + 70, gy + 120, '5 L', 'b', 'middle', 'font-size:28px;fill:#1e5fd0')
    L.flecha(gx - 10, gy + 100, x + w - 30, y + 30, '#1e5fd0', 3, '8 6')
    L.t(gx + 70, gy + 235, 'garrafa: de 5 en 5 L', 's', 'middle', 'font-weight:700')
    # panel de pasos
    px = 800
    L.r(px, 100, 670, 250, '#fff', '#9aa8a2')
    L.t(px + 18, 130, 'A. Cero (bidón VACÍO)', 'b', 'start', 'font-size:18px')
    etiqueta_quien(L, px + 18, 168, 'PERSONA'); L.t(px + 122, 168, 'sonda de pie en el fondo, bidón vacío, 1 min', 's', 'start', 'font-size:15px')
    etiqueta_quien(L, px + 18, 204, 'CLAUDE'); L.t(px + 110, 204, 'mv (≈ 480 mV estable) → nivel0 → leer', 'mono', 'start', 'fill:#6d4bd1;font-weight:700')
    terminal(L, px + 18, 222, 634, [('Cero del nivel guardado: 9 mm', 'mono'), ('T=nan C  O2=nan mg/L  pH=7.01  nivel=0 mm ...', 'mono')], 'Monitor')
    L.r(px, 370, 670, 280, '#fff', '#9aa8a2')
    L.t(px + 18, 400, 'B. De 5 en 5 L (y el SEN0204)', 'b', 'start', 'font-size:18px')
    etiqueta_quien(L, px + 18, 436, 'PERSONA'); L.t(px + 122, 436, 'echa una garrafa y dice «listo»', 's', 'start', 'font-size:15px')
    etiqueta_quien(L, px + 18, 470, 'CLAUDE'); L.t(px + 110, 470, 'espera 30 s → leer → apunta nivel y agua', 's', 'start', 'font-size:15px')
    filas = [('Litros', 'nivel= (ejemplo)', 'agua='), ('5', '≈ 80 mm', '0'), ('10', '≈ 160 mm', '1 (lo pasa hacia 7-8 L)'),
             ('15', '≈ 240 mm', '1'), ('20', '≈ 320 mm', '1'), ('25', '≈ 400 mm → web', '1')]
    for k, (a1, a2, a3) in enumerate(filas):
        yy = 504 + 24 * k
        cls = 'b' if k == 0 else 's'
        L.t(px + 40, yy, a1, cls, 'start', 'font-size:14px'); L.t(px + 160, yy, a2, cls, 'start', 'font-size:14px')
        L.t(px + 380, yy, a3, cls, 'start', 'font-size:14px')
    L.t(28, 700, 'El valor con 25 L es el alturaLlenoMm de la web (raspberry/web/static/app.js, ahora 400): así el % y los litros de la tarjeta cuadran con el bidón.', 'm', 'start')
    L.t(28, 724, 'Los mm de la tabla son orientativos: el sensor tiene un error de unos ±25 mm en este bidón. Si agua no cambia nunca a 1, pulsar SET en la placa del SEN0204.', 'm', 'start')
    L.guardar('calib-nivel')

# ---------------------------------------------------------------- 6. Oxígeno
def oxigeno():
    L = Lienzo(1500, 740, 'Oxígeno (SEN0681): salinidad a 0 y punto del 100 % · solo con el módulo RS485',
               'Claude pregunta antes de mandar sal0, o2_100 y o2_cero, porque escriben dentro del sensor.')
    # paso 1 salinidad
    L.r(28, 90, 440, 560, '#fff', '#9aa8a2')
    L.t(48, 122, '1. Salinidad a 0 (agua de red)', 'b', 'start', 'font-size:18px')
    terminal(L, 48, 145, 400, [('> sal', 'monob'), ('Salinidad: registros 0x....', 'mono'), ('> sal0', 'monob'),
                               ('Salinidad a 0: OK', 'mono'), ('Salinidad: 0x0000 0x0000 (0)', 'mono')], 'Monitor')
    for k, lin in enumerate(['El SEN0681 es la versión de agua de mar:', 'puede venir con salinidad ≠ 0 y daría', 'el oxígeno mal en agua dulce.',
                             'Se hace una sola vez (se guarda en el sensor).', 'Apuntar el valor de fábrica.']):
        L.t(48, 330 + 26 * k, lin, 's', 'start', 'font-size:15px')
    etiqueta_quien(L, 48, 500, 'PERSONA'); L.t(150, 500, 'dice «sí» a poner 0', 's', 'start')
    etiqueta_quien(L, 48, 540, 'CLAUDE'); L.t(140, 540, 'sal → sal0', 'mono', 'start', 'fill:#6d4bd1;font-weight:700')
    # paso 2 botella
    bx = 520
    L.r(bx, 90, 460, 560, '#fff', '#9aa8a2')
    L.t(bx + 20, 122, '2. Punto del 100 % (aire saturado)', 'b', 'start', 'font-size:18px')
    cx, cy = bx + 140, 215
    L.a(f'<path d="M{cx-30},{cy} L{cx+30},{cy} L{cx+30},{cy+40} Q{cx+80},{cy+70} {cx+80},{cy+130} L{cx+80},{cy+380} '
        f'Q{cx+80},{cy+400} {cx+60},{cy+400} L{cx-60},{cy+400} Q{cx-80},{cy+400} {cx-80},{cy+380} L{cx-80},{cy+130} '
        f'Q{cx-80},{cy+70} {cx-30},{cy+40} Z" fill="#f4fafe" stroke="#6f8390" stroke-width="3"/>')
    L.a(f'<rect x="{cx-78}" y="{cy+320}" width="156" height="78" fill="#8ccbef" opacity=".6"/>')
    L.r(cx - 18, cy - 50, 36, 320, '#3a3f44', '#111', 6)                 # sonda
    L.a(f'<rect x="{cx-18}" y="{cy+262}" width="36" height="8" fill="#ffcf4a"/>')
    L.a(f'<path d="M{cx+40},{cy+270} H{cx+110}" stroke="#b3261e" stroke-width="2"/><path d="M{cx+40},{cy+320} H{cx+110}" stroke="#b3261e" stroke-width="2"/>')
    L.a(f'<path d="M{cx+100},{cy+272} V{cy+318}" stroke="#b3261e" stroke-width="2"/>')
    L.t(cx + 116, cy + 300, '1 cm', 'warn', 'start')
    L.t(cx + 116, cy + 262, 'membrana', 's', 'start')
    L.t(cx + 116, cy + 350, 'un poco de agua', 's', 'start')
    L.a(f'<path d="M{cx-40},{cy+2} Q{cx},{cy-16} {cx+40},{cy+2}" stroke="#9aa8a2" stroke-width="6" fill="none"/>')
    L.t(cx - 50, cy - 8, 'film tapando la boca', 's', 'end')
    for k, lin in enumerate(['a. Agitar la botella', '    cerrada 30 s.', 'b. Meter la sonda', '    sin tocar el agua.',
                             'c. leer cada minuto', '    5-10 min, hasta', '    3 lecturas iguales.', 'd. o2_100']):
        L.t(bx + 300, 190 + 30 * k, lin, 's', 'start', 'font-size:15px;font-weight:700' if lin.startswith('d') else 'font-size:15px')
    # paso 3 comprobación
    ox = 1032
    L.r(ox, 90, 440, 560, '#fff', '#9aa8a2')
    L.t(ox + 20, 122, '3. Comprobar en el bidón', 'b', 'start', 'font-size:18px')
    L.t(ox + 20, 156, 'O2 en agua dulce saturada de aire:', 's', 'start', 'font-size:15px')
    tabla = [('15 °C', 10.1), ('20 °C', 9.1), ('25 °C', 8.3), ('30 °C', 7.6)]
    for k, (tt, v) in enumerate(tabla):
        yy = 190 + 50 * k
        L.t(ox + 30, yy + 18, tt, 'b', 'start')
        L.r(ox + 110, yy, v * 26, 26, '#0e8fb5', '#0e8fb5', 4)
        L.t(ox + 120 + v * 26, yy + 18, f'{v:.1f} mg/L'.replace('.', ','), 's', 'start', 'font-weight:700')
    for k, lin in enumerate(['Bien si el O2 del bidón (agua que lleve', 'horas al aire) se parece a la tabla, ±0,5.',
                             'La T del SEN0681 tiene que dar lo mismo', 'que el termómetro, ±0,5 °C.',
                             'Cero con sulfito sódico: solo si lo hay', '(docs/13, apartado 5.3).']):
        L.t(ox + 20, 420 + 28 * k, lin, 's', 'start', 'font-size:15px')
    L.t(28, 690, 'Si sale rs485_err=1: con la fuente apagada, cambiar entre sí los dupont de las columnas 6 y 7; si sigue, cambiar A y B en el módulo. No se rompe nada.', 'm', 'start')
    L.guardar('calib-oxigeno')

for f in (flujo, puente, pantallas, ph, nivel, oxigeno):
    f()
print('SVG generados en', SAL)
