"""
Web del proyecto: API + página de la maqueta de calidad del agua.

- /                  página con los datos en tiempo real y las gráficas (static/)
- /api/nodos         nodos y su última recepción
- /api/ultima        última medida de un nodo
- /api/historico     serie de datos entre dos fechas (se agrupa sola si hay muchos puntos)
- /api/csv           descarga en CSV de las medidas en bruto
- /api/eventos       tiempo real (Server-Sent Events): cada uplink nuevo llega al navegador al momento

La base de datos avisa de cada medida nueva con NOTIFY (trigger en 10-init.sql).
La web entra con el usuario web_lector, que solo puede leer.
"""
import asyncio
import csv
import io
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import psycopg
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("web")

PG_DSN = os.environ["PG_DSN"]
CARPETA_STATIC = os.path.join(os.path.dirname(__file__), "static")

# Variables que se enseñan en la web (la conductividad ya no se mide)
VARIABLES = ["temperatura_c", "oxigeno_mgl", "ph", "nivel_mm", "caudal_lmin", "bateria_v", "rssi_dbm", "snr_db"]
PUNTOS_MAX = 1500  # por encima de esto se agrupan los datos en intervalos (medias)

pool: AsyncConnectionPool | None = None
suscriptores: set[asyncio.Queue] = set()


async def escuchar_bd():
    """Conexión dedicada con LISTEN: reparte cada medida nueva a los navegadores conectados."""
    while True:
        try:
            async with await psycopg.AsyncConnection.connect(PG_DSN, autocommit=True) as conn:
                await conn.execute("LISTEN nueva_medida")
                log.info("Escuchando medidas nuevas en la base de datos")
                async for aviso in conn.notifies():
                    fila = await ultima_medida(aviso.payload)
                    if fila:
                        datos = json.dumps(fila, default=a_json)
                        for cola in list(suscriptores):
                            cola.put_nowait(datos)
        except Exception as e:  # la BD se ha reiniciado o no está lista todavía
            log.warning("LISTEN caído (%s), reintento en 5 s", e)
            await asyncio.sleep(5)


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    global pool
    pool = AsyncConnectionPool(PG_DSN, min_size=1, max_size=5, open=False,
                               kwargs={"row_factory": dict_row})
    await pool.open()
    tarea = asyncio.create_task(escuchar_bd())
    yield
    tarea.cancel()
    await pool.close()


app = FastAPI(title="Calidad del agua", lifespan=ciclo_vida, docs_url=None, redoc_url=None)


def a_json(valor):
    """Fechas en ISO 8601 (las entiende cualquier navegador); el resto como texto."""
    return valor.isoformat() if isinstance(valor, datetime) else str(valor)


def a_utc(texto: str | None, por_defecto: datetime) -> datetime:
    """Convierte una fecha ISO del navegador a UTC. Sin zona horaria se entiende UTC."""
    if not texto:
        return por_defecto
    try:
        f = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(400, f"Fecha no válida: {texto}")
    return f if f.tzinfo else f.replace(tzinfo=timezone.utc)


async def ultima_medida(dev_eui: str) -> dict | None:
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT * FROM medidas WHERE dev_eui = %s ORDER BY tiempo DESC LIMIT 1", (dev_eui,))
        return await cur.fetchone()


@app.get("/api/nodos")
async def nodos():
    async with pool.connection() as conn:
        cur = await conn.execute("""
            SELECT n.dev_eui, n.nombre, n.ubicacion,
                   (SELECT max(tiempo) FROM medidas m WHERE m.dev_eui = n.dev_eui) AS ultima
            FROM nodos n ORDER BY ultima DESC NULLS LAST""")
        return await cur.fetchall()


@app.get("/api/ultima")
async def ultima(dev_eui: str):
    fila = await ultima_medida(dev_eui)
    if not fila:
        raise HTTPException(404, "Ese nodo no tiene medidas")
    return fila


@app.get("/api/historico")
async def historico(dev_eui: str, desde: str | None = None, hasta: str | None = None):
    ahora = datetime.now(timezone.utc)
    t_hasta = a_utc(hasta, ahora)
    t_desde = a_utc(desde, t_hasta - timedelta(hours=24))
    if t_desde >= t_hasta:
        raise HTTPException(400, "'desde' tiene que ser anterior a 'hasta'")

    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT count(*) AS n FROM medidas WHERE dev_eui = %s AND tiempo BETWEEN %s AND %s",
            (dev_eui, t_desde, t_hasta))
        n = (await cur.fetchone())["n"]

        columnas = ", ".join(VARIABLES)
        if n <= PUNTOS_MAX:
            intervalo_s = 0
            cur = await conn.execute(
                f"SELECT tiempo, {columnas} FROM medidas "
                "WHERE dev_eui = %s AND tiempo BETWEEN %s AND %s ORDER BY tiempo",
                (dev_eui, t_desde, t_hasta))
        else:
            # Demasiados puntos para la gráfica: medias por intervalo (time_bucket de TimescaleDB)
            intervalo_s = max(60, int((t_hasta - t_desde).total_seconds() / PUNTOS_MAX))
            medias = ", ".join(f"avg({v}) AS {v}" for v in VARIABLES)
            cur = await conn.execute(
                f"SELECT time_bucket(make_interval(secs => %s), tiempo) AS tiempo, {medias} "
                "FROM medidas WHERE dev_eui = %s AND tiempo BETWEEN %s AND %s "
                "GROUP BY 1 ORDER BY 1",
                (intervalo_s, dev_eui, t_desde, t_hasta))
        filas = await cur.fetchall()

    # Formato por columnas: más ligero y es lo que usan las gráficas
    serie = {"tiempo": [f["tiempo"].isoformat() for f in filas]}
    for v in VARIABLES:
        serie[v] = [None if f[v] is None else round(float(f[v]), 3) for f in filas]
    return {"desde": t_desde, "hasta": t_hasta, "puntos": len(filas),
            "medidas_totales": n, "agrupado_cada_s": intervalo_s, "serie": serie}


@app.get("/api/csv")
async def descargar_csv(dev_eui: str, desde: str | None = None, hasta: str | None = None):
    ahora = datetime.now(timezone.utc)
    t_hasta = a_utc(hasta, ahora)
    t_desde = a_utc(desde, t_hasta - timedelta(days=7))
    async with pool.connection() as conn:
        cur = await conn.execute(
            f"SELECT tiempo, fcnt, {', '.join(VARIABLES)}, agua_presente, bomba_sin_caudal, flags "
            "FROM medidas WHERE dev_eui = %s AND tiempo BETWEEN %s AND %s ORDER BY tiempo",
            (dev_eui, t_desde, t_hasta))
        filas = await cur.fetchall()
    salida = io.StringIO()
    if filas:
        w = csv.DictWriter(salida, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    nombre = f"medidas_{dev_eui}_{t_desde:%Y%m%d}_{t_hasta:%Y%m%d}.csv"
    return StreamingResponse(iter([salida.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="{nombre}"'})


@app.get("/api/eventos")
async def eventos(request: Request):
    cola: asyncio.Queue = asyncio.Queue(maxsize=100)
    suscriptores.add(cola)

    async def generar():
        try:
            yield "retry: 5000\n\n"
            while not await request.is_disconnected():
                try:
                    datos = await asyncio.wait_for(cola.get(), timeout=20)
                    yield f"event: medida\ndata: {datos}\n\n"
                except asyncio.TimeoutError:
                    yield ": latido\n\n"   # mantiene viva la conexión a través del proxy
        finally:
            suscriptores.discard(cola)

    return StreamingResponse(generar(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/salud")
async def salud():
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
    return {"estado": "ok"}


@app.get("/")
async def inicio():
    return FileResponse(os.path.join(CARPETA_STATIC, "index.html"))


app.mount("/static", StaticFiles(directory=CARPETA_STATIC), name="static")
