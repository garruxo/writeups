#!/bin/bash
# ============================================================
#  LA FORTALEZA - Panel de Control (con subcarpetas)
#  Autor: Daniel Garrucho Garcia.   Uso:  bash fortaleza.sh
# ============================================================
cd "$(dirname "$(readlink -f "$0")")" || exit 1
URL="http://localhost:8000"
APPLOG="app.log"
V='\033[1;32m'; R='\033[1;31m'; A='\033[1;33m'; C='\033[1;36m'; M='\033[1;35m'; X='\033[0m'

viva(){ curl -s -o /dev/null --max-time 3 "$URL/"; }
encender(){ viva || { setsid env TRUSTED_PROXIES=127.0.0.1 BIND_HOST="${FORT_HOST:-127.0.0.1}" python3 app.py > "$APPLOG" 2>&1 < /dev/null & sleep 2; }; }
apagar(){ pkill -f "python3 app.py" 2>/dev/null; }
arrancar_exterior(){
  apagar; sleep 1
  setsid env BIND_HOST=0.0.0.0 python3 app.py > "$APPLOG" 2>&1 < /dev/null & sleep 2
  local ipv; ipv=$(hostname -I 2>/dev/null | awk '{print $1}')
  echo -e "  ${V}Accesible desde el exterior en http://${ipv:-TU_IP}:8000${X}"
  echo "  (otras maquinas de la red ya pueden conectarse y atacar)"
}
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
    echo "  1) Arrancar la Fortaleza (solo este equipo)"
    echo "  2) Arrancar accesible desde el EXTERIOR (0.0.0.0)"
    echo "  3) Parar"
    echo "  4) Reiniciar (limpia baneos y expedientes)"
    echo "  5) Estado"
    echo "  6) Atacar (demo: ver el muro aguantar)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) encender; estado; pausa;;
      2) arrancar_exterior; pausa;;
      3) apagar; echo -e "  ${A}Detenida.${X}"; pausa;;
      4) apagar; sleep 1; encender; echo -e "  ${V}Reiniciada (estado limpio).${X}"; pausa;;
      5) estado; pausa;;
      6) atacar_demo; pausa;;
      0) break;;
    esac
  done
}

atacar_demo(){
  encender
  local F="45.148.10.9"   # IP de atacante SIMULADA, publica (asi no te baneas a ti)
  echo -e "  ${A}Demo: atacamos como el IP externo $F (tu equipo no se bloquea).${X}\n"
  echo -e "  ${C}1) SQLi en login ( ' OR 1=1-- ):${X}"
  echo -n "     -> "; curl -s -H "X-Forwarded-For: $F" -X POST "$URL/login" --data-urlencode "email=' OR 1=1--" --data "password=x"; echo
  echo -e "  ${C}2) Honeytoken (/.env):${X}"
  echo -n "     -> "; curl -s -H "X-Forwarded-For: $F" "$URL/.env"; echo
  echo -e "  ${C}3) XSS que evade la regex (lo caza la IA):${X}"
  echo -n "     -> "; curl -s -H "X-Forwarded-For: $F" -X POST "$URL/muro" --data-urlencode "mensaje=<details open ontoggle=x>"; echo
  echo -e "\n  ${V}El muro rebota y $F queda EXPULSADO. Mira Analisis > expedientes o el mapa.${X}"
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
    if ! python3 -c "import sklearn" 2>/dev/null; then
      echo -e "  ${R}Falta scikit-learn (la IA no puede funcionar).${X}"
      echo -e "  ${A}La Fortaleza funciona igual sin IA; para activarla, instalala:${X}\n"
      echo "  i) Instalar la IA ahora (sudo apt install python3-sklearn...)"
      echo "  0) Volver"; echo
      read -rp "  Opcion: " o; echo
      case "$o" in
        i|I) sudo apt install -y python3-sklearn python3-numpy python3-joblib; pausa;;
        0) break;;
      esac
      continue
    fi
    echo "  1) Ver metricas (datos sinteticos de laboratorio)"
    echo "  2) Reentrenar la IA"
    echo "  3) Probar una peticion (¿la marca como anomala?)"
    echo "  4) Evaluar con TRAFICO REAL capturado (tus .txt)"
    echo "  5) Capturar trafico real (guia)"
    echo "  6) Evaluar con el dataset REAL CSIC 2010"
    echo "  7) Comparar SUPERVISADO vs no supervisado (mismos .txt)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) python3 cerebro_ia.py | sed 's/^/  /'; pausa;;
      2) rm -f cerebro_ia.joblib; python3 -c "import cerebro_ia; cerebro_ia.entrenar(); print('  modelo reentrenado')"; pausa;;
      3) read -rp "  Escribe una peticion (p.ej. /?q=1 UNION SELECT): " q
         Q="$q" python3 -c "import os,cerebro_ia as i; print('  ->', 'ANOMALA' if i.es_anomalo(os.environ['Q']) else 'normal')"; pausa;;
      4) read -rp "  Fichero de trafico NORMAL (.txt): " fn
         read -rp "  Fichero de ATAQUES (.txt): " fa
         [ -f "$fn" ] && [ -f "$fa" ] && python3 cerebro_ia.py "$fn" "$fa" | sed 's/^/  /' || echo -e "  ${R}No existen esos ficheros.${X}"; pausa;;
      5) echo -e "  ${C}Como capturar tu propio trafico real:${X}"
         echo "  1. Para la Fortaleza (Control > Parar)."
         echo "  2. Arrancala GRABANDO el trafico NORMAL mientras la usas normal:"
         echo "       LOG_TRAFICO=normal.txt python3 app.py   (navega, entra, postea; luego Ctrl+C)"
         echo "  3. Arrancala grabando los ATAQUES mientras atacas (atacante.py / sqlmap):"
         echo "       LOG_TRAFICO=ataques.txt python3 app.py   (lanza ataques; luego Ctrl+C)"
         echo "  4. Vuelve aqui, opcion 4, y pasale normal.txt y ataques.txt."; pausa;;
      6) echo -e "  ${C}Dataset REAL academico CSIC 2010:${X}"; bash descargar_csic.sh | sed 's/^/  /'; pausa;;
      7) read -rp "  Fichero de trafico NORMAL (.txt): " fn
         read -rp "  Fichero de ATAQUES (.txt): " fa
         if [ -f "$fn" ] && [ -f "$fa" ]; then
           echo -e "  ${C}--- NO SUPERVISADO (cerebro_ia: solo ve lo normal) ---${X}"
           python3 cerebro_ia.py "$fn" "$fa" | sed 's/^/  /'
           echo; echo -e "  ${C}--- SUPERVISADO (cerebro_super: aprende de los ataques) ---${X}"
           python3 cerebro_super.py "$fn" "$fa" | sed 's/^/  /'
         else echo -e "  ${R}No existen esos ficheros.${X}"; fi; pausa;;
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
    echo "  7) Geo: instalar base de geolocalizacion (mapa por pais)"
    echo "  8) Geo: bloquear un PAIS (geo-blocking)"
    echo "  0) Volver"; echo
    read -rp "  Opcion: " o; echo
    case "$o" in
      1) salud; pausa;;
      2) echo "  Lanzando despliegue (Ctrl+C para parar)..."; bash desplegar.sh;;
      3) echo "  Instala fail2ban para banear en iptables las IPs expulsadas (sudo):"; bash instalar_fail2ban.sh; pausa;;
      4) sudo fail2ban-client status fortaleza 2>/dev/null || echo -e "  ${A}Jail no instalada (opcion 3) o fail2ban parado.${X}"; pausa;;
      5) redis-cli ping 2>/dev/null && echo "  Redis OK" || echo -e "  ${R}Redis no responde (sudo service redis-server start)${X}"; pausa;;
      6) echo "  gunicorn: $(grep -E 'workers|bind' gunicorn_conf.py | sed 's/#.*//' | tr -d ' ')"; echo "  Despliegue: desplegar.sh -> :8443 (TLS)"; pausa;;
      7) bash instalar_geo.sh; pausa;;
      8) read -rp "  Codigo ISO del pais a bloquear (ej RU, CN): " pb
         apagar; sleep 1
         setsid env TRUSTED_PROXIES=127.0.0.1 BLOQUEAR_PAISES="$pb" python3 app.py > "$APPLOG" 2>&1 < /dev/null & sleep 2
         echo -e "  ${V}Reiniciada bloqueando trafico de: $pb${X} (necesita la base geo instalada)"; pausa;;
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
