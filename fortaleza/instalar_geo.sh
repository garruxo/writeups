#!/bin/bash
# Instala la geolocalizacion offline de La Fortaleza:
#   - libreria geoip2
#   - base de datos local gratuita y SIN CLAVE (DB-IP City Lite, formato .mmdb,
#     compatible con MaxMind GeoLite2 que usan CrowdSec / banip / iptables-geo)
cd "$(dirname "$(readlink -f "$0")")" || exit 1

echo "[*] Instalando libreria geoip2..."
sudo apt install -y python3-geoip2 2>/dev/null || pip install --break-system-packages geoip2 || pip install geoip2

echo "[*] Descargando base geo offline (DB-IP City Lite, gratis, sin registro)..."
MES=$(date +%Y-%m)
URL="https://download.db-ip.com/free/dbip-city-lite-${MES}.mmdb.gz"
if curl -fsSL "$URL" -o dbip.mmdb.gz 2>/dev/null; then
  gunzip -f dbip.mmdb.gz && mv -f dbip.mmdb GeoLite2-City.mmdb
  echo "[*] Base lista: $(pwd)/GeoLite2-City.mmdb"
  echo "[*] Reinicia la Fortaleza y el mapa ya situara a los atacantes por pais/ciudad."
else
  echo "[!] No se pudo descargar automaticamente ($URL)."
  echo "    Descargala a mano (gratis, sin clave) y guardala como GeoLite2-City.mmdb:"
  echo "      https://db-ip.com/db/download/ip-to-city-lite"
  echo "    Alternativa oficial (cuenta gratuita): MaxMind GeoLite2-City."
fi
