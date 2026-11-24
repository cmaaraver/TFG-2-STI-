# Genera docs/img/montaje-visual.svg: montaje del nodo en la protoboard de la caja estanca, cable a cable.
# Uso: python3 montaje-visual.py salida.svg
import sys, random
W,H=1900,1430
o=[]
def a(s): o.append(s)
COL={'rojo':'#d32f2f','negro':'#222','amarillo':'#f2c100','azul':'#1e5fd0','marron':'#7a4a22',
     'naranja':'#f07c00','morado':'#8e3fd1','gris':'#8a8f94','blanco':'#ffffff','verde':'#1f9d48','rojog':'#e57373'}
def wire(pts,col,w=4.5):
    d='M'+' L'.join(f'{x:.0f},{y:.0f}' for x,y in pts)
    halo='#555' if col=='blanco' else '#ffffff'
    a(f'<path d="{d}" fill="none" stroke="{halo}" stroke-width="{w+(2.5 if col=="blanco" else 3)}" stroke-linejoin="round" stroke-linecap="round"/>')
    a(f'<path d="{d}" fill="none" stroke="{COL[col]}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')
def t(x,y,s,cls='t',anchor='middle',st=''):
    a(f'<text x="{x:.0f}" y="{y:.0f}" class="{cls}" text-anchor="{anchor}"'+(f' style="{st}"' if st else '')+f'>{s}</text>')
def tip(x,y,col):  # punta del cable metida en un agujero
    a(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4.5" fill="{COL[col] if col!="blanco" else "#fff"}" stroke="#111" stroke-width="1.3"/>')
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="DejaVu Sans, Arial, sans-serif" font-size="15">')
a('''<style>
.t{fill:#17201d}.m{fill:#4f5b57;font-size:13px}.h{font-weight:700;font-size:18px;fill:#17201d}
.b{font-weight:700;fill:#17201d}.s{font-size:12px;fill:#17201d}
.mono{font-family:DejaVu Sans Mono,monospace;font-size:12px;fill:#17201d;font-weight:700}
.pin{font-family:DejaVu Sans Mono,monospace;font-size:12px;fill:#ffe07a;font-weight:700}
.num{font-family:DejaVu Sans Mono,monospace;font-size:10px;fill:#6b7570}
.warn{fill:#b3261e;font-size:13px;font-weight:700}
</style>''')
a(f'<rect width="{W}" height="{H}" fill="#f6f8f7"/>')
t(30,42,'Montaje del nodo en la protoboard, cable a cable · LILYGO T3 V1.6.1 · firmware lilygo_t3_simple','h','start','font-size:24px')
t(30,66,'Arriba, los sensores con el color real de sus cables. En medio, la protoboard de la caja estanca (columnas numeradas). Abajo, los cables dupont a la LILYGO y la alimentación.','m','start')

# ---------- Protoboard ----------
PX=36; X0=372; NC=30
def bx(c): return X0+(c-1)*PX
ROWS={'T+':668,'T-':690,'a':724,'b':746,'c':768,'d':790,'e':812,'f':856,'g':878,'h':900,'i':922,'j':944,'B-':978,'B+':1000}
def hole(c,r): return (bx(c),ROWS[r])
BX0,BX1,BY0b,BY1b=bx(1)-34,bx(NC)+34,646,1020
a(f'<rect x="{BX0}" y="{BY0b}" width="{BX1-BX0}" height="{BY1b-BY0b}" rx="10" fill="#fdfdfb" stroke="#b9c0bc" stroke-width="2"/>')
a(f'<rect x="{BX0+8}" y="{ROWS["e"]+15}" width="{BX1-BX0-16}" height="{ROWS["f"]-ROWS["e"]-30}" rx="3" fill="#e6e9e7"/>')
for r,col,lab in (('T+','#d32f2f','+12 V'),('T-','#1e5fd0','GND'),('B-','#1e5fd0','GND'),('B+','#f07c00','3V3 (¡no 12 V!)')):
    y=ROWS[r]+(-11 if r in('T+','B-') else 11)
    a(f'<path d="M{bx(1)-12},{y} H{bx(NC)+12}" stroke="{col}" stroke-width="2"/>')
    t(BX0-8,ROWS[r]+4,('+' if '+' in r else '−'),'b','end',f'fill:{col};font-size:16px')
    t(BX1+10,ROWS[r]+4,lab,'s','start',f'font-weight:700;fill:{col}')
for c in range(1,NC+1):
    for r in ROWS:
        x,y=hole(c,r)
        a(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" rx="1.5" fill="#3b3f3d" opacity=".75"/>')
    t(bx(c),ROWS['a']-12+0,str(c),'num') if c%1==0 else None
for r in 'abcdefghij':
    t(BX0+16,ROWS[r]+4,r,'num'); t(BX1-16,ROWS[r]+4,r,'num')
t(BX1+10,ROWS['c']+4,'columnas 1-30','m','start'); t(BX1+10,ROWS['c']+20,'(cada columna a-e','m','start'); t(BX1+10,ROWS['c']+36,'está unida por dentro)','m','start')
t(BX1+10,ROWS['h']+4,'mitad de abajo (f-j):','m','start'); t(BX1+10,ROWS['h']+20,'no se usa','m','start')

# ---------- cajas de sensores ----------
BY0,BY1=95,470
def box(x,w,title,sub,stroke='#9aa8a2'):
    a(f'<rect x="{x}" y="{BY0}" width="{w}" height="{BY1-BY0}" rx="10" fill="#fff" stroke="{stroke}" stroke-width="1.5"/>')
    t(x+12,BY0+22,title,'b','start'); t(x+12,BY0+40,sub,'m','start')
term=[]   # (x, color, destino(col,fila), etiqueta)
def salida(x,col,dest,lab1,lab2=None):
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[col] if col!="blanco" else "#fff"}" stroke="#333" stroke-width="1.2"/>')
    t(x+6,BY1-8,lab1,'s','start','font-size:10.5px;font-weight:700')
    if lab2: t(x+6,BY1-21,lab2,'s','start','font-size:10.5px')
    term.append((x,col,dest))

# SEN0681
box(30,240,'Oxígeno · SEN0681','O2 + temperatura · RS485 · 10-30 V')
a('<rect x="70" y="240" width="56" height="140" rx="10" fill="#cfd5d8" stroke="#6b7479" stroke-width="2"/><rect x="70" y="362" width="56" height="18" rx="4" fill="#2b2f33"/>')
t(98,400,'sonda dentro','m'); t(98,416,'del bidón','m')
a('<rect x="91" y="196" width="14" height="46" fill="#333"/>')
wire([(102,200),(102,182),(150,182),(150,BY1)],'marron'); salida(150,'marron',(2,'T+'),'marrón','+12 V')
wire([(107,200),(107,192),(215,192),(215,BY1)],'negro'); salida(215,'negro',(3,'T-'),'negro','GND')
wire([(92,200),(92,152),(322,152),(322,235),(330,235)],'amarillo')
wire([(97,200),(97,166),(308,166),(308,262),(330,262)],'azul')
t(40,436,'amarillo → A','s','start','font-size:11px;font-weight:700'); t(40,451,'azul → B','s','start','font-size:11px;font-weight:700')

# RS485
box(290,260,'Módulo RS485 ↔ TTL','3,3 V (MAX3485) · POR CONSEGUIR','#c0392b')
a('<rect x="345" y="200" width="190" height="180" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
t(440,290,'MAX3485','pin')
for n,y in (('A',235),('B',262)):
    a(f'<rect x="330" y="{y-12}" width="26" height="24" fill="#2f8f3a" stroke="#1d5c25"/><circle cx="343" cy="{y}" r="6" fill="#d9b44a"/>')
    t(366,y+5,n,'pin','start')
ttl=[('VCC',365,'naranja',(4,'B+')),('GND',395,'negro',(5,'T-')),('DI',425,'morado',(6,'a')),('RO',455,'gris',(7,'a')),('DE',490,'blanco',(8,'a')),('RE',520,'blanco',None)]
for n,x,c,d in ttl:
    a(f'<rect x="{x-6}" y="376" width="12" height="14" fill="#d9b44a"/>'); t(x,368,n,'pin','middle','font-size:10.5px')
wire([(490,390),(490,420),(520,420),(520,390)],'blanco',3); t(505,437,'DE+RE','s','middle','font-size:10px')
for n,x,c,d in ttl[:5]:
    wire([(x,420 if n=='DE' else 390),(x,BY1)],c)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[c] if c!="blanco" else "#fff"}" stroke="#333" stroke-width="1.2"/>')
    term.append((x,c,d))

# KIT0139
box(580,190,'Nivel · KIT0139','sonda 4-20 mA · 12-36 V')
a('<rect x="610" y="290" width="50" height="110" rx="8" fill="#cfd5d8" stroke="#6b7479" stroke-width="2"/>'); t(635,418,'sonda','m'); t(635,434,'en el fondo','m')
a('<rect x="627" y="226" width="16" height="66" fill="#333"/>')
wire([(643,232),(705,232),(705,150)],'rojog',8); a('<circle cx="705" cy="145" r="7" fill="#fff" stroke="#e57373" stroke-width="3"/>')
t(712,180,'tubo de','warn','start'); t(712,196,'aire: no','warn','start'); t(712,212,'conectar','warn','start')
wire([(631,232),(631,256),(690,256),(690,BY1)],'rojo'); salida(690,'rojo',(10,'T+'),'rojo','+12 V')
wire([(639,236),(639,268),(735,268),(735,BY1)],'negro'); salida(735,'negro',(11,'a'),'negro','→ col 11')

# Conversor
box(800,250,'Conversor 4-20 mA → V','SEN0262 · viene en la caja del KIT0139')
a('<rect x="830" y="190" width="190" height="190" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
t(925,280,'SEN0262','pin'); t(925,300,'(placa azul pequeña)','m','middle','fill:#cfe0f5;font-size:11px')
conv=[('I+',845,'marron',(11,'b')),('I−',885,'negro',(12,'T-')),('GND',930,'negro',(13,'T-')),('VCC',970,'rojo',(14,'B+')),('SIG',1010,'azul',(15,'a'))]
for n,x,c,d in conv:
    if n in('I+','I−'):
        a(f'<rect x="{x-14}" y="368" width="28" height="22" fill="#2f8f3a" stroke="#1d5c25"/><circle cx="{x}" cy="379" r="6" fill="#d9b44a"/>')
    else:
        a(f'<rect x="{x-6}" y="378" width="12" height="12" fill="#fff" stroke="#333"/>')
    t(x,360,n,'pin','middle','font-size:10.5px')
    wire([(x,390),(x,BY1)],c)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[c]}" stroke="#333" stroke-width="1.2"/>')
    term.append((x,c,d))


# pH
box(1080,220,'pH · SEN0169-V2','sonda BNC + placa · placa a 3V3')
a('<rect x="1100" y="290" width="34" height="110" rx="14" fill="#e8eef0" stroke="#6b7479" stroke-width="2"/>'); t(1117,418,'sonda','m'); t(1117,434,'siempre mojada','m','middle','font-size:11px')
wire([(1117,290),(1117,265),(1170,265)],'negro',5)
a('<rect x="1160" y="160" width="125" height="170" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
a('<rect x="1166" y="254" width="26" height="22" rx="3" fill="#c9c9c9" stroke="#555"/>'); t(1200,245,'BNC','pin','start')
t(1225,200,'placa pH','pin')
ph=[('−',1200,'negro',(17,'T-')),('+',1235,'rojo',(18,'B+')),('A',1270,'azul',(19,'a'))]
for n,x,c,d in ph:
    a(f'<rect x="{x-6}" y="318" width="12" height="12" fill="#fff" stroke="#333"/>'); t(x,310,n,'pin','middle','font-size:12px')
    wire([(x,330),(x,BY1)],c)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[c]}" stroke="#333" stroke-width="1.2"/>')
    term.append((x,c,d))

# SEN0204 con su placa adaptadora
box(1330,270,'Presencia de agua · SEN0204','sensor Y25 + su placa adaptadora')
a('<rect x="1348" y="160" width="30" height="200" fill="#3d7fd6" opacity=".30"/><rect x="1378" y="160" width="7" height="200" fill="#2a63b8"/>')
t(1348,152,'agua | pared','m','start','font-size:11px')
a('<rect x="1385" y="200" width="56" height="42" rx="5" fill="#f4f4f4" stroke="#333" stroke-width="2"/>'); t(1413,226,'Y25','mono')
t(1348,380,'a 12 cm del fondo,','m','start','font-size:11px'); t(1348,394,'pegado por fuera','m','start','font-size:11px')
# 4 hilos a la placa
for k,c in enumerate(['marron','amarillo','azul','negro']):
    wire([(1428+k*0, 242),(1428,0)],c,0.1) if False else None
for k,c in enumerate(['marron','amarillo','azul','negro']):
    x0=1404+k*8
    wire([(x0,242),(x0,262+k*0),(1470+k*12,262),(1470+k*12,290)],c,3)
a('<rect x="1455" y="288" width="110" height="78" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
t(1510,306,'placa adaptadora','pin','middle','font-size:10px')
a('<rect x="1468" y="316" width="22" height="16" rx="3" fill="#ddd" stroke="#333"/>'); t(1479,328,'SET','mono','middle','font-size:8px')
t(1468,346,'4 hilos entran','m','start','font-size:9.5px;fill:#cfe0f5'); t(1468,358,'3 hilos salen','m','start','font-size:9.5px;fill:#cfe0f5')
sen=[('rojo',1462,(21,'T+'),'rojo','+12 V'),('negro',1512,(22,'T-'),'negro','GND'),('verde',1560,(23,'a'),'verde','salida')]
for c,x,d,l1,l2 in sen:
    a(f'<rect x="{x-5}" y="366" width="10" height="10" fill="#fff" stroke="#333"/>')
    wire([(x,376),(x,BY1)],c); salida(x,c,d,l1,None)


# ---------- carriles: asignación con mínimo de cruces ----------
LY0,LY1=480,640
n=len(term)
def fin(d):
    c,r=d; x,y=hole(c,r); return x,y
def segs(order):
    sp=(LY1-LY0)/n; res=[]
    for k,idx in enumerate(order):
        x,c,d=term[idx]; xe,ye=fin(d); res.append((x,LY0+sp*(k+0.5),xe,ye))
    return res
def crossings(order):
    s=segs(order); cnt=0
    for i in range(n):
        xi,yi,ei,_=s[i]; lo,hi=min(xi,ei),max(xi,ei)
        for j in range(n):
            if i==j: continue
            xj,yj,ej,fj=s[j]
            if lo<xj<hi and yi<yj: cnt+=1
            if lo<ej<hi and yi>yj: cnt+=1
    return cnt
random.seed(7); best=list(range(n)); bc=crossings(best)
for it in range(60000):
    cand=best[:]; i,j=random.sample(range(n),2); cand[i],cand[j]=cand[j],cand[i]
    cc=crossings(cand)
    if cc<=bc: best,bc=cand,cc
sys.stderr.write(f'cruces: {bc}\n')
for (x,y,xe,ye),idx in zip(segs(best),best):
    c=term[idx][1]; wire([(x,BY1),(x,y),(xe,y),(xe,ye)],c,4); tip(xe,ye,c)

# ---------- puentes y resistencias en la protoboard ----------
# puente GND de arriba (T-) a GND de abajo (B-), por la izquierda
x1,y1=hole(2,'T-'); x2,y2=hole(1,'B-')
wire([(x1,y1),(x1,y1+14),(x1-58,y1+14),(x1-58,y2),(x2,y2)],'negro',4); tip(x1,y1,'negro'); tip(x2,y2,'negro')
t(x1-64,(y1+y2)/2,'puente','s','end','font-size:11px;font-weight:700'); t(x1-64,(y1+y2)/2+15,'GND','s','end','font-size:11px;font-weight:700')
# 27k entre columna 20 (fila c) y 24 (fila c)
def resistor(p1,p2,label,cols):
    (x1,y1),(x2,y2)=p1,p2
    xm,ym=(x1+x2)/2,(y1+y2)/2
    a(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#8a8a8a" stroke-width="2.5"/>')
    import math
    ang=math.degrees(math.atan2(y2-y1,x2-x1))
    a(f'<g transform="translate({xm},{ym}) rotate({ang})"><rect x="-20" y="-7" width="40" height="14" rx="6" fill="#e8cfa0" stroke="#7a5a2a"/>'+''.join(f'<rect x="{-12+k*7}" y="-7" width="3.5" height="14" fill="{cc}"/>' for k,cc in enumerate(cols))+'</g>')
    tip(x1,y1,'gris'); tip(x2,y2,'gris')
resistor(hole(23,'c'),hole(27,'c'),'27k',['#d32f2f','#8e3fd1','#f07c00'])
resistor(hole(27,'b'),hole(29,'T-'),'10k',['#7a4a22','#222','#f07c00'])
t(bx(25),ROWS['d']+20,'27 kΩ','s','middle','font-size:11px;font-weight:700')
t(bx(29)+10,ROWS['T-']+40,'10 kΩ','s','start','font-size:11px;font-weight:700')
# DE+RE no; etiquetas de columnas usadas (en el canal central)
labs={6:'DI',7:'RO',8:'DE',11:'lazo',15:'nivel',19:'pH',23:'agua',27:'divisor'}
for c,l in labs.items():
    t(bx(c)+7,ROWS['g']+4,l,'s','start','font-size:11px;font-weight:700;fill:#33413b')

# ---------- Fuente y LILYGO ----------
a('<rect x="30" y="690" width="230" height="200" rx="10" fill="#fff4e5" stroke="#e0a060" stroke-width="1.5"/>')
t(42,712,'Fuente de PC','b','start'); t(42,730,'adaptada · 12 V · ≥ 1 A','m','start','font-size:12px')
a('<rect x="55" y="748" width="150" height="90" rx="6" fill="#9aa1a6" stroke="#555"/>')
for k in range(5): a(f'<circle cx="{76+k*27}" cy="794" r="8" fill="#777" stroke="#555"/>')
t(145,860,'si es ATX: verde (PS_ON)','m','middle','font-size:11px'); t(145,875,'unido a un negro','m','middle','font-size:11px')
xa,ya=hole(1,'T+'); xn,yn=hole(1,'T-')
wire([(205,770),(275,770),(275,ya),(xa,ya)],'amarillo',5); tip(xa,ya,'amarillo')
wire([(205,812),(300,812),(300,yn),(xn,yn)],'negro',5); tip(xn,yn,'negro')
t(250,ya-32,'amarillo +12 V','s','start','font-size:11px;font-weight:700') if False else None
t(30,906,'amarillo → + de arriba (12 V)','s','start','font-size:11.5px;font-weight:700'); t(30,922,'negro → − de arriba (GND)','s','start','font-size:11.5px;font-weight:700')

LX,LY,LW,LH=330,1110,1130,190
a(f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="12" fill="#1d1f22" stroke="#000" stroke-width="2"/>')
a(f'<rect x="{LX+30}" y="{LY+60}" width="170" height="100" rx="4" fill="#0b2a3d" stroke="#5a7d90"/>')
t(LX+115,LY+105,'OLED','pin'); t(LX+115,LY+125,'logo Los Viveros','m','middle','fill:#9fc3d6;font-size:11px')
t(LX+LW/2+90,LY+100,'LILYGO T3 V1.6.1 (fuera de la protoboard)','t','middle','fill:#ffffff;font-size:22px;font-weight:700')
t(LX+LW/2+90,LY+127,'cables dupont macho-hembra: el macho a la protoboard, la hembra al pin de la LILYGO','m','middle','fill:#c9d1cd')
t(LX+LW/2+90,LY+151,'GPIO36 = VP y GPIO39 = VN en la serigrafía · sin microSD · pin 5V, GPIO12 y GPIO34 sin conectar','m','middle','fill:#ffb4a8')
a(f'<path d="M{LX+LW},{LY+160} h40" stroke="#888" stroke-width="6"/><rect x="{LX+LW+38}" y="{LY+148}" width="70" height="24" rx="10" fill="#333"/>')
t(LX+LW+120,LY+158,'antena 868 MHz:','warn','start'); t(LX+LW+120,LY+174,'siempre puesta','warn','start')
a(f'<rect x="{LX-18}" y="{LY+80}" width="22" height="40" rx="4" fill="#b8b8b8" stroke="#555"/>')
a('<rect x="30" y="1170" width="230" height="100" rx="10" fill="#fff4e5" stroke="#e0a060" stroke-width="1.5"/>')
t(42,1192,'Cargador USB 5 V','b','start'); t(42,1210,'con batería de respaldo','m','start')
wire([(260,1240),(300,1240),(300,LY+100),(LX-18,LY+100)],'negro',8); t(36,1292,'cable USB de datos → LILYGO','m','start')
pins=[(2,'B+','3V3','naranja',385),(3,'B-','GND','negro',455),(6,'e','GPIO13','morado',540),(7,'e','GPIO14','gris',610),(8,'e','GPIO25','blanco',680),
      (15,'e','VN (39)','verde',876),(19,'e','VP (36)','azul',1020),(27,'e','GPIO4','amarillo',1308)]
for c,r,name,col,xp in pins:
    x0,y=hole(c,r)
    wire([(x0,y),(x0,1060),(xp,1060),(xp,LY-4)],col,4.5); tip(x0,y,col); x=xp
    a(f'<rect x="{x-27}" y="{LY+8}" width="54" height="22" rx="3" fill="#2d3136" stroke="#d9b44a"/><rect x="{x-4}" y="{LY-4}" width="8" height="12" fill="#d9b44a"/>')
    t(x,LY+24,name,'pin','middle','font-size:11px')

# Puente de calibración
CX=LX+LW+40
a(f'<rect x="{CX}" y="{LY-20}" width="330" height="140" rx="10" fill="#fff" stroke="#9aa8a2"/>')
t(CX+14,LY+4,'Puente de calibración','b','start')
for k,nme in enumerate(['GPIO15','GND']):
    x=CX+80+k*150
    a(f'<rect x="{x-32}" y="{LY+20}" width="64" height="22" rx="3" fill="#2d3136" stroke="#d9b44a"/>'); t(x,LY+36,nme,'pin','middle','font-size:11.5px')
wire([(CX+80,LY+42),(CX+80,LY+64),(CX+230,LY+64),(CX+230,LY+42)],'marron',4)
t(CX+14,LY+90,'dupont hembra-hembra entre los dos pines.','m','start'); t(CX+14,LY+106,'Puesto al encender = modo calibración.','m','start')

# ---------- Leyenda ----------
GX=1620
a(f'<rect x="{GX}" y="95" width="260" height="540" rx="10" fill="#fff" stroke="#9aa8a2"/>')
t(GX+14,120,'Código de colores','b','start')
leg=[('rojo','+12 V (o VCC del cable)'),('negro','GND (una sola masa)'),('naranja','3V3 de la LILYGO'),('amarillo','+12 V de la fuente · GPIO4'),
     ('marron','+12 V SEN0681 · lazo I+'),('verde','salida SEN0204 · VN (39)'),('azul','señal pH / nivel · VP (36)'),('morado','DI ↔ GPIO13'),
     ('gris','RO ↔ GPIO14'),('blanco','DE+RE ↔ GPIO25'),('rojog','tubo de aire (no es cable)')]
for k,(c,txt) in enumerate(leg):
    y=150+k*25; wire([(GX+16,y),(GX+56,y)],c,6); t(GX+66,y+5,txt,'s','start')
y=436
for s_,cls in [('Colores de los sensores: los de','m'),('su propio cable. Los dupont','m'),('pueden ser de otro color: manda','m'),
               ('la columna y el nombre del pin.','m'),('',''),('Antes de pinchar la LILYGO:','warn'),('ningún cable de GPIO > 3,3 V;','m'),
               ('la columna 23 lleva 12 V.','m'),('Bomba: aparte, sin conexión.','m')]:
    if s_: t(GX+14,y,s_,cls,'start')
    y+=18

t(30,1345,'El módulo RS485 está por conseguir: sin él, el SEN0681 no se lee (el firmware marca fallo RS485 y compensa el pH con 25 °C). Si es de dirección automática (pines TXD/RXD), la columna 8 y el GPIO25 sobran.','m','start')
t(30,1367,'Si el SEN0681 no responde: cambiar entre sí los cables de las columnas 6 y 7, o A y B (no se rompe nada). Nada de 230 V dentro de la caja: la fuente y el cargador se enchufan fuera, a la regleta del inversor.','m','start')
t(30,1389,'Puntas de los cables de los sensores: estañadas o con un pin macho crimpado, que el cable de hilos sueltos no agarra bien en la protoboard. Fuentes: wikis de DFRobot (SEN0681, SEN0204, KIT0139, SEN0262, SEN0169-V2) y config.h.','m','start')
t(30,1411,'Pasos del montaje: docs/12-guia-montaje.md','m','start')
a('</svg>')
open(sys.argv[1],'w').write('\n'.join(o))
