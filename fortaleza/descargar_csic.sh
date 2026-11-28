#!/bin/bash
# Prepara el dataset REAL CSIC 2010 (trafico HTTP academico etiquetado) como
# corpus para la IA, y la evalua con el.
cd "$(dirname "$(readlink -f "$0")")" || exit 1

echo "=== Dataset CSIC 2010 (trafico HTTP real etiquetado) ==="
echo "Descarga los 3 ficheros desde la pagina OFICIAL:"
echo "   https://www.tic.itefi.csic.es/dataset/"
echo "   - Normal Traffic (Training)  -> guarda como  normalTrafficTraining.txt"
echo "   - Normal Traffic (Test)      -> guarda como  normalTrafficTest.txt"
echo "   - Anomalous Traffic (Test)   -> guarda como  anomalousTrafficTest.txt"
echo "en esta carpeta: $(pwd)"
echo
read -rp "Pulsa Enter cuando los tengas aqui... " _

falta=0
for f in normalTrafficTraining.txt anomalousTrafficTest.txt; do
  [ -f "$f" ] || { echo "  [!] falta $f"; falta=1; }
done
[ "$falta" = 1 ] && { echo "Descarga los ficheros y repite."; exit 1; }

echo "[*] Convirtiendo a corpus..."
cat normalTrafficTraining.txt normalTrafficTest.txt 2>/dev/null > _normal_csic.txt
python3 csic_a_corpus.py _normal_csic.txt csic_normal.txt
python3 csic_a_corpus.py anomalousTrafficTest.txt csic_ataques.txt
rm -f _normal_csic.txt

echo
echo "=== IA evaluada con el dataset REAL CSIC 2010 ==="
python3 cerebro_ia.py csic_normal.txt csic_ataques.txt
