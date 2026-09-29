#!/bin/bash
# Base de datos y usuario de ChirpStack en la misma instancia de PostgreSQL.
# Extensiones que pide ChirpStack v4 (igual que chirpstack-docker/configuration/postgresql/initdb).
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE ROLE chirpstack LOGIN PASSWORD '${CHIRPSTACK_DB_PASSWORD}';
  CREATE DATABASE chirpstack OWNER chirpstack;
EOSQL
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname chirpstack <<-EOSQL
  CREATE EXTENSION pg_trgm;
  CREATE EXTENSION hstore;
EOSQL
