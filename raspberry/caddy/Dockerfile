# Caddy con el módulo de DuckDNS: saca el certificado HTTPS de Let's Encrypt por DNS,
# así funciona aunque el puerto 80 no esté abierto desde Internet.
FROM caddy:2-builder AS construir
RUN xcaddy build --with github.com/caddy-dns/duckdns

FROM caddy:2
COPY --from=construir /usr/bin/caddy /usr/bin/caddy
