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
  echo; echo "=== IA evaluada con el dataset REAL ==="
  python3 cerebro_ia.py csic_normal.txt csic_ataques.txt
}

# 1) ¿Ya hay ficheros en la carpeta? -> usarlos
if convertir_y_evaluar; then exit 0; fi

# 2) Intentar un mirror estable (Hugging Face)
echo "[*] No hay ficheros locales. Probando mirror (Hugging Face)..."
MIRROR="https://huggingface.co/datasets/YangYang-Research/web-attack-detection/resolve/main/dataset.csv"
if curl -fsSL "$MIRROR" -o web_attack.csv 2>/dev/null && [ -s web_attack.csv ]; then
  echo "[*] Descargado web_attack.csv"
  convertir_y_evaluar && exit 0
fi

# 3) Guia manual
cat <<'TXT'
[!] No se pudo descargar automaticamente. Consigue un dataset real (gratis) y
    deja el fichero EN ESTA CARPETA; luego vuelve a ejecutar este script:

  Oficial (a veces caido):  https://www.tic.itefi.csic.es/dataset/
     -> normalTrafficTraining.txt, normalTrafficTest.txt, anomalousTrafficTest.txt
  Mirrors CSV en Hugging Face (busca "CSIC 2010" o "web attack detection"):
     https://huggingface.co/datasets?search=web%20attack%20detection

Si tu CSV tiene nombres de columna raros, conviertelo indicandolos a mano:
  python3 csv_a_corpus.py TU.csv <columna_peticion> <columna_etiqueta>
  python3 cerebro_ia.py csic_normal.txt csic_ataques.txt
TXT
