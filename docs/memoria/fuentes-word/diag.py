import re
import os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../img/')  # docs/img del repositorio
s=open(R+'instalacion-sensores.svg',encoding='utf8').read()
s=s.replace('Detalle en docs/06-maqueta.md y docs/08-guia-instalacion.md.','La bomba va aparte, con su propia alimentación.')
s=s.replace('LILYGO + placa base','LILYGO T3 V1.6.1').replace('ADS1115, placa pH,','placa del pH,').replace('aislador, RS485','conversor 4-20 mA,').replace('pantalla visible por','módulo RS485,').replace('la tapa transparente','resistencias y diodo')
s=s.replace('Caja 1 (IP66)','Caja del nodo').replace('prensaestopas y GX16','entradas de cable').replace('BNC → caja del nodo','BNC → placa del pH').replace('RS485 + 12 V (GX16 4 pines)','RS485 + 12 V')
s=s.replace('<rect x="60" y="170" width="12" height="300" fill="#78716c"/>','').replace('<polygon points="30,290 250,170 262,190 42,310" fill="#1e3a8a" stroke="#111" stroke-width="2"/>','')
s=re.sub(r'<text[^>]*>Panel 50 W[^<]*</text>','',s)
s=s.replace('Bomba 12 V sumergida + rejilla','Bomba sumergida + rejilla')
s=s.replace('Caja 2 (a la sombra)','Alimentación (a cubierto)').replace('MPPT + LiFePO4 12,8 V','regleta 230 V (inversor solar)').replace('20 Ah + fusibles','fuente 12 V → sensores').replace('12 V → caja 1','cargador USB 5 V → LILYGO')
open('plano-sondas.svg','w',encoding='utf8').write(s)

def svg(w,h,body,title,sub=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="DejaVu Sans, Arial, sans-serif">
<defs><marker id="a" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M1,1 L11,6 L1,11 z" fill="#334155"/></marker>
<marker id="b" markerWidth="12" markerHeight="12" refX="2" refY="6" orient="auto"><path d="M11,1 L1,6 L11,11 z" fill="#334155"/></marker></defs>
<rect width="{w}" height="{h}" fill="#fff"/>
<text x="30" y="42" font-size="24" font-weight="700" fill="#0f172a">{title}</text>
<text x="30" y="68" font-size="14" fill="#475569">{sub}</text>
{body}</svg>'''
def box(x,y,w,h,t,lines=(),fill='#f1f5f9',st='#334155'):
    o=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{st}" stroke-width="2"/>'
    fs=min(15,round((w-16)/(len(t)*0.64),1))
    o+=f'<text x="{x+w/2}" y="{y+26}" font-size="{fs}" font-weight="700" fill="#0f172a" text-anchor="middle">{t}</text>'
    for i,l in enumerate(lines):
        o+=f'<text x="{x+w/2}" y="{y+48+i*18}" font-size="12.5" fill="#334155" text-anchor="middle">{l}</text>'
    return o
def arr(x1,y1,x2,y2,lab='',dash=False,both=False,col='#334155',dy=-8):
    d=' stroke-dasharray="8 6"' if dash else ''
    ms=' marker-start="url(#b)"' if both else ''
    o=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="2.5"{d} marker-end="url(#a)"{ms}/>'
    if lab:
        tw=len(lab)*7.6+10; cx=(x1+x2)/2; cy=(y1+y2)/2+dy
        o+=f'<rect x="{cx-tw/2}" y="{cy-13}" width="{tw}" height="18" fill="#fff"/><text x="{cx}" y="{cy}" font-size="12" font-weight="700" fill="#0f172a" text-anchor="middle">{lab}</text>'
    return o
def zone(x,y,w,h,t,col='#94a3b8'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="6 5"/><text x="{x+14}" y="{y+22}" font-size="13" font-weight="700" fill="#475569">{t}</text>'

# A) esquema general
b=''
b+=zone(20,95,470,560,'EXTERIOR · zona del depósito')
b+=zone(520,95,330,560,'AZOTEA · mástil')
b+=zone(880,95,500,560,'INTERIOR · aula / red del centro')
b+=box(40,130,200,120,'Sondas en el depósito',['Oxígeno + temp. SEN0681','pH SEN0169-V2','Nivel KIT0139','Presencia agua SEN0204'],'#e0f2fe','#0369a1')
b+=box(40,280,200,70,'Bidón de 25 L',['sondas colgadas del tapón'],'#e0f2fe','#0369a1')
b+=box(40,380,200,70,'Bomba de recirculación',['fuera del bidón','sin conexión al nodo'],'#f5f5f4','#78716c')
b+=box(280,190,190,120,'Nodo LILYGO',['T3 V1.6.1','ESP32 + SX1276','LoRaWAN 1.1 · OTAA','un envío cada 15 min'],'#1e293b0d','#0f172a')
b+=arr(240,190,280,225)
b+=box(40,500,430,130,'Alimentación del nodo',['Placas solares + batería → inversor → 230 V','Fuente de 12 V (de PC, adaptada) → sensores','Cargador USB 5 V con batería de respaldo → LILYGO'],'#fff7ed','#c2410c')
b+=arr(375,500,375,312,'12 V / 5 V',dy=4)
b+=box(560,190,250,120,'Gateway MikroTik wAP LR8',['8 canales EU868','IP 172.16.50.2','PoE por el cable de red','reenvío UDP 1700'],'#ecfdf5','#047857')
b+=arr(470,250,560,250,'LoRaWAN 868 MHz',dash=True,dy=-12)
b+=box(900,130,210,80,'Inyector PoE + fuente 24 V',['baja por la bajante (Cat6)'],'#f1f5f9')
b+=box(900,260,210,90,'Switch del instituto',['VLAN 500 · 172.16.50.0/24','puerta de enlace 172.16.50.1'],'#f1f5f9')
b+=arr(810,225,900,175,'Cat6 exterior',dy=4)
b+=arr(1005,210,1005,260)
b+=box(1150,240,215,130,'Raspberry Pi 5',['IP 172.16.50.3','ChirpStack · Mosquitto','TimescaleDB · ingestor','web · Caddy · Tailscale'],'#fdf2f8','#be185d')
b+=arr(1110,305,1150,305,both=True)
b+=box(900,430,210,80,'Router del centro',['salida a Internet (NAT)','sin puertos abiertos'],'#f1f5f9')
b+=arr(1005,350,1005,430)
b+=box(900,560,210,75,'Tailscale Funnel',['HTTPS público'],'#eef2ff','#4338ca')
b+=arr(1005,510,1005,560,'conexión de salida',dy=4)
b+=box(1150,545,215,95,'Usuarios',['móvil o PC, desde cualquier sitio','rpi-lora.tailc40e5c.ts.net'],'#eef2ff','#4338ca')
b+=arr(1150,597,1110,597)
open('plano-general.svg','w',encoding='utf8').write(svg(1400,680,b,'Esquema general del sistema','Monitorización de la calidad del agua · CPIFP Los Viveros (Sevilla) · sin escala'))

# B) red
b=''
b+=box(560,100,280,80,'Internet',['servidores de Tailscale (Funnel y VPN)'],'#eef2ff','#4338ca')
b+=box(560,240,280,90,'Router del instituto',['VLAN 500 · puerta de enlace 172.16.50.1','NAT de salida · no se abren puertos'],'#f1f5f9')
b+=arr(700,240,700,180,both=True)
b+=box(480,400,440,80,'Switch del instituto · VLAN 500 (172.16.50.0/24)',['tomas en modo acceso (sin etiquetar)'],'#f1f5f9')
b+=arr(700,330,700,400,both=True)
b+=box(80,560,330,150,'MikroTik wAP LR8 (gateway LoRaWAN)',['IP fija 172.16.50.2/24 en bridgeLocal','gateway-id 04F41CFFFFC15CEB','RouterOS 7.20.7 · PoE pasivo 24 V','servidor LoRa → 172.16.50.3 UDP 1700','hora (NTP) → 172.16.50.3'],'#ecfdf5','#047857')
b+=box(535,560,330,150,'Raspberry Pi 5 (servidor)',['IP fija 172.16.50.3/24 en eth0','DNS 1.1.1.1 y 192.168.2.1','ufw: SSH solo desde la VLAN 500','chrony: servidor NTP para el wAP','tailscale0 100.x.y.z'],'#fdf2f8','#be185d')
b+=box(990,560,330,150,'PC de trabajo (puesta en marcha)',['cable a la VLAN 500 con métrica 500','WinBox → wAP LR8','SSH → Raspberry','PlatformIO → LILYGO por USB'],'#fefce8','#a16207')
b+=arr(560,480,300,560,'inyector PoE',both=True)
b+=arr(700,480,700,560,both=True)
b+=arr(840,480,1100,560,both=True)
b+=arr(410,620,535,620,'UDP 1700 · NTP 123',dy=-10)
b+=box(990,100,330,120,'Accesos desde fuera',['Web: https://rpi-lora.tailc40e5c.ts.net (pública)','ChirpStack: mismo nombre, puerto 8443','(solo equipos del tailnet)','SSH: ssh charlie@rpi-lora (solo tailnet)'],'#eef2ff','#4338ca')
b+=arr(990,150,840,140)
b+=box(80,100,330,120,'Nodo LILYGO (exterior)',['LoRaWAN EU868 · OTAA · clase A','no tiene IP: solo radio','uplink cada 15 min, fPort 1, 16 bytes'],'#e0f2fe','#0369a1')
b+=arr(245,220,245,560,'radio 868 MHz',dash=True,dy=4)
open('plano-red.svg','w',encoding='utf8').write(svg(1400,740,b,'Plano de red','VLAN 500 del instituto, direcciones IP y accesos'))

# C) flujo de datos
b=''
b+=box(30,150,150,90,'Nodo LILYGO',['payload v2','16 bytes'],'#e0f2fe','#0369a1')
b+=box(230,150,150,90,'wAP LR8',['packet forwarder','UDP 1700'],'#ecfdf5','#047857')
b+=arr(180,195,230,195,dash=True)
b+=zone(420,95,950,420,'Raspberry Pi 5 · Docker Compose (raspberry/docker-compose.yml)','#be185d')
b+=box(445,150,165,90,'Gateway Bridge',['chirpstack-','gateway-bridge:4'],'#fdf2f8','#be185d')
b+=arr(380,195,445,195)
b+=box(660,150,165,90,'Mosquitto',['eclipse-mosquitto:2','MQTT QoS 1'],'#fdf2f8','#be185d')
b+=arr(610,195,660,195,both=True)
b+=box(875,150,200,90,'ChirpStack v4',['región eu868','codec decoder.js'],'#fdf2f8','#be185d')
b+=arr(825,195,875,195,both=True)
b+=box(1125,150,220,90,'Redis + PostgreSQL',['estado de ChirpStack','(redis:7 · BD chirpstack)'],'#f1f5f9')
b+=arr(1075,195,1125,195,both=True)
b+=box(660,300,165,90,'Ingestor',['Python','MQTT → BD'],'#fdf2f8','#be185d')
b+=arr(742,240,742,300,'uplink decodificado',dy=4)
b+=box(875,300,200,90,'TimescaleDB',['BD agua: medidas,','nodos, uplinks_raw (UTC)'],'#fdf2f8','#be185d')
b+=arr(825,345,875,345)
b+=box(1125,300,220,90,'Web (FastAPI + ECharts)',['tiempo real: NOTIFY + SSE','histórico y CSV'],'#fdf2f8','#be185d')
b+=arr(1075,345,1125,345)
b+=box(1125,410,220,80,'Caddy',['proxy en el puerto 80'],'#fdf2f8','#be185d')
b+=arr(1235,390,1235,410)
b+=box(875,410,200,80,'backup.sh (cron 03:00)',['copia diaria de las 2 BD'],'#f1f5f9')
b+=arr(975,390,975,410)
b+=box(1125,560,220,80,'Tailscale Funnel',['HTTPS · certificado automático'],'#eef2ff','#4338ca')
b+=arr(1235,490,1235,560)
b+=box(820,560,240,80,'Navegador (móvil o PC)',['https://rpi-lora.tailc40e5c.ts.net'],'#eef2ff','#4338ca')
b+=arr(1125,600,1060,600)
b+=box(445,560,300,80,'Dentro del instituto',['http://172.16.50.3 (VLAN 500)'],'#f1f5f9')
open('plano-datos.svg','w',encoding='utf8').write(svg(1400,670,b,'Flujo de datos y servicios del servidor','Del sensor a la web: cada mensaje queda guardado con fecha y hora'))
