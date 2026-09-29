// Página de la maqueta: tarjetas en tiempo real + gráficas del histórico (ECharts)
"use strict";

// Qué se enseña y cómo. "bien"/"aviso" son rangos orientativos para agua de red; ajustarlos
// cuando tengamos datos reales de la maqueta.
const VARIABLES = [
  { id: "temperatura_c", nombre: "Temperatura", unidad: "°C", dec: 1, color: "#f97316",
    estado: v => v > 35 ? "mal" : v > 30 ? "aviso" : "bien" },
  { id: "oxigeno_mgl", nombre: "Oxígeno disuelto", unidad: "mg/L", dec: 2, color: "#0ea5e9",
    estado: v => v < 4 ? "mal" : v < 6 ? "aviso" : "bien" },
  { id: "ph", nombre: "pH", unidad: "", dec: 2, color: "#a855f7",
    estado: v => (v < 6 || v > 9) ? "mal" : (v < 6.5 || v > 8.5) ? "aviso" : "bien" },
  { id: "nivel_mm", nombre: "Nivel del depósito", unidad: "mm", dec: 0, color: "#14b8a6" },
  { id: "caudal_lmin", nombre: "Caudal de la bomba", unidad: "L/min", dec: 2, color: "#3b82f6",
    estado: v => v < 0.3 ? "mal" : "bien" },
  { id: "bateria_v", nombre: "Batería", unidad: "V", dec: 2, color: "#22c55e",
    estado: v => v < 12.0 ? "mal" : v < 12.6 ? "aviso" : "bien" },
  { id: "rssi_dbm", nombre: "RSSI", unidad: "dBm", dec: 0, color: "#64748b",
    estado: v => v < -120 ? "mal" : v < -110 ? "aviso" : "bien" },
  { id: "snr_db", nombre: "SNR", unidad: "dB", dec: 1, color: "#94a3b8",
    estado: v => v < -15 ? "mal" : v < -7 ? "aviso" : "bien" },
];
const MIN_SIN_DATOS = 35; // envía cada 15 min: más de 2 envíos perdidos = nodo caído
const ZONA = "Europe/Madrid";

const $ = sel => document.querySelector(sel);
const estado = { nodo: null, horas: 24, desde: null, hasta: null, graficas: {}, ultima: null };

const fmtFecha = t => new Date(t).toLocaleString("es-ES", {
  timeZone: ZONA, day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
const fmtNum = (v, dec) => v == null ? "—" : Number(v).toLocaleString("es-ES", {
  minimumFractionDigits: dec, maximumFractionDigits: dec });

function hace(t) {
  const min = Math.round((Date.now() - new Date(t)) / 60000);
  if (min < 1) return "hace menos de 1 min";
  if (min < 60) return `hace ${min} min`;
  const h = Math.floor(min / 60);
  return h < 48 ? `hace ${h} h ${min % 60} min` : `hace ${Math.floor(h / 24)} días`;
}

async function pedir(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

// ---------- Tarjetas "Ahora mismo" ----------
function pintarTarjetas(m, destacar) {
  estado.ultima = m;
  $("#tarjetas").innerHTML = VARIABLES.map(v => {
    const val = m ? m[v.id] : null;
    const clase = val != null && v.estado ? v.estado(val) : "";
    return `<div class="tarjeta ${clase} ${destacar ? "nuevo" : ""}">
      <div class="nombre">${v.nombre}</div>
      <div class="valor">${fmtNum(val, v.dec)}<span class="unidad">${v.unidad}</span></div>
      <div class="detalle">${m ? "SF" + (m.spreading_factor ?? "?") + " · fcnt " + (m.fcnt ?? "?") : ""}</div>
    </div>`;
  }).join("");

  const avisos = [];
  if (m) {
    if (m.agua_presente === false) avisos.push(["mal", "El sensor de presencia no detecta agua: rellenar el depósito."]);
    if (m.bomba_sin_caudal) avisos.push(["mal", "La bomba no da caudal (atasco, sin agua o avería)."]);
    if (m.flags & 0x02) avisos.push(["aviso", "Fallo de lectura del sensor de oxígeno (RS485)."]);
    if (m.flags & 0x04) avisos.push(["aviso", "Fallo del convertidor analógico (ADS1115)."]);
    if (m.flags & 0x08) avisos.push(["aviso", "El nodo avisa de batería baja."]);
  }
  $("#avisos").innerHTML = avisos.map(([c, t]) => `<div class="aviso-linea ${c}">${t}</div>`).join("");
  actualizarRecepcion();
}

function actualizarRecepcion() {
  const m = estado.ultima;
  const p = $("#estado");
  if (!m) { $("#ultima-recepcion").textContent = "Sin datos todavía"; return; }
  const min = (Date.now() - new Date(m.tiempo)) / 60000;
  $("#ultima-recepcion").textContent = `Último mensaje: ${fmtFecha(m.tiempo)} (${hace(m.tiempo)})`;
  if (min > MIN_SIN_DATOS) { p.textContent = "Nodo sin transmitir"; p.className = "pastilla caido"; }
  else if (conectadoTiempoReal) { p.textContent = "En directo"; p.className = "pastilla vivo"; }
}

// ---------- Gráficas ----------
function colorTexto() {
  return getComputedStyle(document.documentElement).getPropertyValue("--tenue").trim();
}
function colorBorde() {
  return getComputedStyle(document.documentElement).getPropertyValue("--borde").trim();
}

function crearGraficas() {
  const cont = $("#graficas");
  cont.innerHTML = "";
  estado.graficas = {};
  for (const v of VARIABLES) {
    const div = document.createElement("div");
    div.className = "grafica";
    cont.appendChild(div);
    const g = echarts.init(div, null, { renderer: "canvas" });
    g.group = "agua"; // zoom y cursor sincronizados entre todas las gráficas
    g.setOption({
      title: { text: `${v.nombre}${v.unidad ? " (" + v.unidad + ")" : ""}`, left: 10, top: 0,
               textStyle: { fontSize: 13, fontWeight: 600, color: colorTexto() } },
      grid: { left: 52, right: 16, top: 34, bottom: 58 },
      tooltip: { trigger: "axis",
        valueFormatter: val => val == null ? "—" : fmtNum(val, v.dec) + (v.unidad ? " " + v.unidad : ""),
        axisPointer: { type: "cross", label: { formatter: p => p.axisDimension === "x" ? fmtFecha(p.value) : fmtNum(p.value, v.dec) } } },
      xAxis: { type: "time", axisLabel: { color: colorTexto(), hideOverlap: true,
               formatter: val => fmtFecha(val) }, axisLine: { lineStyle: { color: colorBorde() } } },
      yAxis: { type: "value", scale: true, axisLabel: { color: colorTexto() },
               splitLine: { lineStyle: { color: colorBorde() } } },
      dataZoom: [{ type: "inside" }, { type: "slider", height: 18, bottom: 8, borderColor: colorBorde(),
                  labelFormatter: val => fmtFecha(val), textStyle: { color: colorTexto(), fontSize: 10 } }],
      toolbox: { right: 8, top: -4, itemSize: 13, feature: {
        dataZoom: { yAxisIndex: "none", title: { zoom: "Zoom", back: "Deshacer zoom" } },
        restore: { title: "Restaurar" }, saveAsImage: { title: "Guardar imagen", name: v.id } } },
      series: [{ type: "line", name: v.nombre, showSymbol: false, smooth: 0.2, connectNulls: false,
                 lineStyle: { width: 2, color: v.color }, itemStyle: { color: v.color },
                 areaStyle: { opacity: 0.08, color: v.color }, data: [] }],
    });
    estado.graficas[v.id] = g;
  }
  echarts.connect("agua");
}

function rango() {
  if (estado.horas > 0) {
    const hasta = new Date();
    return { desde: new Date(hasta - estado.horas * 3600e3), hasta, envivo: true };
  }
  return { desde: estado.desde, hasta: estado.hasta, envivo: false };
}

async function cargarHistorico() {
  if (!estado.nodo) return;
  const r = rango();
  const q = `dev_eui=${encodeURIComponent(estado.nodo)}&desde=${r.desde.toISOString()}&hasta=${r.hasta.toISOString()}`;
  $("#csv").href = `/api/csv?${q}`;
  $("#info-historico").textContent = "Cargando…";
  const h = await pedir(`/api/historico?${q}`);
  const s = h.serie;
  for (const v of VARIABLES) {
    estado.graficas[v.id].setOption({
      xAxis: { min: r.desde.getTime(), max: r.hasta.getTime() },
      series: [{ data: s.tiempo.map((t, i) => [t, s[v.id][i]]) }],
    });
  }
  $("#info-historico").textContent = h.puntos === 0
    ? "No hay medidas en este intervalo."
    : `${h.medidas_totales} medidas` + (h.agrupado_cada_s
        ? ` (se muestran medias cada ${Math.round(h.agrupado_cada_s / 60)} min para que la gráfica vaya fluida)` : "")
      + ". Arrastra o usa la rueda para hacer zoom.";
}

function anadirPuntoEnVivo(m) {
  if (estado.horas <= 0) return; // en rango personalizado no se toca la gráfica
  const r = rango();
  for (const v of VARIABLES) {
    const g = estado.graficas[v.id];
    const datos = g.getOption().series[0].data.filter(p => new Date(p[0]) >= r.desde);
    datos.push([m.tiempo, m[v.id]]);
    g.setOption({ xAxis: { min: r.desde.getTime(), max: r.hasta.getTime() }, series: [{ data: datos }] });
  }
}

// ---------- Tiempo real (Server-Sent Events) ----------
let conectadoTiempoReal = false;
function conectarTiempoReal() {
  const es = new EventSource("/api/eventos");
  es.onopen = () => { conectadoTiempoReal = true; actualizarRecepcion(); };
  es.onerror = () => {
    conectadoTiempoReal = false;
    const p = $("#estado"); p.textContent = "Reconectando…"; p.className = "pastilla caido";
  };
  es.addEventListener("medida", e => {
    const m = JSON.parse(e.data);
    if (!estado.nodo) { // primer mensaje de la historia: se elige ese nodo
      estado.nodo = m.dev_eui;
      $("#nodo").innerHTML = `<option value="${m.dev_eui}">${m.dev_eui}</option>`;
    }
    if (m.dev_eui !== estado.nodo) return;
    pintarTarjetas(m, true);
    anadirPuntoEnVivo(m);
  });
}

// ---------- Controles ----------
function aLocal(d) { // Date → valor para <input type="datetime-local">
  const z = new Date(d - d.getTimezoneOffset() * 60000);
  return z.toISOString().slice(0, 16);
}

function prepararControles() {
  document.querySelectorAll(".rangos button").forEach(b => b.addEventListener("click", () => {
    document.querySelectorAll(".rangos button").forEach(x => x.classList.remove("activo"));
    b.classList.add("activo");
    estado.horas = Number(b.dataset.horas);
    $("#personalizado").hidden = estado.horas !== 0;
    if (estado.horas === 0) {
      const hasta = new Date(), desde = new Date(hasta - 7 * 86400e3);
      $("#desde").value = aLocal(desde); $("#hasta").value = aLocal(hasta);
      estado.desde = desde; estado.hasta = hasta;
    }
    cargarHistorico().catch(mostrarError);
  }));
  $("#aplicar").addEventListener("click", () => {
    estado.desde = new Date($("#desde").value);
    estado.hasta = new Date($("#hasta").value);
    cargarHistorico().catch(mostrarError);
  });
  $("#nodo").addEventListener("change", e => { estado.nodo = e.target.value; cargarNodo().catch(mostrarError); });
  window.addEventListener("resize", () => Object.values(estado.graficas).forEach(g => g.resize()));
  setInterval(actualizarRecepcion, 30000);
}

function mostrarError(e) {
  console.error(e);
  $("#info-historico").textContent = "No se pudieron cargar los datos. ¿Está encendida la base de datos?";
}

async function cargarNodo() {
  try { pintarTarjetas(await pedir(`/api/ultima?dev_eui=${encodeURIComponent(estado.nodo)}`), false); }
  catch { pintarTarjetas(null, false); }
  await cargarHistorico();
}

async function iniciar() {
  crearGraficas();
  prepararControles();
  const nodos = await pedir("/api/nodos");
  if (!nodos.length) {
    pintarTarjetas(null, false);
    $("#info-historico").textContent = "Todavía no ha llegado ningún mensaje del nodo.";
  } else {
    $("#nodo").innerHTML = nodos.map(n =>
      `<option value="${n.dev_eui}">${n.nombre || n.dev_eui}</option>`).join("");
    estado.nodo = nodos[0].dev_eui;
    await cargarNodo();
  }
  conectarTiempoReal();
}

iniciar().catch(mostrarError);
