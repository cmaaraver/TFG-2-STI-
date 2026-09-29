#!/bin/bash
# Copia de seguridad diaria. Añadir a cron del host:
#   0 3 * * * /ruta/servidor-datos/backup.sh >> /var/log/backup-agua.log 2>&1
set -euo pipefail
cd "$(dirname "$0")"
source .env
mkdir -p backups
f="backups/agua_$(date -u +%Y%m%d_%H%M).dump"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$f"
find backups -name '*.dump' -mtime +30 -delete
echo "Copia creada: $f"
