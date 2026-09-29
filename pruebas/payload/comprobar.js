// Pasa los payloads generados por el firmware por el decodificador de ChirpStack
// (raspberry/codec/decoder.js) y comprueba los valores y que el ingestor encuentra sus campos.
const fs = require("fs");
const path = require("path");
const raiz = path.join(__dirname, "..", "..");

// Cargar decoder.js igual que lo usa ChirpStack (funciones globales)
const codigo = fs.readFileSync(path.join(raiz, "raspberry/codec/decoder.js"), "utf8");
const { decodeUplink, encodeDownlink } = new Function(codigo + "; return { decodeUplink, encodeDownlink };")();

// Valores esperados para cada caso de generar.cpp
const esperado = {
  normal: { temperatura_c: 21.37, oxigeno_mgl: 8.42, ph: 7.61, conductividad_uscm: null, nivel_mm: 412,
            bateria_v: 13.21, caudal_lmin: 3.85, agua_presente: true, bateria_baja: false,
            fallo_rs485: false, bomba_sin_caudal: false },
  frio_bateria_baja: { temperatura_c: -2.5, bateria_v: 12.1, bateria_baja: true, conductividad_uscm: null },
  sin_datos: { temperatura_c: null, oxigeno_mgl: null, ph: null, nivel_mm: null, bateria_v: null,
               caudal_lmin: null, conductividad_uscm: null, agua_presente: false, fallo_rs485: true,
               fallo_ads: true, temp_por_defecto: true, bomba_sin_caudal: true, bateria_baja: false },
};

// Campos que lee el ingestor (obj.get("...") en raspberry/ingestor/ingestor.py)
const ingestor = fs.readFileSync(path.join(raiz, "raspberry/ingestor/ingestor.py"), "utf8");
const camposIngestor = [...ingestor.matchAll(/obj\.get\("(\w+)"\)/g)].map(m => m[1]);

let errores = 0;
const fallo = (msg) => { console.log("  FALLO: " + msg); errores++; };

const lineas = fs.readFileSync(0, "utf8").trim().split("\n");
for (const linea of lineas) {
  const [nombre, hex] = linea.split(";");
  const bytes = Array.from(Buffer.from(hex, "hex"));
  const r = decodeUplink({ bytes, fPort: 1 });
  console.log(`${nombre}: ${hex}`);
  if (r.errors) { fallo(r.errors.join(", ")); continue; }
  for (const [campo, valor] of Object.entries(esperado[nombre])) {
    const real = r.data[campo];
    const ok = valor === null || typeof valor === "boolean" ? real === valor : Math.abs(real - valor) < 0.006;
    if (!ok) fallo(`${campo} = ${real}, se esperaba ${valor}`);
  }
  for (const c of camposIngestor) if (!(c in r.data)) fallo(`el ingestor lee "${c}" y el decodificador no lo da`);
  console.log("  " + JSON.stringify(r.data));
}

// Downlink de intervalo: lo que genera ChirpStack debe ser lo que espera procesarDownlink() del firmware
const d = encodeDownlink({ data: { intervalo_min: 30 } });
if (d.fPort !== 10 || d.bytes.join(",") !== "1,0,30") fallo("downlink de intervalo: " + JSON.stringify(d));
if (!encodeDownlink({ data: { intervalo_min: 2 } }).errors) fallo("el downlink debería rechazar 2 min");

console.log(errores ? `\n${errores} fallos` : `\nTODO OK (${lineas.length} payloads, ${camposIngestor.length} campos del ingestor comprobados)`);
process.exit(errores ? 1 : 0);
