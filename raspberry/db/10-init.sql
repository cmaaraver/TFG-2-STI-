-- Esquema de la base de datos de calidad del agua (TimescaleDB). Horas siempre en UTC.
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Nodos dados de alta
CREATE TABLE nodos (
  dev_eui     text PRIMARY KEY,
  nombre      text,
  ubicacion   text,
  alta        timestamptz NOT NULL DEFAULT now()
);

-- Una fila por uplink recibido
CREATE TABLE medidas (
  tiempo              timestamptz NOT NULL,     -- hora de recepción en ChirpStack (UTC)
  dedup_id            uuid        NOT NULL,     -- id único de ChirpStack (evita duplicados)
  dev_eui             text        NOT NULL,
  fcnt                integer,
  temperatura_c       real,
  oxigeno_mgl         real,
  ph                  real,
  conductividad_uscm  real,
  nivel_mm            real,
  bateria_v           real,
  caudal_lmin         real,                     -- caudal de la bomba de recirculación
  agua_presente       boolean,
  bomba_sin_caudal    boolean,
  flags               smallint,
  rssi_dbm            smallint,
  snr_db              real,
  gateway_id          text,
  spreading_factor    smallint,
  recibido_en         timestamptz NOT NULL DEFAULT now(),  -- hora de inserción en la BD
  PRIMARY KEY (dedup_id, tiempo)
);
SELECT create_hypertable('medidas', 'tiempo');
CREATE INDEX medidas_nodo_tiempo ON medidas (dev_eui, tiempo DESC);

-- Mensaje completo tal como llega (auditoría y para reprocesar si cambia el codec)
CREATE TABLE uplinks_raw (
  dedup_id  uuid PRIMARY KEY,
  tiempo    timestamptz NOT NULL,
  mensaje   jsonb NOT NULL
);

-- Medias horarias calculadas automáticamente (para gráficas largas)
CREATE MATERIALIZED VIEW medidas_hora
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', tiempo) AS hora,
       dev_eui,
       avg(temperatura_c)      AS temperatura_c,
       avg(oxigeno_mgl)        AS oxigeno_mgl,
       avg(ph)                 AS ph,
       avg(conductividad_uscm) AS conductividad_uscm,
       avg(nivel_mm)           AS nivel_mm,
       min(bateria_v)          AS bateria_min_v,
       avg(caudal_lmin)        AS caudal_lmin,
       count(*)                AS n_mensajes
FROM medidas
GROUP BY hora, dev_eui
WITH NO DATA;

SELECT add_continuous_aggregate_policy('medidas_hora',
  start_offset => INTERVAL '3 days',
  end_offset   => INTERVAL '1 hour',
  schedule_interval => INTERVAL '30 minutes');

-- Aviso en tiempo real: cada medida nueva se publica en el canal "nueva_medida".
-- La web lo escucha (LISTEN) y la envía al navegador al instante, sin esperar a recargar.
CREATE FUNCTION avisar_medida() RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('nueva_medida', NEW.dev_eui);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER medida_insertada AFTER INSERT ON medidas
  FOR EACH ROW EXECUTE FUNCTION avisar_medida();
