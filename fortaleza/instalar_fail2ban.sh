#!/bin/bash
# Instala la jail de La Fortaleza en fail2ban (requiere sudo).
# fail2ban leera el log de seguridad y baneara en iptables cada IP EXPULSADA.
cd "$(dirname "$(readlink -f "$0")")" || exit 1
LOG="$(pwd)/fortaleza_seguridad.log"

echo "[*] Instalando fail2ban (si falta)..."
sudo apt install -y fail2ban || exit 1

echo "[*] Copiando filtro y jail..."
sudo cp fail2ban/filter.d/fortaleza.conf /etc/fail2ban/filter.d/fortaleza.conf
sed "s#__LOGPATH__#$LOG#" fail2ban/jail.d/fortaleza.conf | sudo tee /etc/fail2ban/jail.d/fortaleza.conf >/dev/null

echo "[*] Comprobando el filtro contra el log..."
sudo fail2ban-regex "$LOG" /etc/fail2ban/filter.d/fortaleza.conf 2>/dev/null | grep -E "Failregex|matches" | head -3

echo "[*] Reiniciando fail2ban..."
sudo systemctl restart fail2ban
sleep 2
echo "[*] Estado de la jail:"
sudo fail2ban-client status fortaleza
echo
echo "Listo. A partir de ahora, cada IP que la Fortaleza expulse se banea"
echo "en iptables (todos los puertos) durante 24h. Ver IPs baneadas:"
echo "   sudo fail2ban-client status fortaleza"
