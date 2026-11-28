#!/bin/bash
# Prepara un dataset REAL de trafico HTTP etiquetado como corpus para la IA y la
# evalua. Acepta el formato ORIGINAL (txt crudo) o CSV (mirrors). Auto-detecta.
cd "$(dirname "$(readlink -f "$0")")" || exit 1

convertir_y_evaluar() {
  if ls normalTraffic*.txt >/dev/null 2>&1 && ls anomalous*.txt >/dev/null 2>&1; then
    echo "[*] Formato original (txt crudo) detectado."
    cat normalTraffic*.txt > _n.txt
    python3 csic_a_corpus.py _n.txt csic_normal.txt
    python3 csic_a_corpus.py anomalous*.txt csic_ataques.txt
    rm -f _n.txt
  elif ls *.csv >/dev/null 2>&1; then
    CSV=$(ls -S *.csv | head -1)
    echo "[*] CSV detectado: $CSV"
    python3 csv_a_corpus.py "$CSV" || return 1
  else
    return 1
  fi
  # verificar que SI se genero el corpus antes de evaluar (no petar)
  if [ ! -s csic_normal.txt ] || [ ! -s csic_ataques.txt ]; then
    echo "[!] No se pudo generar el corpus desde ese fichero (formato no valido)."
    return 1
  fi
  echo; echo "=== IA evaluada con el dataset REAL ==="
  python3 cerebro_ia.py csic_normal.txt csic_ataques.txt
}

# ¿Hay ficheros del dataset en la carpeta? -> convertir y evaluar
if convertir_y_evaluar; then exit 0; fi

# Si no, guiar (sin descargas a ciegas: los mirrors cambian y no son fiables)
cat <<'TXT'
[!] No hay ningun dataset en esta carpeta. Consigue uno real (gratis), deja el
    fichero AQUI, y vuelve a ejecutar este script (lo detecta solo).

  Desde el navegador (lo mas facil ahora que el oficial esta caido):
    1. Entra en Hugging Face y busca "web attack detection" o "CSIC 2010":
         https://huggingface.co/datasets?search=web+attack+detection
    2. Abre un dataset, pestaña "Files", descarga el .csv
    3. Guardalo en esta carpeta y ejecuta de nuevo:  bash descargar_csic.sh

  Oficial (cuando vuelva a estar en linea):
    https://www.tic.itefi.csic.es/dataset/
    -> normalTrafficTraining.txt, normalTrafficTest.txt, anomalousTrafficTest.txt

Si el CSV tiene columnas con nombres raros, mira cuales son y pasalas a mano
(SIN los simbolos < >, que en la terminal dan error):
  python3 csv_a_corpus.py TU.csv COLUMNA_PETICION COLUMNA_ETIQUETA
  python3 cerebro_ia.py csic_normal.txt csic_ataques.txt
TXT
