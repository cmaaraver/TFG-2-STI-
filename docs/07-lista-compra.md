# Lista de compra con enlaces

Solo lo que hay que comprar (el material que ya tenemos está en `01-lista-material.md`, apartado A).
Enlaces comprobados el 29 y 30/09/2026: todos abrían la ficha del producto con stock, salvo los marcados **SIN VERIFICAR**.
La misma lista en hoja de cálculo, para pasarla al centro: [`07-lista-compra.xlsx`](07-lista-compra.xlsx).
Todos los precios en euros, con IVA, de tiendas que venden y envían en España. Pueden cambiar.

No hace falta comprar: el convertidor 4-20 mA (viene con el KIT0139), el switch (con solo el wAP no hace falta),
el PC de datos (todo va en la Raspberry), el DC-DC para el DFR1120 (admite 12-24 V según la wiki de DFRobot)
ni SSD para la Raspberry (se queda con la microSD de 64 GB).

## 1. Electrónica del nodo

| Cant. | Artículo | Tienda | Precio ud. | Subtotal | Notas |
|---|---|---|---|---|---|
| 1 | [ADC 16 bits I2C ADS1115 Adafruit (STEMMA QT)](https://www.electronicaembajadores.com/es/Productos/Detalle/LCINDD7/) | Electrónica Embajadores | 21,63 € | 21,63 € | Mismo chip y dirección 0x48 (ADDR a GND); se conecta por pines a la placa base |
| 1 | [Aislador de señal analógica Gravity DFRobot (DFR0504)](https://opencircuit.es/producto/gravity-analog-signal-isolator) | Opencircuit | 29,50 € | 29,50 € | Trae 2 cables PH2.0. Tienda en español con precios en euros; envío a España desde 12,50 € (gratis desde 150 €) |
| 1 | [Adaptador RS485-UART aislado Gravity (DFR0845)](https://www.electronicaembajadores.com/es/Productos/Detalle/LCHR006/) | Electrónica Embajadores | 36,14 € | 36,14 € |  |
| 1 | [Convertidor DC-DC 12 V a 5 V 2,5 A Pololu D24V25F5 (reposo < 1 mA)](https://www.electan.com/pololu-25a-stepdown-voltage-regulator-d24v25f5-p-6473.html) | Electan | 29,26 € | 29,26 € |  |
| 1 | [MOSFET P IRF4905 (conmutador 12 V)](https://www.electronicaembajadores.com/es/Productos/Detalle/SMTRIRF4905/) | Electrónica Embajadores | 1,28 € | 1,28 € | Sustituye al IRF9540N, que está sin stock |
| 1 | [MOSFET P AO3401 SOT-23 (conmutador 5 V)](https://www.amazon.es/s?k=AO3401+SOT-23) | Amazon.es (búsqueda) | — | — | SIN VERIFICAR: Amazon no deja comprobarlo. Suele venir en lotes |
| 1 | [Adaptador SOT-23 a DIP para el AO3401](https://www.electronicaembajadores.com/es/Productos/Detalle/CN15006/) | Electrónica Embajadores | 0,61 € | 0,61 € |  |
| 2 | [Transistor NPN BC547C](https://www.electronicaembajadores.com/es/Productos/Detalle/SMTRBC547C/) | Electrónica Embajadores | 0,29 € | 0,58 € |  |
| 1 | [MOSFET N nivel lógico IRLZ44N (bomba)](https://www.turibot.es/mosfet-irlz44n-49a-55v-5uds) | Turibot | 0,84 € | 0,84 € | Confirmar si el precio es por unidad o por lote |
| 1 | [Diodo Schottky 1N5819](https://www.electronicaembajadores.com/es/Productos/Detalle/SMDI1N5819/) | Electrónica Embajadores | 0,28 € | 0,28 € |  |
| 1 | [Kit 600 resistencias 1 % (30 valores: 220, 1k, 10k, 20k, 100k...)](https://leantec.es/tienda/lote-kit-600-resistencias-1-4w-1-30-valores/) | Leantec | 4,27 € | 4,27 € |  |
| 2 | [Resistencia 22 kΩ 1 %](https://leantec.es/tienda/resistencia-22-kohm-1-4w-0-25w-pelicula-metalica-1/) | Leantec | 0,03 € | 0,06 € | Divisor de la batería |
| 1 | [Placa de topos doble cara 9×15 cm](https://www.tiendatec.es/electronica/placas-de-prototipo/placas/891-placa-pcb-prototipos-doble-cara-9x15cm-8472496014496.html) | Tiendatec | 1,85 € | 1,85 € |  |
| 2 | [Tira de pines hembra 2,54 mm 40 pines](https://www.electronicaembajadores.com/es/Productos/Detalle/CTO1HR40/) | Electrónica Embajadores | 1,71 € | 3,42 € |  |
| 2 | [Tira de pines macho 2,54 mm 40 pines](https://www.electronicaembajadores.com/es/Productos/Detalle/CTO1MR40/) | Electrónica Embajadores | 0,50 € | 1,00 € |  |
| 6 | [Borna de tornillo PCB 5,08 mm 2 vías](https://www.electronicaembajadores.com/es/Productos/Detalle/CTNA5102/) | Electrónica Embajadores | 0,30 € | 1,80 € |  |
| 4 | [Borna de tornillo PCB 5,08 mm 3 vías](https://www.electronicaembajadores.com/es/Productos/Detalle/CTNA5103/) | Electrónica Embajadores | 0,43 € | 1,72 € |  |
| 1 | [Cables Gravity PH2.0 3 pines a Dupont hembra, 50 cm (10 uds) FIT0769](https://opencircuit.es/producto/gravity-analog-sensor-cable-arduino-50cm-10) | Opencircuit | 4,60 € | 4,60 € | Placa de pH y aislador a los pines de la placa base. Mismo pedido que el aislador |
| 1 | [Kit antena LoRaWAN 868 MHz exterior + cable IPEX-SMA](https://www.tiendatec.es/maker-zone/comunicaciones-redes/2762-seeed-kit-antena-lorawan-para-wm1302.html) | Tiendatec | 6,95 € | 6,95 € |  |
| 1 | [Pigtail u.FL a SMA hembra de pasamuros 15 cm](https://www.electronicaembajadores.com/es/Productos/Detalle/CXRF001/) | Electrónica Embajadores | 5,15 € | 5,15 € | Para sacar la antena por la pared de la caja |
| 1 | [Cable USB-A a USB-C de datos 1 m](https://www.electronicaembajadores.com/es/Productos/Detalle/CX313101/) | Electrónica Embajadores | 5,83 € | 5,83 € | Si la LILYGO es micro-USB, cambiarlo |

Subtotal: **156,77 €**

## 2. Cajas, conectores y cableado exterior

| Cant. | Artículo | Tienda | Precio ud. | Subtotal | Notas |
|---|---|---|---|---|---|
| 1 | [Caja estanca IP66 255×250×120 mm (electrónica)](https://www.electronicaembajadores.com/es/Productos/Detalle/CJ41G712/) | Electrónica Embajadores | 56,55 € | 56,55 € |  |
| 1 | [Caja estanca ABS 320×270×121 mm IP65 (batería y MPPT)](https://www.electronicaembajadores.com/es/Productos/Detalle/CJ41D09/) | Electrónica Embajadores | 69,03 € | 69,03 € | La batería va tumbada; con el toldo encima, IP65 es suficiente |
| 2 | [Tapón de ventilación M12 con membrana](https://www.amazon.es/s?k=tap%C3%B3n+ventilaci%C3%B3n+M12x1.5+IP68+membrana) | Amazon.es (búsqueda) | — | — | SIN VERIFICAR |
| 1 | [Conector GX16 4 pines: base macho](https://www.electronicaembajadores.com/es/Productos/Detalle/CTEAMB4/) | Electrónica Embajadores | 1,00 € | 1,00 € | Sensor de oxígeno |
| 1 | [Conector GX16 4 pines: aéreo hembra](https://www.electronicaembajadores.com/es/Productos/Detalle/CTEAHA4/) | Electrónica Embajadores | 0,90 € | 0,90 € |  |
| 1 | [Conector GX16 2 pines: base macho](https://www.electronicaembajadores.com/es/Productos/Detalle/CTEAMB2/) | Electrónica Embajadores | 1,40 € | 1,40 € | Bomba |
| 1 | [Conector GX16 2 pines: aéreo hembra](https://www.electronicaembajadores.com/es/Productos/Detalle/CTEAHA2/) | Electrónica Embajadores | 1,23 € | 1,23 € |  |
| 3 | [Conector GX16 3 pines: base macho](https://www.electronicaembajadores.com/es/Productos/Detalle/CTEAMB3/) | Electrónica Embajadores | 0,94 € | 2,82 € | Caudalímetro, presencia de agua y nivel |
| 3 | [Conector GX16 3 pines: aéreo hembra](https://www.electronicaembajadores.com/es/Productos/Detalle/CTEAHA3/) | Electrónica Embajadores | 0,92 € | 2,76 € |  |
| 1 | [Pasamuros BNC hembra-hembra](https://www.electronicaembajadores.com/es/Productos/Detalle/CT2A703/) | Electrónica Embajadores | 2,25 € | 2,25 € | Sonda de pH |
| 3 | [Prensaestopas PG9 IP68](https://www.electronicaembajadores.com/es/Productos/Detalle/CC2APG09N/) | Electrónica Embajadores | 0,84 € | 2,52 € |  |
| 3 | [Prensaestopas PG11 IP68](https://www.electronicaembajadores.com/es/Productos/Detalle/CC2APG11N/) | Electrónica Embajadores | 0,80 € | 2,40 € |  |
| 5 | [Manguera apantallada 4×0,5 mm² (metro)](https://www.electricidad.tienda/cable-apantallado/manguera-apantallada-4x05-mm2-libre-de-halogenos-rc4z1-k-por-metros-7372.html) | electricidad.tienda | 1,36 € | 6,80 € | RS485 + 12 V del sensor de oxígeno |
| 5 | [Manguera 3×1 mm² (metro)](https://www.electronicaembajadores.com/es/Productos/Detalle/CA2A011/) | Electrónica Embajadores | 1,98 € | 9,90 € | Caudalímetro, presencia y nivel |
| 3 | [Manguera RV-K 2×1,5 mm² exterior (metro)](https://www.electronicaembajadores.com/es/Productos/Detalle/CA2A213/) | Electrónica Embajadores | 1,88 € | 5,64 € | Bomba |
| 1 | [Barniz protector tropicalizador Jelt Tropicoat 400 ml](https://www.electronicaembajadores.com/es/Productos/Detalle/HR11060/) | Electrónica Embajadores | 18,85 € | 18,85 € |  |
| 1 | [Gel de sílice, 100 bolsitas de 10 g](https://www.bolaseca.com/es/productos/silica-gel/silica-gel-100-bolsitas-de-10-gramos) | Bolaseca | — | — | Pedir presupuesto (no muestra precio) |
| 1 | [Candado numérico 4 dígitos](https://www.electronicaembajadores.com/es/Productos/Detalle/SG2A101N/) | Electrónica Embajadores | 6,78 € | 6,78 € | Solo si la caja tiene orejetas |

Subtotal: **190,83 €**

## 3. Circuito de agua y soporte de sondas

| Cant. | Artículo | Tienda | Precio ud. | Subtotal | Notas |
|---|---|---|---|---|---|
| 1 | [Bidón HDPE 60 L con tapa, gris opaco](https://ricardoteransl.es/producto/bidon-gris-60-l/) | Ricardo Terán | 29,50 € | 29,50 € | COMPROBAR que la boca es ancha: las sondas se cuelgan de una pletina que cruza la boca |
| 1 | [Bomba sumergible 12 V sin escobillas DC40A-1230 (0,8 A, 500 L/h, 3 m)](https://www.amazon.es/s?k=DC40A-1230) | Amazon.es (búsqueda) | — | — | SIN VERIFICAR. Ficha del fabricante: https://zksj.com/product/3_phase_brushless_DC_Pump_DC40A.html . Comprobar que es la 1230 de 12 V (la 1245 gasta 1,2 A) |
| 1 | [Filtro en Y latón 1/2" H-H, malla inox](https://www.traxco.es/tienda/filtro-laton) | Traxco | 3,60 € | 3,60 € | Elegir 1/2" |
| 1 | [Caudalímetro de efecto Hall YF-S201](https://tienda.bricogeek.com/otros-sensores/936-sensor-de-flujo-yf-s201.html) | BricoGeek | 4,78 € | 4,78 € |  |
| 1 | [Válvula de esfera PVC 1/2" rosca hembra](https://www.fuentejardin.com/valvulas-de-esfera-pvc-rh/388-valvula-de-esfera-pvc-12-rosca-hembra.html) | FuenteJardín (Sevilla) | 7,44 € | 7,44 € |  |
| 3 | [Manguera cristal reforzada 12×18 mm (metro)](https://www.suministrosurquiza.com/metro-manguera-cristal-reforzada) | Suministros Urquiza | 1,39 € | 4,17 € | Elegir 12×18 |
| 3 | [Entronque manguera macho latón 14 mm × 1/2"](https://www.fuentejardin.com/entronque-manguera-macho-laton/2263-entronque-manguera-macho-laton-14mmx12.html) | FuenteJardín (Sevilla) | 4,46 € | 13,38 € |  |
| 1 | [Racor manguera hembra latón 14 mm × 1/2"](https://www.fuentejardin.com/racor-2-piezas-manguera-hembra/2269-racor-2-piezas-manguera-h-laton-14mmx12.html) | FuenteJardín (Sevilla) | 2,88 € | 2,88 € |  |
| 10 | [Abrazadera sinfín inox W4 12-22 mm](https://agrogomasonline.com/sin-fin-inox/8279-abrazaderas-sinfin-inox-w4-12-22-l.html) | Agrogomas | 1,45 € | 14,50 € |  |
| 1 | [Cinta de teflón 12 m](https://www.fuentejardin.com/cinta-de-sellado/383-cinta-de-sellado-12-mm-x-12-m-x-01-mm.html) | FuenteJardín (Sevilla) | 0,63 € | 0,63 € |  |
| 1 | [Pletina de aluminio 40×3 mm, barra 2,5 m](https://www.esteba.com/es/perfil-pletina-plana-aluminio) | Esteba | 29,27 € | 29,27 € | Soporte de las sondas; elegir 40×3 |
| 1 | [Prensaestopas PG16 IP68 (sonda de pH)](https://www.electronicaembajadores.com/es/Productos/Detalle/CC2APG16/) | Electrónica Embajadores | 1,00 € | 1,00 € |  |
| 3 | [Prensaestopas PG21 IP68 (sonda de oxígeno y tapa del depósito)](https://www.electronicaembajadores.com/es/Productos/Detalle/CC2APG21/) | Electrónica Embajadores | 1,80 € | 5,40 € | Medir la sonda de oxígeno antes |
| 1 | [Prensaestopas PG13,5 IP68 (cable del sensor de nivel)](https://www.electronicaembajadores.com/es/Productos/Detalle/CC2APG13/) | Electrónica Embajadores | 0,89 € | 0,89 € |  |
| 8 | [Tornillo hexagonal DIN 933 inox A2 M6×30](https://entaban.es/hexagonales/138-tornillo-hexagonal-din-933-inoxidable-a2.html) | Entaban | 0,10 € | 0,80 € | Precio orientativo según medida |
| 8 | [Tuerca autoblocante DIN 985 inox A2 M6](https://entaban.es/autoblocantes/164-tuerca-autoblocante-din-985-inoxidable-a2.html) | Entaban | 0,07 € | 0,56 € |  |
| 1 | [Toldo vela HDPE 3,6×3,6 m](https://terralba.es/toldos-y-sombra/5454-toldo-vela-sombra-36x36-beige-8435450468308.html) | Terralba | 49,90 € | 49,90 € |  |

Subtotal: **168,70 €**

## 4. Energía autónoma (panel + batería)

| Cant. | Artículo | Tienda | Precio ud. | Subtotal | Notas |
|---|---|---|---|---|---|
| 1 | [Panel solar Victron 50 W 12 V monocristalino](https://solarmat.es/es/paneles-solares-12v/panel-solar-monocristalino-12v-50w-victron.html) | Solarmat | 89,44 € | 89,44 € |  |
| 1 | [Estructura regulable 30-60° para panel](https://www.damiasolar.com/estructura-para-panel-solar-regulable-30-a-60-grados.html) | Damia Solar | 55,00 € | 55,00 € |  |
| 1 | [Batería LiFePO4 12,8 V 20 Ah con BMS FirstPower FPLI1220AH](https://www.andupil.com/es/baterias-para-alumbrado-de-emergencia-y-senalizacion/19144-bateria-de-litio-128v-20ah-256wh-lifepo4-firstpower-fpli1220ah.html) | Andupil | 134,16 € | 134,16 € | Alternativa más barata: INNPO 20 Ah, 75 €: https://bateriasonline.com/es/baterias-litio-recargable/bateria-lifepo4-12v-20ah-innpo-baterias-litio-recargable.html |
| 1 | [Regulador Victron SmartSolar MPPT 75/10 (con salida de carga)](https://www.damiasolar.com/regulador-victron-mppt-smartsolar-75-10.html) | Damia Solar | 73,38 € | 73,38 € | Autoconsumo 20 mA; corte por baja tensión configurable |
| 2 | [Portafusibles aéreo de láminas con tapa](https://www.electronicaembajadores.com/es/Productos/Detalle/FU5A011/) | Electrónica Embajadores | 1,53 € | 3,06 € | Dentro de la caja |
| 4 | [Fusible de láminas 5 A](https://www.electronicaembajadores.com/es/Productos/Detalle/FUAUM502/) | Electrónica Embajadores | 0,20 € | 0,80 € | 2 de repuesto |
| 4 | [Fusible de láminas 3 A](https://www.electronicaembajadores.com/es/Productos/Detalle/FUAUM302/) | Electrónica Embajadores | 0,35 € | 1,40 € | 2 de repuesto |
| 1 | [Desconectador de baterías rotativo IP66](https://cuencasolar.es/producto/desconectador-de-baterias-300a/) | CuencaSolar | 57,86 € | 57,86 € | Sobredimensionado; un interruptor de 12 V más pequeño también vale. La tienda bloquea las comprobaciones automáticas: abrir el enlace a mano |
| 10 | [Cable solar 4 mm² (metro)](https://solarmat.es/es/Cable-solar/metro-cable-solar-4mm2.html) | Solarmat | 2,21 € | 22,10 € | Negro: marcar el positivo con cinta roja |
| 1 | [Par de conectores MC4](https://solarmat.es/es/Conector-solar/par-de-conectores-solares-macho-y-hembra.html) | Solarmat | 7,02 € | 7,02 € |  |
| 2 | [Cable 2,5 mm² rojo (metro)](https://www.electronicaembajadores.com/en/Productos/Detalle/CA5A2PV22/) | Electrónica Embajadores | 3,16 € | 6,32 € | Confirmar si se vende por metro |
| 2 | [Cable 2,5 mm² negro (metro)](https://www.electronicaembajadores.com/en/Productos/Detalle/CA5A2PV21/) | Electrónica Embajadores | 3,16 € | 6,32 € |  |
| 1 | [Terminales de ojal 2,5 mm² M6 (25 uds)](https://www.electronicaembajadores.com/en/Productos/Detalle/CTV1R27-25/) | Electrónica Embajadores | 3,99 € | 3,99 € |  |
| 1 | [Punteras 2,5 mm² (100 uds)](https://www.electronicaembajadores.com/en/Productos/Detalle/CTV1010/) | Electrónica Embajadores | 2,39 € | 2,39 € |  |
| 1 | [Bridas negras 4,8×188 mm (100 uds)](https://todoelectrico.es/es/bridas-100-ud-negra-4-8x188mm-u2244-0.html) | Todoeléctrico | 6,21 € | 6,21 € |  |
| 1 | [Pica de tierra 1,5 m cobreada](https://bricoelige.com/pica-acero-cobre-100-micras-15-metros) | Bricoelige | 14,69 € | 14,69 € | Solo si no hay toma de tierra cerca |
| 1 | [Grapa para pica de tierra](https://bricoelige.com/grapa-toma-tierra-tgt142-sofamel) | Bricoelige | 3,44 € | 3,44 € |  |
| 3 | [Cable 6 mm² para tierra (metro)](https://solarmat.es/es/Cable-solar/metro-cable-solar-6mm2.html) | Solarmat | 3,12 € | 9,36 € | Marcar con cinta verde-amarilla |
| 1 | [Terminales de ojal 6 mm² (25 uds)](https://www.electronicaembajadores.com/es/Productos/Detalle/CTV1R45-25/) | Electrónica Embajadores | 5,90 € | 5,90 € |  |

Subtotal: **502,84 €**

## 5. Raspberry Pi 5 y red

| Cant. | Artículo | Tienda | Precio ud. | Subtotal | Notas |
|---|---|---|---|---|---|
| 1 | [Batería RTC oficial Raspberry Pi 5](https://www.kubii.com/es/baterias-pilas/4110-bateria-rtc-para-raspberry-pi-5-5056561803739.html) | Kubii | 6,00 € | 6,00 € |  |
| 1 | [Fuente oficial Raspberry Pi 27 W USB-C](https://www.kubii.com/es/fuentes-de-alimentacion/4107-1890-fuente-de-alimentacion-raspberry-pi-27w-usb-c-3272496315761.html) | Kubii | 12,90 € | 12,90 € |  |
| 1 | [Active Cooler oficial Raspberry Pi 5](https://www.kubii.com/es/ventiladores-disipadores-de-calor/4109-ventilador-disipador-para-raspberry-pi-5-5056561803357.html) | Kubii | 6,00 € | 6,00 € |  |
| 1 | [Adaptador USB 3.0 a Ethernet Gigabit](https://www.tiendatec.es/maker-zone/comunicaciones-redes/2057-adaptador-usb-3-0-a-ethernet-gigabit-8436574700480.html) | Tiendatec | 12,95 € | 12,95 € | Pedir el de chip RTL8153 |
| 2 | [Latiguillo UTP Cat6 1 m](https://www.electronicaembajadores.com/es/Productos/Detalle/CX3A601/) | Electrónica Embajadores | 1,38 € | 2,76 € | Raspberry-inyector PoE y red del instituto |
| 1 | [SAI Salicru SPS 500 ONE v2 (opcional)](https://www.discoazul.com/sai-linea-interactiva-salicru-sps-500-one-v2-500va-240w-2-schuko.html) | Discoazul | 63,99 € | 63,99 € | Opcional |

Subtotal: **104,60 €**

## 6. Calibración y medida

| Cant. | Artículo | Tienda | Precio ud. | Subtotal | Notas |
|---|---|---|---|---|---|
| 1 | [Solución tampón pH 4,01 Hanna 230 ml](https://www.hannainst.es/parametros/5096-solucion-tampon-ph-401.html) | Hanna Instruments | 12,10 € | 12,10 € |  |
| 1 | [Solución tampón pH 7,01 Hanna 230 ml](https://www.hannainst.es/parametros/5099-solucion-tampon-ph-701.html) | Hanna Instruments | 12,10 € | 12,10 € |  |
| 1 | [Solución tampón pH 10,01 Hanna 230 ml](https://www.hannainst.es/parametros/5095-solucion-tampon-ph-1001.html) | Hanna Instruments | 12,10 € | 12,10 € |  |
| 1 | [Solución de almacenamiento de electrodos Hanna 230 ml](https://www.hannainst.es/parametros/4974-solucion-almacenamiento-electrodos.html) | Hanna Instruments | 21,78 € | 21,78 € |  |
| 3 | [Vaso de precipitado 100 ml borosilicato](https://www.daselab.es/vasos-de-vidrio/198-vaso-precipitado-forma-baja-100-ml.html) | Daselab | 1,45 € | 4,35 € |  |
| 1 | [Escobillón nº 40 (limpiar sondas)](https://www.daselab.es/labware/3156-escobillon-n-40-ptubos-medianos.html) | Daselab | 1,40 € | 1,40 € |  |
| 1 | [Vatímetro DC jOY-it COM-VAO10020](https://www.electronicaembajadores.com/es/Productos/Detalle/IPDDAM5/) | Electrónica Embajadores | 14,90 € | 14,90 € | Medir consumos en la fase 6 |
| 1 | Agua destilada (garrafa 5 L) | Supermercado o ferretería | — | — | Compra local, unos 2 € |

Subtotal: **78,73 €**

## Total

| Bloque | €, IVA incl. |
|---|---|
| 1. Electrónica del nodo | 156,77 |
| 2. Cajas, conectores y cableado exterior | 190,83 |
| 3. Circuito de agua y soporte de sondas | 168,70 |
| 4. Energía autónoma (panel + batería) | 502,84 |
| 5. Raspberry Pi 5 y red | 104,60 |
| 6. Calibración y medida | 78,73 |
| **Total** | **1.202,47 €** |

Sin contar 5 artículos sin precio (bomba, AO3401, tapones de ventilación, gel de sílice, agua destilada; unos 40 € más)
ni los portes de cada tienda. El SAI (64 €) es opcional.

## Tiendas principales
- **Electrónica Embajadores** (Madrid): casi toda la electrónica, cajas, conectores y cables en un pedido. Pedido mínimo 10 € sin IVA.
- **FuenteJardín** (Bollullos de la Mitación, Sevilla, tel. 955 692 234): fontanería.
- **Kubii**: Raspberry Pi. **Solarmat** y **Damia Solar**: panel, regulador y cable solar.
- **Opencircuit** (tienda en español, precios en euros): aislador y cables Gravity de DFRobot.
