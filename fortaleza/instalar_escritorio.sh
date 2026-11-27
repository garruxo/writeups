#!/bin/bash
# ============================================================
#  Integra La Fortaleza en el escritorio de Kali (XFCE).
#  Un solo comando, una vez. Despues: todo sin comandos.
#    - icono en la BARRA al iniciar sesion (autostart)
#    - iconos de DOBLE CLIC (Escritorio + menu de apps)
#    - desde el icono: Abrir panel / Parar
#  Requiere 'yad' para el icono de bandeja:  sudo apt install yad
# ============================================================
cd "$(dirname "$(readlink -f "$0")")" || exit 1
DIR="$(pwd)"
APPS="$HOME/.local/share/applications"
AUTO="$HOME/.config/autostart"
mkdir -p "$APPS" "$AUTO"

# 1) Icono de bandeja (arranca la Fortaleza + menu: Abrir panel / Parar)
cat > "$APPS/fortaleza-tray.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=La Fortaleza (barra)
Comment=Icono de bandeja: arrancar/parar y abrir el panel
Exec=bash "$DIR/fortaleza_tray.sh"
Icon=security-high
Terminal=false
Categories=Security;System;
EOF

# 2) Acceso directo al Panel (doble clic, sin comandos)
cat > "$APPS/fortaleza-panel.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=La Fortaleza · Panel
Comment=Abre el panel de control en una terminal
Exec=bash -c 'cd "$DIR"; x-terminal-emulator -e bash -c "bash fortaleza.sh; exec bash" || xterm -e bash -c "bash fortaleza.sh; exec bash"'
Icon=utilities-terminal
Terminal=false
Categories=Security;System;
EOF

# 3) Autostart: el icono de la barra aparece al iniciar sesion
cp "$APPS/fortaleza-tray.desktop" "$AUTO/fortaleza-tray.desktop"

# 4) Iconos en el Escritorio (doble clic), marcados de confianza
DESK="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
if [ -d "$DESK" ]; then
  cp "$APPS/fortaleza-tray.desktop" "$APPS/fortaleza-panel.desktop" "$DESK/" 2>/dev/null
  chmod +x "$DESK"/fortaleza-*.desktop 2>/dev/null
  gio set "$DESK/fortaleza-tray.desktop"  metadata::trusted true 2>/dev/null
  gio set "$DESK/fortaleza-panel.desktop" metadata::trusted true 2>/dev/null
fi
update-desktop-database "$APPS" 2>/dev/null

echo "Listo:"
echo " - Al iniciar Kali, el icono de La Fortaleza aparece en la BARRA (arriba)."
echo " - En el menu de apps y en el Escritorio: 'La Fortaleza (barra)' y 'La Fortaleza · Panel'."
echo " - Clic derecho en el icono de la barra -> Abrir panel / Parar (apagar)."
echo
echo "Si el icono no sale, instala yad:  sudo apt install yad"
