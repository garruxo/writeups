#!/bin/bash
# ============================================================
#  Despliegue de La Fortaleza en modo PRODUCCION (laboratorio).
#  gunicorn (varios workers) + Redis (estado compartido) + TLS.
#  Primera vez:
#     pip install -r requirements.txt
#     sudo apt install redis-server
#  Luego:  bash desplegar.sh
# ============================================================
cd "$(dirname "$0")" || exit 1

# 1) Redis en marcha (estado compartido entre workers)
if ! redis-cli ping >/dev/null 2>&1; then
  echo "[!] Redis no responde. Arrancalo:  sudo service redis-server start"
  echo "    (sigo igual; sin Redis, gunicorn con >1 worker dara sesiones incoherentes)"
fi

# 2) Certificado autofirmado para TLS (solo laboratorio)
if [ ! -f cert.pem ]; then
  echo "[*] Generando certificado autofirmado..."
  openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem \
    -days 365 -subj "/CN=localhost" 2>/dev/null
fi

# 3) Arranque: gunicorn con Redis + TLS + 4 workers
export REDIS_URL="redis://localhost:6379/0"
echo "[*] Arrancando gunicorn en https://localhost:8443 (4 workers, Redis)"
exec gunicorn --certfile cert.pem --keyfile key.pem \
     --bind 127.0.0.1:8443 -c gunicorn_conf.py app:app
