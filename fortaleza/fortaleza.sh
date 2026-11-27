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

# monitor en vivo del log (Enter para parar)
monitor(){
  [ -f fortaleza_seguridad.log ] || { echo "  (sin log todavia)"; return; }
  echo -e "  ${C}Monitor en vivo. Pulsa Enter para volver.${X}\n"
  tail -n 8 -f fortaleza_seguridad.log & local t=$!
  read -r _; kill "$t" 2>/dev/null; wait "$t" 2>/dev/null
}

# resumen tipo dashboard en el terminal
resumen(){
  encender
  curl -s "$URL/api/ataques" | python3 -c "
import sys,json
from collections import Counter
d=json.load(sys.stdin)
exp=sum(1 for a in d if a['expulsado']); fr=sum(1 for a in d if a.get('frontera_cerrada'))
ev=sum(a['n_eventos'] for a in d)
print(f'  Vigilados: {len(d)}   Expulsados: {exp}   Fronteras cerradas: {fr}   Eventos: {ev}')
mot=Counter()
for a in d:
    for e in a.get('eventos',[]): mot[e['motivo']]+=1
if mot: print('  Top motivos: '+', '.join(f'{m}={n}' for m,n in mot.most_common(6)))
" 2>/dev/null || echo "  (arranca la Fortaleza)"
}

# chequeo de salud de los componentes
salud(){
  echo -n "  App (Fortaleza): "; viva && echo -e "${V}OK${X}" || echo -e "${R}CAIDA${X}"
  echo -n "  Redis:           "; redis-cli ping >/dev/null 2>&1 && echo -e "${V}OK${X}" || echo -e "${A}no (opcional en desarrollo)${X}"
  echo -n "  fail2ban:        "; systemctl is-active fail2ban >/dev/null 2>&1 && echo -e "${V}activo${X}" || echo -e "${A}no instalado (Produccion > fail2ban)${X}"
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
    echo "  2) Monitor EN VIVO (log en tiempo real)"
    echo "  3) Resumen rapido (dashboard en terminal)"
    echo "  4) Ver expedientes (quien ataca, sospecha, frontera)"
    echo "  5) Abrir el MAPA de ataques en el navegador"
    echo "  6) Medir clock skew (huella del reloj fisico)"
    echo "  7) Analizar un .pcap"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) if [ -s fortaleza_seguridad.log ]; then tail -n 20 fortaleza_seguridad.log
         else echo -e "  ${V}Sin intrusos todavia.${X}"; fi; pausa;;
      2) monitor;;
      3) resumen; pausa;;
      4) encender; curl -s "$URL/api/ataques" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if not d: print('  Sin ataques registrados.')
for a in d:
    fr=' [FRONTERA CERRADA]' if a.get('frontera_cerrada') else ''
    est='EXPULSADO' if a['expulsado'] else 'vigilado'
    print(f\"  {a['ip']:<16} sospecha {a['sospecha']:<2} {est:<9} origen {a.get('origen','')}{fr}\")
" 2>/dev/null || echo "  (arranca la Fortaleza primero)"; pausa;;
      5) encender; echo "  Abriendo $URL/mapa ..."; (xdg-open "$URL/mapa" >/dev/null 2>&1 &) || echo "  Abrelo a mano: $URL/mapa"; pausa;;
      6) encender; bash medir_skew.sh; pausa;;
      7) read -rp "  Ruta del .pcap: " p; [ -f "$p" ] && python3 cerebro_clockskew.py "$p" || echo -e "  ${R}No existe.${X}"; pausa;;
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
    echo "  1) Chequeo de salud (app / Redis / fail2ban)"
    echo "  2) Desplegar (gunicorn + Redis + HTTPS)  -> https://localhost:8443"
    echo "  3) fail2ban: INSTALAR frontera a nivel de sistema (iptables)"
    echo "  4) fail2ban: ver IPs baneadas en el cortafuegos"
    echo "  5) Estado de Redis"
    echo "  6) Ver configuracion (workers, puertos)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) salud; pausa;;
      2) echo "  Lanzando despliegue (Ctrl+C para parar)..."; bash desplegar.sh;;
      3) echo "  Instala fail2ban para banear en iptables las IPs expulsadas (sudo):"; bash instalar_fail2ban.sh; pausa;;
      4) sudo fail2ban-client status fortaleza 2>/dev/null || echo -e "  ${A}Jail no instalada (opcion 3) o fail2ban parado.${X}"; pausa;;
      5) redis-cli ping 2>/dev/null && echo "  Redis OK" || echo -e "  ${R}Redis no responde (sudo service redis-server start)${X}"; pausa;;
      6) echo "  gunicorn: $(grep -E 'workers|bind' gunicorn_conf.py | sed 's/#.*//' | tr -d ' ')"; echo "  Despliegue: desplegar.sh -> :8443 (TLS)"; pausa;;
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
