#!/bin/bash
# medir_skew.sh - Captura + ataca + mide clock skew, TODO en un comando.
# Evita el fallo de orden (capturar antes de atacar) haciendolo automatico.
# Requiere: la Fortaleza (app.py) corriendo en 127.0.0.1:8000, tshark, sudo.
cd "$(dirname "$0")" || exit 1
PCAP=skew.pcap

# comprobar que la Fortaleza responde
if ! curl -s -o /dev/null http://localhost:8000/ ; then
  echo "[!] La Fortaleza no responde en el puerto 8000."
  echo "    Arranca 'python3 app.py' en otra terminal y repite."
  exit 1
fi

echo "[*] Necesito sudo para capturar trafico:"
sudo -v || exit 1

echo "[*] Capturando tcp/8000 en loopback durante ~130s..."
sudo timeout 130 tcpdump -i lo -s 0 -w "$PCAP" tcp port 8000 &
sleep 2   # dar tiempo a que tcpdump este escuchando ANTES de atacar

echo "[*] Abriendo UNA conexion larga de 120s (/stream)..."
echo "    (una sola conexion -> tsval lineal -> skew medible)"
curl -s -N --max-time 125 http://localhost:8000/stream > /dev/null

echo "[*] Esperando a que cierre la captura..."
wait
sudo chown "$USER" "$PCAP" 2>/dev/null

echo "[*] Analizando clock skew:"
echo "------------------------------------------------------------"
python3 cerebro_clockskew.py "$PCAP"
