// Codec ChirpStack v4 — nodo de calidad del agua (payload v1 = 14 bytes, v2 = 16 bytes con caudal)
// Ver docs/04-formato-payload.md

function u16(b, i) { return (b[i] << 8) | b[i + 1]; }
function i16(b, i) { var v = u16(b, i); return (v & 0x8000) ? v - 0x10000 : v; }
function sinDato(v, marca, escala) { return v === marca ? null : v / escala; }

function decodeUplink(input) {
  var b = input.bytes;
  if (input.fPort !== 1) { return { errors: ["fPort no esperado: " + input.fPort] }; }
  var version = b[0];
  var largo = { 1: 14, 2: 16 }[version];
  if (!largo) { return { errors: ["version de payload desconocida: " + version] }; }
  if (b.length < largo) { return { errors: ["longitud incorrecta: " + b.length] }; }

  var flags = b[1];
  var datos = {
    version: version,
    flags: flags,
    agua_presente: (flags & 0x01) !== 0,
    fallo_rs485: (flags & 0x02) !== 0,
    fallo_ads: (flags & 0x04) !== 0,
    bateria_baja: (flags & 0x08) !== 0,
    temp_por_defecto: (flags & 0x10) !== 0,
    bomba_sin_caudal: (flags & 0x20) !== 0,
    temperatura_c: sinDato(i16(b, 2), 0x7FFF, 100),
    oxigeno_mgl: sinDato(u16(b, 4), 0xFFFF, 100),
    ph: sinDato(u16(b, 6), 0xFFFF, 100),
    conductividad_uscm: sinDato(u16(b, 8), 0xFFFF, 1),
    nivel_mm: sinDato(u16(b, 10), 0xFFFF, 1),
    bateria_v: sinDato(u16(b, 12), 0xFFFF, 1000),
    caudal_lmin: version >= 2 ? sinDato(u16(b, 14), 0xFFFF, 100) : null
  };
  return { data: datos };
}

// Downlink: { "intervalo_min": 30 } → fPort 10
function encodeDownlink(input) {
  var m = input.data.intervalo_min;
  if (typeof m !== "number" || m < 5 || m > 120) { return { errors: ["intervalo_min fuera de rango (5-120)"] }; }
  return { bytes: [0x01, (m >> 8) & 0xFF, m & 0xFF], fPort: 10 };
}
