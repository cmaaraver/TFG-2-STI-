#!/bin/bash
# Usuario de solo lectura para Grafana
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE ROLE grafana_lector LOGIN PASSWORD '${GRAFANA_DB_PASSWORD}';
  GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO grafana_lector;
  GRANT USAGE ON SCHEMA public TO grafana_lector;
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_lector;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO grafana_lector;
EOSQL
