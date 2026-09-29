#!/bin/bash
# Copia de seguridad diaria de las dos bases de datos (medidas y ChirpStack). Añadir a cron:
#   0 3 * * * /home/<usuario>/TFG-2-STI-/raspberry/backup.sh >> /var/log/backup-agua.log 2>&1
# Mejor copiar además la carpeta backups/ fuera de la Raspberry (pendrive o PC) de vez en cuando.
set -euo pipefail
cd "$(dirname "$0")"
source .env
mkdir -p backups
fecha=$(date -u +%Y%m%d_%H%M)
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "backups/agua_$fecha.dump"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d chirpstack -Fc > "backups/chirpstack_$fecha.dump"
find backups -name '*.dump' -mtime +30 -delete
echo "Copias creadas: backups/agua_$fecha.dump y backups/chirpstack_$fecha.dump"
