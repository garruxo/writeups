#!/bin/bash
# ============================================================
#  Icono de bandeja para controlar La Fortaleza (Kali/XFCE).
#  Click izquierdo: estado.  Click derecho: menu (arrancar/parar).
#  Requiere: yad   ->   sudo apt install yad
#  Uso: bash fortaleza_tray.sh
# ============================================================
SELF="$(readlink -f "$0")"
DIR="$(dirname "$SELF")"
cd "$DIR" || exit 1
URL="http://localhost:8000"
APPLOG="app.log"

viva(){ curl -s -o /dev/null --max-time 2 "$URL/"; }
encender(){ viva || { setsid python3 app.py > "$APPLOG" 2>&1 < /dev/null & } ; }
apagar(){ pkill -f "python3 app.py"; }

case "$1" in
  start)  encender; exit 0 ;;
  stop)   apagar;   exit 0 ;;
  status)
    if viva; then yad --info --timeout=3 --title="Fortaleza" \
        --text="●  La Fortaleza esta VIVA\n$URL"
    else yad --info --timeout=3 --title="Fortaleza" \
        --text="●  La Fortaleza esta APAGADA"; fi
    exit 0 ;;
  panel)
    setsid x-terminal-emulator -e bash -c "bash '$DIR/fortaleza.sh'; exec bash" \
      >/dev/null 2>&1 &
    exit 0 ;;
esac

# Sin argumento: arrancar (si no esta viva) y mostrar el icono de bandeja
encender; sleep 1

yad --notification \
    --image="security-high" \
    --text="La Fortaleza" \
    --command="bash '$SELF' status" \
    --menu="Estado!bash '$SELF' status!dialog-information|\
Arrancar!bash '$SELF' start!media-playback-start|\
Parar (desactivar)!bash '$SELF' stop!process-stop|\
Abrir panel!bash '$SELF' panel!utilities-terminal|\
Salir del icono!quit!application-exit"
