#!/bin/bash
# ============================================================
#  LA FORTALEZA - Panel de Control
#  Defensa activa (legal) en laboratorio. Autor: Daniel Garrucho
#  Uso:  bash fortaleza.sh
# ============================================================
cd "$(dirname "$0")" || exit 1
PIDFILE=".app.pid"
APPLOG="app.log"
URL="http://localhost:8000"

# --- colores ---
V='\033[1;32m'; R='\033[1;31m'; A='\033[1;33m'; C='\033[1;36m'; X='\033[0m'

viva()      { curl -s -o /dev/null --max-time 2 "$URL/" ; }
pausa()     { echo; read -rp "  [Enter para volver al menu] " _; }

arrancar() {
  if viva; then echo -e "  ${A}La Fortaleza ya esta viva.${X}"; return; fi
  echo -e "  ${C}Arrancando la Fortaleza...${X}"
  nohup python3 app.py > "$APPLOG" 2>&1 &
  echo $! > "$PIDFILE"
  sleep 2
  if viva; then echo -e "  ${V}Viva en $URL (PID $(cat $PIDFILE)).${X}"
  else echo -e "  ${R}No arranco. Mira $APPLOG.${X}"; fi
}

estado() {
  if viva; then echo -e "  ${V}● VIVA${X}  en $URL  (PID $(cat $PIDFILE 2>/dev/null || echo '?'))"
  else echo -e "  ${R}● APAGADA${X}"; fi
}

parar() {
  pkill -f "python3 app.py" 2>/dev/null
  rm -f "$PIDFILE"
  echo -e "  ${A}Fortaleza detenida.${X}"
}

atacar_demo() {
  if ! viva; then echo -e "  ${R}Arranca la Fortaleza primero (opcion 1).${X}"; return; fi
  echo -e "  ${C}1) SQLi en login ( ' OR 1=1-- ):${X}"
  echo -n "     respuesta -> "; curl -s -X POST "$URL/login" --data-urlencode "email=' OR 1=1--" --data "password=x"; echo
  echo -e "  ${C}2) Honeytoken (/.env):${X}"
  echo -n "     respuesta -> "; curl -s "$URL/.env"; echo
  echo -e "  ${C}3) Login correcto:${X}"
  echo -n "     respuesta -> "; curl -s -X POST "$URL/login" --data "email=daniel@fortaleza.lab&password=Pa\$\$w0rd-Fuerte-2026!"; echo
  echo -e "  ${V}El muro rebota el ataque y marca al intruso en el log (opcion 6).${X}"
}

medir_skew() {
  if ! viva; then echo -e "  ${R}Arranca la Fortaleza primero (opcion 1).${X}"; return; fi
  echo -e "  ${C}Midiendo clock skew (~2 min, no toques nada)...${X}"
  bash medir_skew.sh
}

analizar_pcap() {
  read -rp "  Ruta del .pcap a analizar: " p
  [ -f "$p" ] && python3 cerebro_clockskew.py "$p" || echo -e "  ${R}No existe: $p${X}"
}

ver_log() {
  if [ -s fortaleza_seguridad.log ]; then
    echo -e "  ${A}Ultimos intrusos detectados:${X}"
    tail -n 20 fortaleza_seguridad.log
  else
    echo -e "  ${V}Sin intrusos registrados todavia.${X}"
  fi
}

menu() {
  clear
  echo -e "${C}"
  echo "   ╔════════════════════════════════════════╗"
  echo "   ║        🏰  LA FORTALEZA  ·  Panel       ║"
  echo "   ╚════════════════════════════════════════╝"
  echo -e "${X}"
  echo -n "   Estado: "; estado
  echo
  echo "   1) Arrancar la Fortaleza (web blindada)"
  echo "   2) Estado"
  echo "   3) Parar la Fortaleza"
  echo "   4) Atacar (demo: ver el muro aguantar)"
  echo "   5) Medir clock skew (experimento)"
  echo "   6) Ver log de seguridad (intrusos)"
  echo "   7) Analizar un .pcap existente"
  echo "   0) Salir"
  echo
}

while true; do
  menu
  read -rp "   Elige opcion: " op
  echo
  case "$op" in
    1) arrancar ;;
    2) estado ;;
    3) parar ;;
    4) atacar_demo ;;
    5) medir_skew ;;
    6) ver_log ;;
    7) analizar_pcap ;;
    0) echo -e "  ${C}Hasta la proxima, Daniel.${X}"; exit 0 ;;
    *) echo -e "  ${R}Opcion no valida.${X}" ;;
  esac
  pausa
done
