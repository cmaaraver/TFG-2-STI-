#!/bin/bash
# Usuario de solo lectura para la web (no puede modificar ni borrar datos)
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE ROLE web_lector LOGIN PASSWORD '${WEB_DB_PASSWORD}';
  GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO web_lector;
  GRANT USAGE ON SCHEMA public TO web_lector;
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO web_lector;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO web_lector;
EOSQL
