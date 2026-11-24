# Genera docs/img/montaje-visual.svg (esquema de montaje cable a cable del montaje simple)
import sys, random
W,H=1900,1380
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
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="DejaVu Sans, Arial, sans-serif" font-size="15">')
a('''<style>
.t{fill:#17201d}.m{fill:#4f5b57;font-size:13px}.h{font-weight:700;font-size:18px;fill:#17201d}
.b{font-weight:700;fill:#17201d}.s{font-size:12px;fill:#17201d}
.mono{font-family:DejaVu Sans Mono,monospace;font-size:12px;fill:#17201d;font-weight:700}
.pin{font-family:DejaVu Sans Mono,monospace;font-size:12px;fill:#ffe07a;font-weight:700}
.num{font-family:DejaVu Sans Mono,monospace;font-size:16px;font-weight:700;fill:#17201d}
.warn{fill:#b3261e;font-size:13px;font-weight:700}
</style>''')
a(f'<rect width="{W}" height="{H}" fill="#f6f8f7"/>')
t(30,42,'Montaje visual del nodo, cable a cable · montaje simple · LILYGO T3 V1.6.1 · firmware lilygo_t3_simple','h','start','font-size:24px')
t(30,66,'Todo pasa por una regleta de 20 clemas numeradas, agrupadas por sensor. Arriba entran los cables de los sensores; abajo, la fuente de 12 V, los puentes, las resistencias y los cables dupont a la LILYGO.','m','start')

# ---------- Regleta ----------
N=20; X0=300; CW=60; RY=720; RH=86; TOP=RY; BOT=RY+RH
def cx(i): return X0+CW*(i-1)+CW/2
R,G,O='#d32f2f','#222','#f07c00'
nets={1:('+12 V',R),2:('GND',G),3:('3V3',O),4:('GND',G),5:('DI',"#8e3fd1"),6:('RO',"#8a8f94"),7:('DE/RE',"#777"),
      8:('+12 V',R),9:('lazo',"#7a4a22"),10:('GND',G),11:('3V3',O),12:('nivel',"#1f9d48"),
      13:('GND',G),14:('3V3',O),15:('pH',"#1e5fd0"),16:('+12 V',R),17:('GND',G),18:('agua',"#f2c100"),19:('divisor',"#f2c100"),20:('GND',G)}
POST=[]
grupos=[(1,2,'SEN0681'),(3,7,'RS485'),(8,12,'nivel KIT0139'),(13,15,'pH'),(16,20,'agua SEN0204')]
a(f'<rect x="{X0-14}" y="{RY-12}" width="{CW*N+28}" height="{RH+24}" rx="8" fill="#e3e7e5" stroke="#9aa8a2"/>')
for i in range(1,N+1):
    x=X0+CW*(i-1)
    a(f'<rect x="{x+3}" y="{RY}" width="{CW-6}" height="{RH}" rx="5" fill="#fbfbf7" stroke="#8d9893" stroke-width="1.5"/>')
    a(f'<rect x="{x+3}" y="{RY+RH/2-15}" width="{CW-6}" height="30" fill="{nets[i][1]}" opacity=".2"/>')
    for yy in (RY+15,RY+RH-15):
        a(f'<circle cx="{x+CW/2}" cy="{yy}" r="9" fill="#d9b44a" stroke="#8a6d16" stroke-width="1.5"/><path d="M{x+CW/2-5},{yy} h10" stroke="#6b5310" stroke-width="2.5"/>')
    t(x+CW/2,RY+RH/2+1,str(i),'num')
    t(x+CW/2,RY+RH/2+13,nets[i][0],'s','middle','font-size:10.5px;font-weight:700')
for i0,i1,nm in grupos:
    x0=X0+CW*(i0-1)+4; x1=X0+CW*i1-4
    a(f'<path d="M{x0},{RY-22} H{x1}" stroke="#5c6b66" stroke-width="3"/>')
    POST.append((x0,x1,nm))
t(X0-22,RY+28,'arriba:','m','end'); t(X0-22,RY+44,'sensores','m','end')
t(X0-22,RY+66,'abajo:','m','end'); t(X0-22,RY+82,'LILYGO','m','end')
xr=X0+CW*N+26
t(xr,RY+26,'Regleta de clemas','b','start'); t(xr,RY+44,'20 bornas de tornillo','m','start')
t(xr,RY+62,'(la típica de ferretería:','m','start'); t(xr,RY+78,'una de 12 + 8 de otra)','m','start')

# ---------- cajas de sensores ----------
BY0,BY1=95,500  # cajas
def box(x,w,title,sub,fill='#fff',stroke='#9aa8a2'):
    a(f'<rect x="{x}" y="{BY0}" width="{w}" height="{BY1-BY0}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    t(x+12,BY0+22,title,'b','start'); t(x+12,BY0+40,sub,'m','start')
term=[]  # (x, col, clema, offset, label)
def stub(x,col,label,clema,off=0,ytop=None,lab2=None):
    # terminal en el borde inferior de la caja
    if ytop is not None: wire([(x,ytop),(x,BY1)],col)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[col] if col!="blanco" else "#fff"}" stroke="#333" stroke-width="1.2"/>')
    t(x+6,BY1-8,label,'s','start','font-size:10.5px;font-weight:700')
    if lab2: t(x+6,BY1-21,lab2,'s','start','font-size:10.5px')
    if clema: term.append((x,col,clema,off))

# SEN0681
box(30,240,'Oxígeno · SEN0681','O2 + temperatura · RS485 · 10-30 V')
a('<rect x="70" y="250" width="56" height="150" rx="10" fill="#cfd5d8" stroke="#6b7479" stroke-width="2"/><rect x="70" y="382" width="56" height="18" rx="4" fill="#2b2f33"/>')
t(98,420,'sonda dentro','m'); t(98,436,'del bidón','m')
a('<rect x="91" y="200" width="14" height="52" fill="#333"/>')
wire([(102,205),(102,182),(150,182),(150,440)],'marron'); stub(150,'marron','marrón',1,0,None,'+12 V')
wire([(107,205),(107,196),(215,196),(215,440)],'negro'); stub(215,'negro','negro',2,0,None,'GND')
for yy in (440,): pass
wire([(150,440),(150,BY1)],'marron'); wire([(215,440),(215,BY1)],'negro')
wire([(92,205),(92,152),(322,152),(322,235),(330,235)],'amarillo')
wire([(97,205),(97,166),(308,166),(308,262),(330,262)],'azul')
t(40,456,'amarillo → A','s','start','font-size:11px;font-weight:700'); t(40,471,'azul → B','s','start','font-size:11px;font-weight:700')

# RS485
box(290,260,'Módulo RS485 ↔ TTL','3,3 V (MAX3485) · POR CONSEGUIR','#fff','#c0392b')
a('<rect x="345" y="200" width="190" height="200" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
t(440,300,'MAX3485','pin')
for n,y in (('A',235),('B',262)):
    a(f'<rect x="330" y="{y-12}" width="26" height="24" fill="#2f8f3a" stroke="#1d5c25"/><circle cx="343" cy="{y}" r="6" fill="#d9b44a"/>')
    t(366,y+5,n,'pin','start')
ttl=[('VCC',365,'naranja',3,0),('GND',395,'negro',4,0),('DI',425,'morado',5,0),('RO',455,'gris',6,0),('DE',490,'blanco',7,0),('RE',520,'blanco',None,0)]
for n,x,c,cl,off in ttl:
    a(f'<rect x="{x-6}" y="396" width="12" height="14" fill="#d9b44a"/>')
    t(x,388,n,'pin','middle','font-size:10.5px')
wire([(490,410),(490,445),(520,445),(520,410)],'blanco',3); t(505,462,'DE+RE','s','middle','font-size:10px')
for n,x,c,cl,off in ttl[:5]:
    if n=='DE': wire([(490,445),(490,BY1)],c)
    else: wire([(x,410),(x,BY1)],c)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[c] if c!="blanco" else "#fff"}" stroke="#333" stroke-width="1.2"/>')
    term.append((x,c,cl,off))

# KIT0139
box(580,190,'Nivel · KIT0139','4-20 mA · 12-36 V · 0-5 m')
a('<rect x="610" y="300" width="50" height="120" rx="8" fill="#cfd5d8" stroke="#6b7479" stroke-width="2"/>'); t(635,440,'sonda','m'); t(635,456,'en el fondo','m')
a('<rect x="627" y="230" width="16" height="72" fill="#333"/>')
wire([(643,236),(705,236),(705,150)],'rojog',8); a('<circle cx="705" cy="145" r="7" fill="#fff" stroke="#e57373" stroke-width="3"/>')
t(712,180,'tubo de','warn','start'); t(712,196,'aire: no','warn','start'); t(712,212,'conectar','warn','start')
wire([(631,236),(631,260),(690,260),(690,BY1)],'rojo'); stub(690,'rojo','rojo',8,0,None,'+12 V')
wire([(639,240),(639,272),(735,272),(735,BY1)],'negro'); stub(735,'negro','negro',9,-8,None,'→ I+')

# Conversor
box(800,250,'Conversor 4-20 mA → V','SEN0262 · 3,3-5,5 V · 120 Ω')
a('<rect x="830" y="190" width="190" height="200" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
t(925,300,'SEN0262','pin')
conv=[('I+',845,'marron',9,8),('I−',885,'negro',10,-8),('GND',930,'negro',10,8),('VCC',970,'rojo',11,0),('SIG',1010,'azul',12,0)]
for n,x,c,cl,off in conv:
    if n in('I+','I−'):
        a(f'<rect x="{x-14}" y="378" width="28" height="22" fill="#2f8f3a" stroke="#1d5c25"/><circle cx="{x}" cy="389" r="6" fill="#d9b44a"/>')
    else:
        a(f'<rect x="{x-6}" y="388" width="12" height="12" fill="#fff" stroke="#333"/>')
    t(x,370,n,'pin','middle','font-size:10.5px')
    wire([(x,400),(x,BY1)],c)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[c]}" stroke="#333" stroke-width="1.2"/>')
    term.append((x,c,cl,off))


# pH
box(1080,220,'pH · SEN0169-V2','sonda BNC + placa · placa a 3V3')
a('<rect x="1100" y="300" width="34" height="120" rx="14" fill="#e8eef0" stroke="#6b7479" stroke-width="2"/>'); t(1117,440,'sonda','m'); t(1117,456,'siempre mojada','m','middle','font-size:11px')
wire([(1117,300),(1117,265),(1170,265)],'negro',5)
a('<rect x="1160" y="160" width="125" height="170" rx="6" fill="#1a5aa6" stroke="#0d2a4d" stroke-width="1.5"/>')
a('<rect x="1166" y="254" width="26" height="22" rx="3" fill="#c9c9c9" stroke="#555"/>'); t(1200,245,'BNC','pin','start')
t(1225,200,'placa pH','pin')
ph=[('−',1200,'negro',13,0),('+',1235,'rojo',14,0),('A',1270,'azul',15,0)]
for n,x,c,cl,off in ph:
    a(f'<rect x="{x-6}" y="318" width="12" height="12" fill="#fff" stroke="#333"/>'); t(x,310,n,'pin','middle','font-size:12px')
    wire([(x,330),(x,BY1)],c)
    a(f'<circle cx="{x}" cy="{BY1}" r="5" fill="{COL[c]}" stroke="#333" stroke-width="1.2"/>')
    term.append((x,c,cl,off))


# SEN0204
box(1330,260,'Presencia de agua · SEN0204','XKC-Y25 · 5-24 V · pegado por fuera')
a('<rect x="1350" y="170" width="34" height="290" fill="#3d7fd6" opacity=".30"/><rect x="1384" y="170" width="8" height="290" fill="#2a63b8"/>')
t(1350,162,'agua | pared del bidón','m','start','font-size:11px')
a('<rect x="1392" y="250" width="66" height="46" rx="5" fill="#f4f4f4" stroke="#333" stroke-width="2"/>'); t(1425,278,'Y25','mono')
t(1466,240,'a 12 cm del fondo','m','start','font-size:11px')
a('<rect x="1418" y="296" width="14" height="22" fill="#222"/>')
wire([(1420,318),(1420,386),(1430,386),(1430,BY1)],'marron'); stub(1430,'marron','marrón',16,0,None,'+12 V')
wire([(1424,318),(1424,374),(1484,374),(1484,BY1)],'azul'); stub(1484,'azul','azul',17,0,None,'GND')
wire([(1428,318),(1428,362),(1530,362),(1530,BY1)],'amarillo'); stub(1530,'amarillo','amarillo',18,0,None,'salida')
wire([(1432,318),(1432,334),(1572,334),(1572,316)],'negro',4)
a('<rect x="1562" y="292" width="20" height="26" rx="4" fill="#ffd54a" stroke="#333"/>')
t(1466,262,'negro (ADJ):','warn','start'); t(1466,278,'suelto, con cinta','m','start','font-size:11px')

# ---------- carriles: asignación con mínimo de cruces ----------
LY0,LY1=512,690
wires=[(x,c,cl,off) for (x,c,cl,off) in term if cl]
n=len(wires)
def segs(order):
    sp=(LY1-LY0)/(n)
    res=[]
    for k,idx in enumerate(order):
        x,c,cl,off=wires[idx]; y=LY0+sp*(k+0.5); xe=cx(cl)+off
        res.append((x,y,xe))
    return res
def crossings(order):
    s=segs(order); cnt=0
    for i in range(n):
        xi,yi,ei=s[i]
        for j in range(n):
            if i==j: continue
            xj,yj,ej=s[j]
            lo,hi=min(xi,ei),max(xi,ei)
            # vertical superior de j (x=xj, de BY1 a yj) cruza horizontal de i (en yi) si yi<yj
            if lo<xj<hi and yi<yj: cnt+=1
            # vertical inferior de j (x=ej, de yj a TOP) cruza horizontal de i si yi>yj
            if lo<ej<hi and yi>yj: cnt+=1
    return cnt
random.seed(4)
best=list(range(n)); bc=crossings(best)
for it in range(40000):
    cand=best[:]; i,j=random.sample(range(n),2); cand[i],cand[j]=cand[j],cand[i]
    cc=crossings(cand)
    if cc<=bc: best,bc=cand,cc
sys.stderr.write(f'cruces: {bc}\n')
for (x,y,xe),idx in zip(segs(best),best):
    c=wires[idx][1]
    wire([(x,BY1),(x,y),(xe,y),(xe,TOP+4)],c)

# ---------- Abajo: barras de reparto (puentes de cable de borna a borna) ----------
YR,YG,YO=BOT+52,BOT+72,BOT+92
def barra(clemas,col,y,x_ini,off):
    xs=[cx(i)+off for i in clemas]
    wire([(x_ini,y),(max(xs),y)],col,5)
    for x in xs: wire([(x,y),(x,BOT-4)],col,4)
barra([1,8,16],'rojo',YR,280,-12)
barra([2,4,10,13,17,20],'negro',YG,280,-12)
barra([3,11,14],'naranja',YO,cx(3)-12,-12)
t(1522,YR+5,'+12 V (rojo): 1 → 8 → 16','s','start','font-size:11.5px;font-weight:700;fill:#b71c1c')
t(1522,YG+5,'GND (negro): 2 → 4 → 10 → 13 → 17 → 20','s','start','font-size:11.5px;font-weight:700')
t(1522,YO+5,'3V3 (naranja): 3 → 11 → 14','s','start','font-size:11.5px;font-weight:700;fill:#b35900')

# Fuente de PC
a('<rect x="30" y="905" width="230" height="210" rx="10" fill="#fff4e5" stroke="#e0a060" stroke-width="1.5"/>')
t(42,927,'Fuente de PC','b','start'); t(42,945,'adaptada · 12 V · ≥ 1 A','m','start','font-size:12px')
a('<rect x="55" y="960" width="180" height="95" rx="6" fill="#9aa1a6" stroke="#555"/>')
for k in range(6): a(f'<circle cx="{80+k*26}" cy="1008" r="9" fill="#777" stroke="#555"/>')
t(145,1076,'si es ATX: verde (PS_ON)','m','middle','font-size:11.5px'); t(145,1092,'unido a un negro','m','middle','font-size:11.5px')
wire([(235,985),(262,985),(262,YR),(280,YR)],'amarillo',6)
wire([(235,1012),(272,1012),(272,YG),(280,YG)],'negro',6)
t(30,YR-8,'amarillo = +12 V','s','start','font-weight:700'); t(30,YG+18,'negro = GND','s','start','font-weight:700')

# LILYGO
LX,LY,LW,LH=400,1010,1060,200
a(f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="12" fill="#1d1f22" stroke="#000" stroke-width="2"/>')
a(f'<rect x="{LX+30}" y="{LY+70}" width="170" height="100" rx="4" fill="#0b2a3d" stroke="#5a7d90"/>')
t(LX+115,LY+115,'OLED','pin'); t(LX+115,LY+135,'logo Los Viveros','m','middle','fill:#9fc3d6;font-size:11px')
t(LX+LW/2+90,LY+110,'LILYGO T3 V1.6.1','t','middle','fill:#ffffff;font-size:24px;font-weight:700')
t(LX+LW/2+90,LY+137,'ESP32 + SX1276 · 868 MHz · busca cada pin por su nombre en la serigrafía','m','middle','fill:#c9d1cd')
t(LX+LW/2+90,LY+161,'sin tarjeta microSD · pin 5V sin usar · GPIO12 y GPIO34 sin conectar','m','middle','fill:#ffb4a8')
a(f'<path d="M{LX+LW},{LY+170} h40" stroke="#888" stroke-width="6"/><rect x="{LX+LW+38}" y="{LY+158}" width="70" height="24" rx="10" fill="#333"/>')
t(LX+LW+120,LY+168,'antena 868 MHz:','warn','start'); t(LX+LW+120,LY+184,'siempre puesta','warn','start')
a(f'<rect x="{LX-18}" y="{LY+90}" width="22" height="40" rx="4" fill="#b8b8b8" stroke="#555"/>')
a('<rect x="30" y="1150" width="250" height="100" rx="10" fill="#fff4e5" stroke="#e0a060" stroke-width="1.5"/>')
t(42,1172,'Cargador USB 5 V','b','start'); t(42,1190,'con batería de respaldo,','m','start'); t(42,1206,'enchufado a la regleta de 230 V','m','start','font-size:12px')
wire([(280,1220),(330,1220),(330,LY+110),(LX-18,LY+110)],'negro',8); t(285,LY+125,'cable USB','m','start')
pins=[(4,'GND','negro'),(3,'3V3','naranja'),(5,'GPIO13','morado'),(6,'GPIO14','gris'),(7,'GPIO25','blanco'),
      (12,'GPIO39','verde'),(15,'GPIO36','azul'),(19,'GPIO4','amarillo')]
for i,name,col in pins:
    x=cx(i)+ (8 if i in (3,4) else 0)
    wire([(x,BOT-4),(x,LY-4)],col)
    a(f'<rect x="{x-27}" y="{LY+8}" width="54" height="22" rx="3" fill="#2d3136" stroke="#d9b44a"/><rect x="{x-4}" y="{LY-4}" width="8" height="12" fill="#d9b44a"/>')
    t(x,LY+24,name,'pin','middle','font-size:11px')
t(840,LY-28,'cables dupont','m','middle','font-size:12px'); t(840,LY-13,'(hembra al pin)','m','middle','font-size:12px')
def resistor(x1,x2,y,label):
    xm=(x1+x2)/2
    a(f'<path d="M{x1},{BOT-4} V{y} H{xm-18} M{xm+18},{y} H{x2} V{BOT-4}" fill="none" stroke="#8a8a8a" stroke-width="2.5"/>')
    a(f'<rect x="{xm-18}" y="{y-8}" width="36" height="16" rx="6" fill="#e8cfa0" stroke="#7a5a2a"/>')
    cols=['#d32f2f','#8e3fd1','#f07c00'] if label.startswith('27') else ['#7a4a22','#222','#f07c00']
    for k,cc in enumerate(cols): a(f'<rect x="{xm-11+k*8}" y="{y-8}" width="4" height="16" fill="{cc}"/>')
resistor(cx(18)+8,cx(19)-8,BOT+24,'27k'); resistor(cx(19)+8,cx(20)+6,BOT+24,'10k')
t(1522,BOT+120,'27 kΩ entre 18 y 19 · 10 kΩ entre 19 y 20','s','start','font-size:11.5px;font-weight:700')
t(1522,BOT+138,'borna 19 ≈ 3,2 V con agua → GPIO4','m','start','font-size:11.5px')

# Puente de calibración
CX=LX+LW+40
a(f'<rect x="{CX}" y="{LY-10}" width="330" height="150" rx="10" fill="#fff" stroke="#9aa8a2"/>')
t(CX+14,LY+14,'Puente de calibración','b','start')
for k,nme in enumerate(['GPIO15','GND']):
    x=CX+80+k*150
    a(f'<rect x="{x-32}" y="{LY+32}" width="64" height="22" rx="3" fill="#2d3136" stroke="#d9b44a"/>'); t(x,LY+48,nme,'pin','middle','font-size:11.5px')
wire([(CX+80,LY+54),(CX+80,LY+78),(CX+230,LY+78),(CX+230,LY+54)],'marron',4)
t(CX+14,LY+106,'dupont hembra-hembra entre los dos pines.','m','start'); t(CX+14,LY+122,'Puesto al encender = modo calibración.','m','start')

# ---------- Leyenda ----------
GX=1620
a(f'<rect x="{GX}" y="95" width="260" height="600" rx="10" fill="#fff" stroke="#9aa8a2"/>')
t(GX+14,120,'Código de colores','b','start')
leg=[('rojo','+12 V / VCC'),('negro','GND (una sola masa)'),('naranja','3V3 de la LILYGO'),('amarillo','+12 V fuente · salida agua'),
     ('marron','+12 V sensores · lazo 4-20'),('azul','pH · SIG nivel · GND agua'),('verde','nivel → GPIO39'),('morado','GPIO13 → DI'),
     ('gris','RO → GPIO14'),('blanco','GPIO25 → DE+RE'),('rojog','tubo de aire (no es cable)')]
for k,(c,txt) in enumerate(leg):
    y=150+k*26; wire([(GX+16,y),(GX+56,y)],c,6); t(GX+66,y+5,txt,'s','start')
y=450
for s_,cls in [('Colores de los sensores: los de su','m'),('propio cable (wikis de DFRobot).','m'),('Dupont y puentes: si no tenéis','m'),
               ('ese color, da igual; lo que manda','m'),('es el número de borna y el pin.','m'),('',''),('Antes de pinchar la LILYGO:','warn'),
               ('ningún cable de GPIO > 3,3 V.','m'),('La borna 18 lleva 12 V:','m'),('nunca directa a un GPIO.','m')]:
    if s_: t(GX+14,y,s_,cls,'start')
    y+=18
t(GX+14,y+8,'Bomba: aparte, sin conexión.','m','start')

t(30,1290,'El módulo RS485 está por conseguir: sin él, el SEN0681 no se lee (el firmware marca fallo RS485 y compensa el pH con 25 °C). Si el módulo es de dirección automática (pines TXD/RXD), la borna 7 y el GPIO25 sobran.','m','start')
t(30,1312,'Si el SEN0681 no responde: cambiar entre sí los cables de las bornas 5 y 6, o los de A y B (no se rompe nada). Nada de 230 V dentro de la caja: la fuente y el cargador van enchufados fuera, a la regleta del inversor.','m','start')
t(30,1334,'Fuentes: wikis de DFRobot (SEN0681, SEN0204, KIT0139, SEN0262, SEN0169-V2) y firmware/nodo-agua/include/config.h. Pasos del montaje: docs/12-guia-montaje.md','m','start')
for x0,x1,nm in POST:
    a(f'<rect x="{(x0+x1)/2-len(nm)*3.8-6}" y="{RY-31}" width="{len(nm)*7.6+12}" height="17" rx="3" fill="#5c6b66"/>')
    t((x0+x1)/2,RY-18,nm,'s','middle','font-size:11px;font-weight:700;fill:#ffffff')
a('</svg>')
open(sys.argv[1],'w').write('\n'.join(o))
