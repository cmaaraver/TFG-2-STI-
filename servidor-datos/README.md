# PC servidor de datos

1. Ubuntu Server 24.04 LTS, IP estática 192.168.50.5/24, puerta de enlace y DNS 192.168.50.1.
2. NTP: en `/etc/systemd/timesyncd.conf` poner `NTP=192.168.50.1` y reiniciar `systemd-timesyncd`.
3. Instalar Docker (`curl -fsSL https://get.docker.com | sh`).
4. `cp .env.example .env` y cambiar todas las contraseñas.
5. `docker compose up -d --build` y ver logs: `docker compose logs -f ingestor`.
6. Grafana en `http://192.168.50.5:3000` (usuario admin). Crear el panel con consultas como:
   ```sql
   SELECT tiempo AS "time", ph FROM medidas
   WHERE $__timeFilter(tiempo) AND dev_eui = '<deveui>' ORDER BY 1
   ```
7. Cron de copias: `crontab -e` → `0 3 * * * /ruta/servidor-datos/backup.sh >> /var/log/backup-agua.log 2>&1`
8. Tailscale: instalar y `sudo tailscale up`. Enlace público opcional: `sudo tailscale funnel --bg 3000`.

## Prueba de robustez (obligatoria para la memoria)
1. `docker compose stop ingestor`
2. Esperar a que el nodo envíe 2 mensajes.
3. `docker compose start ingestor` → en los logs deben aparecer los 2 mensajes guardados.
4. `SELECT count(*) FROM medidas;` antes y después.
