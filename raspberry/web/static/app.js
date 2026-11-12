// Página de la maqueta: tarjetas en tiempo real + gráficas del histórico (ECharts)
"use strict";

// Qué se enseña y cómo. "bien"/"aviso" son rangos orientativos para agua de red; ajustarlos
// cuando tengamos datos reales de la maqueta. "escala" es el rango de la barrita de cada tarjeta.
const ICONOS = {
  termometro: '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>',
  burbujas: '<circle cx="8" cy="15" r="4"/><circle cx="16" cy="7" r="3"/><circle cx="17.5" cy="17" r="2"/>',
  matraz: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3M7.5 14h9"/>',
  nivel: '<path d="M3 13c2 0 2-2 4.5-2s2.5 2 4.5 2 2.5-2 4.5-2 2.5 2 4.5 2M3 19c2 0 2-2 4.5-2s2.5 2 4.5 2 2.5-2 4.5-2 2.5 2 4.5 2M12 3v5m-2.5-2.5L12 8l2.5-2.5"/>',
  caudal: '<path d="M3 8h11a3 3 0 1 0-3-3M3 16h15a3 3 0 1 1-3 3M3 12h18"/>',
  bateria: '<rect x="2" y="7" width="17" height="10" rx="2"/><path d="M22 11v2M6 10v4M10 10v4"/>',
  senal: '<path d="M4 20v-3M9 20v-7M14 20V9M19 20V4"/>',
  onda: '<path d="M2 12h3l3-7 4 14 3-9 2 2h5"/>',
};
const VARIABLES = [
  { id: "temperatura_c", nombre: "Temperatura", unidad: "°C", dec: 1, color: "#f97316", rangoMin: 4,
    icono: "termometro", escala: [0, 40], estado: v => v > 35 ? "mal" : v > 30 ? "aviso" : "bien" },
  { id: "oxigeno_mgl", nombre: "Oxígeno disuelto", unidad: "mg/L", dec: 2, color: "#0ea5e9", rangoMin: 2,
    icono: "burbujas", escala: [0, 14], estado: v => v < 4 ? "mal" : v < 6 ? "aviso" : "bien" },
  { id: "ph", nombre: "pH", unidad: "", dec: 2, color: "#a855f7", rangoMin: 1,
    icono: "matraz", escala: [0, 14], estado: v => (v < 6 || v > 9) ? "mal" : (v < 6.5 || v > 8.5) ? "aviso" : "bien" },
  { id: "nivel_mm", nombre: "Nivel del depósito", unidad: "mm", dec: 0, color: "#14b8a6", rangoMin: 200,
    icono: "nivel", escala: [0, 1000] },
  { id: "caudal_lmin", nombre: "Caudal de la bomba", unidad: "L/min", dec: 2, color: "#3b82f6", rangoMin: 2,
    icono: "caudal", escala: [0, 10], estado: v => v < 0.3 ? "mal" : "bien" },
  { id: "bateria_v", nombre: "Batería", unidad: "V", dec: 2, color: "#22c55e", rangoMin: 1,
    icono: "bateria", escala: [11, 14.6], estado: v => v < 12.0 ? "mal" : v < 12.6 ? "aviso" : "bien" },
  { id: "rssi_dbm", nombre: "RSSI", unidad: "dBm", dec: 0, color: "#64748b",
    icono: "senal", escala: [-130, -40], estado: v => v < -120 ? "mal" : v < -110 ? "aviso" : "bien" },
  { id: "snr_db", nombre: "SNR", unidad: "dB", dec: 1, color: "#94a3b8",
    icono: "onda", escala: [-20, 15], estado: v => v < -15 ? "mal" : v < -7 ? "aviso" : "bien" },
];
const TEXTO_ESTADO = { bien: "Correcto", aviso: "Vigilar", mal: "Fuera de rango" };
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

const fmtHora = t => new Date(t).toLocaleTimeString("es-ES", { timeZone: ZONA, hour: "2-digit", minute: "2-digit" });
const sinMovimiento = matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---------- Tarjetas "Ahora mismo" ----------
// Las tarjetas se crean una vez y luego solo se cambian sus números (así no se repite la animación de entrada)
function crearTarjetas() {
  $("#tarjetas").innerHTML = VARIABLES.map((v, i) => `
    <article class="tarjeta" id="t-${v.id}" style="--color:${v.color};--i:${i}">
      <div class="cab">
        <span class="icono"><svg viewBox="0 0 24 24" aria-hidden="true">${ICONOS[v.icono]}</svg></span>
        <span class="nombre">${v.nombre}</span>
      </div>
      <div class="valor"><span class="numero">—</span><span class="unidad">${v.unidad}</span></div>
      <div class="barra"><i></i></div>
      <div class="pie-tarjeta"><span class="etq-estado">—</span><span class="extra"></span></div>
    </article>`).join("");
}

// Cuenta animada del valor anterior al nuevo (efecto contador)
function animarNumero(el, desde, hasta, dec) {
  if (sinMovimiento || desde == null || hasta == null || desde === hasta) {
    el.textContent = fmtNum(hasta, dec); return;
  }
  const t0 = performance.now(), dur = 900;
  const paso = ahora => {
    const p = Math.min(1, (ahora - t0) / dur), suave = 1 - Math.pow(1 - p, 3);
    el.textContent = fmtNum(desde + (hasta - desde) * suave, dec);
    if (p < 1) requestAnimationFrame(paso);
  };
  requestAnimationFrame(paso);
}

function pintarTarjetas(m, destacar) {
  const anterior = estado.ultima;
  estado.ultima = m;
  for (const v of VARIABLES) {
    const t = document.getElementById("t-" + v.id);
    const val = m ? m[v.id] : null;
    const clase = val != null && v.estado ? v.estado(val) : "";
    t.classList.remove("bien", "aviso", "mal", "nuevo");
    if (clase) t.classList.add(clase);
    if (destacar) { void t.offsetWidth; t.classList.add("nuevo"); } // reinicia el destello
    const previo = anterior && anterior.dev_eui === m?.dev_eui ? anterior[v.id] : (val != null ? v.escala[0] : null);
    animarNumero(t.querySelector(".numero"), previo, val, v.dec);
    const [a, b] = v.escala;
    const pct = val == null ? 0 : Math.max(3, Math.min(100, (val - a) / (b - a) * 100));
    t.querySelector(".barra i").style.width = pct + "%";
    t.querySelector(".etq-estado").textContent = val == null ? "Sin dato" : (TEXTO_ESTADO[clase] || "Informativo");
  }
  // Datos de radio de la portada
  $("#radio").textContent = m && m.spreading_factor ? `SF${m.spreading_factor} · ${m.rssi_dbm ?? "?"} dBm` : "EU868";
  document.querySelector("#t-rssi_dbm .extra").textContent = m ? `fcnt ${m.fcnt ?? "?"}` : "";

  const avisos = [];
  if (m) {
    if (m.agua_presente === false) avisos.push(["mal", "El sensor de presencia no detecta agua: rellenar el depósito."]);
    if (m.bomba_sin_caudal) avisos.push(["mal", "No hay caudal: la bomba está apagada, atascada o sin agua."]);
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
  $("#ultima-recepcion").innerHTML = `${fmtHora(m.tiempo)}<small>${hace(m.tiempo)}</small>`;
  $("#ultima-recepcion").title = fmtFecha(m.tiempo);
  if (min > MIN_SIN_DATOS) { p.textContent = "Nodo sin transmitir"; p.className = "pastilla cristal-suave caido"; }
  else if (conectadoTiempoReal) { p.textContent = "En directo"; p.className = "pastilla cristal-suave vivo"; }
}

// ---------- Gráficas ----------
const css = nombre => getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
const conAlfa = (hex, a) => hex + Math.round(a * 255).toString(16).padStart(2, "0");

function crearGraficas() {
  Object.values(estado.graficas).forEach(g => g.dispose());
  const cont = $("#graficas");
  cont.innerHTML = "";
  estado.graficas = {};
  const texto = css("--tenue"), rejilla = css("--rejilla"), tinta = css("--texto");
  VARIABLES.forEach((v, i) => {
    const div = document.createElement("div");
    div.className = "grafica";
    div.style.setProperty("--i", i);
    cont.appendChild(div);
    const g = echarts.init(div, null, { renderer: "canvas" });
    g.group = "agua"; // zoom y cursor sincronizados entre todas las gráficas
    g.setOption({
      animationDuration: sinMovimiento ? 0 : 900, animationEasing: "cubicOut",
      title: { text: `${v.nombre}${v.unidad ? " (" + v.unidad + ")" : ""}`, left: 12, top: 2,
               textStyle: { fontSize: 14, fontWeight: 650, color: tinta } },
      grid: { left: 52, right: 18, top: 40, bottom: 58 },
      tooltip: { trigger: "axis", backgroundColor: css("--panel"), borderColor: rejilla,
        textStyle: { color: tinta }, extraCssText: "backdrop-filter: blur(12px); border-radius: 12px;",
        valueFormatter: val => val == null ? "—" : fmtNum(val, v.dec) + (v.unidad ? " " + v.unidad : ""),
        axisPointer: { type: "line", lineStyle: { color: v.color, type: "dashed" },
                       label: { formatter: p => fmtFecha(p.value) } } },
      xAxis: { type: "time", axisLabel: { color: texto, hideOverlap: true,
               formatter: val => estado.horas > 0 && estado.horas <= 24 ? fmtHora(val) : fmtFecha(val) },
               axisLine: { lineStyle: { color: rejilla } }, axisTick: { show: false } },
      // Eje Y con un rango mínimo: si no, una variación de 0,05 de pH se vería enorme
      yAxis: { type: "value", scale: true, axisLabel: { color: texto },
               min: v.rangoMin ? r => Math.floor(Math.min(r.min, (r.min + r.max - v.rangoMin) / 2) * 10) / 10 : null,
               max: v.rangoMin ? r => Math.ceil(Math.max(r.max, (r.min + r.max + v.rangoMin) / 2) * 10) / 10 : null,
               splitLine: { lineStyle: { color: rejilla } } },
      dataZoom: [{ type: "inside" }, { type: "slider", height: 16, bottom: 10, borderColor: "transparent",
                  backgroundColor: rejilla, fillerColor: conAlfa(v.color, .18),
                  dataBackground: { lineStyle: { color: conAlfa(v.color, .5) }, areaStyle: { color: conAlfa(v.color, .15) } },
                  handleStyle: { color: v.color, borderColor: v.color }, moveHandleSize: 0,
                  labelFormatter: val => fmtFecha(val), textStyle: { color: texto, fontSize: 10 } }],
      toolbox: { right: 10, top: 0, itemSize: 13, iconStyle: { borderColor: texto }, feature: {
        dataZoom: { yAxisIndex: "none", title: { zoom: "Zoom", back: "Deshacer zoom" } },
        restore: { title: "Restaurar" }, saveAsImage: { title: "Guardar imagen", name: v.id } } },
      series: [{ type: "line", name: v.nombre, showSymbol: false, symbolSize: 7, smooth: 0.25, connectNulls: false,
                 lineStyle: { width: 2.5, color: v.color, shadowColor: conAlfa(v.color, .35), shadowBlur: 8, shadowOffsetY: 4 },
                 itemStyle: { color: v.color },
                 areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                   { offset: 0, color: conAlfa(v.color, .30) }, { offset: 1, color: conAlfa(v.color, 0) }]) },
                 data: [] }],
    });
    estado.graficas[v.id] = g;
  });
  echarts.connect("agua");
}

function rango() {
  if (estado.horas > 0) {
    const hasta = new Date();
    return { desde: new Date(hasta - estado.horas * 3600e3), hasta, envivo: true };
  }
  return { desde: estado.desde, hasta: estado.hasta, envivo: false };
}

// Con pocos puntos (rango de 1 h o 5 h: un dato cada 15 min) se dibujan también los puntos
function ponerSerie(g, datos, r) {
  g.setOption({
    xAxis: { min: r.desde.getTime(), max: r.hasta.getTime() },
    series: [{ data: datos, showSymbol: datos.length <= 60 }],
  });
}

async function cargarHistorico() {
  if (!estado.nodo) return;
  const r = rango();
  const q = `dev_eui=${encodeURIComponent(estado.nodo)}&desde=${r.desde.toISOString()}&hasta=${r.hasta.toISOString()}`;
  $("#csv").href = `/api/csv?${q}`;
  $("#info-historico").textContent = "Cargando…";
  const h = await pedir(`/api/historico?${q}`);
  const s = h.serie;
  for (const v of VARIABLES) ponerSerie(estado.graficas[v.id], s.tiempo.map((t, i) => [t, s[v.id][i]]), r);
  $("#info-historico").textContent = h.puntos === 0
    ? "No hay medidas en este intervalo."
    : `${h.medidas_totales.toLocaleString("es-ES")} medidas` + (h.agrupado_cada_s
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
    ponerSerie(g, datos, r);
  }
}

// ---------- Tiempo real (Server-Sent Events) ----------
let conectadoTiempoReal = false;
function conectarTiempoReal() {
  const es = new EventSource("/api/eventos");
  es.onopen = () => { conectadoTiempoReal = true; actualizarRecepcion(); };
  es.onerror = () => {
    conectadoTiempoReal = false;
    const p = $("#estado"); p.textContent = "Reconectando…"; p.className = "pastilla cristal-suave caido";
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

// Mueve la pastilla de cristal del selector de rango hasta el botón activo
function moverIndicador() {
  const b = document.querySelector(".rangos button.activo");
  const ind = document.querySelector(".rangos .indicador");
  if (!b || !ind) return;
  ind.style.width = b.offsetWidth + "px";
  ind.style.height = b.offsetHeight + "px";
  ind.style.transform = `translate(${b.offsetLeft}px, ${b.offsetTop}px)`;
}

function prepararControles() {
  document.querySelectorAll(".rangos button").forEach(b => b.addEventListener("click", () => {
    document.querySelectorAll(".rangos button").forEach(x => x.classList.remove("activo"));
    b.classList.add("activo");
    moverIndicador();
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
  $("#nodo").addEventListener("change", e => { estado.nodo = e.target.value; estado.ultima = null; cargarNodo().catch(mostrarError); });
  let espera;
  window.addEventListener("resize", () => {
    clearTimeout(espera);
    espera = setTimeout(() => { Object.values(estado.graficas).forEach(g => g.resize()); moverIndicador(); }, 120);
  });
  // Botón de tema: cambia entre claro y oscuro y se guarda en este navegador
  $("#tema").addEventListener("click", () => {
    const nuevo = document.documentElement.dataset.tema === "oscuro" ? "claro" : "oscuro";
    try { localStorage.setItem("tema", nuevo); } catch (e) { /* modo privado: solo para esta visita */ }
    ponerTema(nuevo);
  });
  // Si no se ha elegido nada con el botón, la web sigue al sistema aunque cambie con la página abierta
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", e => {
    let elegido = null;
    try { elegido = localStorage.getItem("tema"); } catch (err) {}
    if (!elegido) ponerTema(e.matches ? "oscuro" : "claro");
  });
  ponerTema(document.documentElement.dataset.tema);
  setInterval(actualizarRecepcion, 30000);
  moverIndicador();
  document.fonts?.ready.then(moverIndicador);
}

// Aplica el tema (data-tema en <html>) y vuelve a pintar las gráficas con los colores nuevos
function ponerTema(tema) {
  const raiz = document.documentElement;
  const cambia = raiz.dataset.tema !== tema;
  raiz.classList.add("cambiando-tema");
  raiz.dataset.tema = tema;
  document.querySelector('meta[name="theme-color"]').content = tema === "oscuro" ? "#06121c" : "#e8f3f7";
  const b = $("#tema"), texto = tema === "oscuro" ? "Cambiar a modo claro" : "Cambiar a modo oscuro";
  b.title = texto; b.setAttribute("aria-label", texto);
  setTimeout(() => raiz.classList.remove("cambiando-tema"), 500);
  if (cambia) { crearGraficas(); cargarHistorico().catch(mostrarError); }
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
  crearTarjetas();
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
