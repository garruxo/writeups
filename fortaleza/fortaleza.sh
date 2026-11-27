#!/bin/bash
# ============================================================
#  LA FORTALEZA - Panel de Control (con subcarpetas)
#  Autor: Daniel Garrucho Garcia.   Uso:  bash fortaleza.sh
# ============================================================
cd "$(dirname "$(readlink -f "$0")")" || exit 1
URL="http://localhost:8000"
APPLOG="app.log"
V='\033[1;32m'; R='\033[1;31m'; A='\033[1;33m'; C='\033[1;36m'; M='\033[1;35m'; X='\033[0m'

viva(){ curl -s -o /dev/null --max-time 2 "$URL/"; }
encender(){ viva || { setsid python3 app.py > "$APPLOG" 2>&1 < /dev/null & sleep 2; }; }
apagar(){ pkill -f "python3 app.py" 2>/dev/null; }
pausa(){ echo; read -rp "  [Enter para continuar] " _; }
pid(){ pgrep -f "python3 app.py" | head -1; }

estado(){
  if viva; then echo -e "${V}● VIVA${X}  $URL  (PID $(pid))"
  else echo -e "${R}● APAGADA${X}"; fi
}

# ---------- CONTROL ----------
control(){
  while true; do
    clear; echo -e "${C}== CONTROL ==${X}  $(estado)\n"
    echo "  1) Arrancar la Fortaleza"
    echo "  2) Parar"
    echo "  3) Reiniciar (limpia baneos y expedientes)"
    echo "  4) Estado"
    echo "  5) Atacar (demo: ver el muro aguantar)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) encender; estado; pausa;;
      2) apagar; echo -e "  ${A}Detenida.${X}"; pausa;;
      3) apagar; sleep 1; encender; echo -e "  ${V}Reiniciada (estado limpio).${X}"; pausa;;
      4) estado; pausa;;
      5) atacar_demo; pausa;;
      0) break;;
    esac
  done
}

atacar_demo(){
  encender
  echo -e "  ${C}1) SQLi en login ( ' OR 1=1-- ):${X}"
  echo -n "     -> "; curl -s -X POST "$URL/login" --data-urlencode "email=' OR 1=1--" --data "password=x"; echo
  echo -e "  ${C}2) Honeytoken (/.env):${X}"
  echo -n "     -> "; curl -s "$URL/.env"; echo
  echo -e "  ${C}3) XSS que evade la regex (lo caza la IA):${X}"
  echo -n "     -> "; curl -s -X POST "$URL/muro" --data-urlencode "mensaje=<details open ontoggle=x>"; echo
  echo -e "  ${V}El muro rebota; el intruso queda marcado (Analisis > expedientes).${X}"
}

# ---------- ANALISIS ----------
analisis(){
  while true; do
    clear; echo -e "${C}== ANALISIS ==${X}  $(estado)\n"
    echo "  1) Ver log de seguridad (ultimos intrusos)"
    echo "  2) Ver expedientes (quien ataca, sospecha, frontera)"
    echo "  3) Abrir el MAPA de ataques en el navegador"
    echo "  4) Medir clock skew (huella del reloj fisico)"
    echo "  5) Analizar un .pcap"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) if [ -s fortaleza_seguridad.log ]; then tail -n 20 fortaleza_seguridad.log
         else echo -e "  ${V}Sin intrusos todavia.${X}"; fi; pausa;;
      2) encender; curl -s "$URL/api/ataques" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if not d: print('  Sin ataques registrados.')
for a in d:
    fr=' [FRONTERA CERRADA]' if a.get('frontera_cerrada') else ''
    est='EXPULSADO' if a['expulsado'] else 'vigilado'
    print(f\"  {a['ip']:<16} sospecha {a['sospecha']:<2} {est:<9} origen {a.get('origen','')}{fr}\")
" 2>/dev/null || echo "  (arranca la Fortaleza primero)"; pausa;;
      3) encender; echo "  Abriendo $URL/mapa ..."; (xdg-open "$URL/mapa" >/dev/null 2>&1 &) || echo "  Abrelo a mano: $URL/mapa"; pausa;;
      4) encender; bash medir_skew.sh; pausa;;
      5) read -rp "  Ruta del .pcap: " p; [ -f "$p" ] && python3 cerebro_clockskew.py "$p" || echo -e "  ${R}No existe.${X}"; pausa;;
      0) break;;
    esac
  done
}

# ---------- IA ----------
ia(){
  while true; do
    clear; echo -e "${M}== IA (deteccion de anomalias) ==${X}\n"
    echo "  1) Ver metricas (recall / precision / F1)"
    echo "  2) Reentrenar la IA"
    echo "  3) Probar una peticion (¿la marca como anomala?)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) python3 cerebro_ia.py | sed 's/^/  /'; pausa;;
      2) rm -f cerebro_ia.joblib; python3 -c "import cerebro_ia; cerebro_ia.entrenar(); print('  modelo reentrenado')"; pausa;;
      3) read -rp "  Escribe una peticion (p.ej. /?q=1 UNION SELECT): " q
         python3 -c "import cerebro_ia as i; print('  ->', 'ANOMALA' if i.es_anomalo('''$q''') else 'normal')"; pausa;;
      0) break;;
    esac
  done
}

# ---------- PRODUCCION ----------
produccion(){
  while true; do
    clear; echo -e "${A}== PRODUCCION ==${X}\n"
    echo "  1) Desplegar (gunicorn + Redis + HTTPS)  -> https://localhost:8443"
    echo "  2) Estado de Redis"
    echo "  3) Ver configuracion (workers, puertos)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) echo "  Lanzando despliegue (Ctrl+C para parar)..."; bash desplegar.sh;;
      2) redis-cli ping 2>/dev/null && echo "  Redis OK" || echo -e "  ${R}Redis no responde (sudo service redis-server start)${X}"; pausa;;
      3) echo "  gunicorn: $(grep -E 'workers|bind' gunicorn_conf.py | sed 's/#.*//' | tr -d ' ')"; echo "  Despliegue: desplegar.sh -> :8443 (TLS)"; pausa;;
      0) break;;
    esac
  done
}

# ---------- PANEL PRINCIPAL ----------
encender   # auto-arranque al abrir el panel
while true; do
  clear
  echo -e "${C}"
  echo "   ╔════════════════════════════════════════╗"
  echo "   ║        🏰  LA FORTALEZA  ·  Panel       ║"
  echo "   ╚════════════════════════════════════════╝"
  echo -e "${X}   $(estado)\n"
  echo -e "   1) 🛡️   Control      (arrancar, parar, atacar)"
  echo -e "   2) 📊  Analisis     (log, expedientes, mapa, skew)"
  echo -e "   3) 🧠  IA           (metricas, reentrenar, probar)"
  echo -e "   4) 🏭  Produccion   (gunicorn + Redis + HTTPS)"
  echo -e "   0) Salir (la Fortaleza sigue encendida)"; echo
  read -rp "   Elige: " op; echo
  case "$op" in
    1) control;;
    2) analisis;;
    3) ia;;
    4) produccion;;
    0) echo -e "  ${C}Hasta la proxima, Daniel. (opcion Control>Parar para apagarla)${X}"; exit 0;;
    *) echo -e "  ${R}Opcion no valida.${X}"; sleep 1;;
  esac
done
