#!/usr/bin/env python3
"""
Convierte un CSV de trafico web (CSIC 2010 u otro dataset etiquetado, como los
mirrors de Hugging Face) en dos corpus: csic_normal.txt y csic_ataques.txt.
Auto-detecta la columna de la PETICION y la de la ETIQUETA (normal/anomalo).

Uso:
  python3 csv_a_corpus.py dataset.csv                 # auto-detecta columnas
  python3 csv_a_corpus.py dataset.csv <col_peticion> <col_etiqueta>   # a mano
"""
import sys, csv
csv.field_size_limit(10_000_000)

REQ = {"url", "request", "payload", "req", "uri", "path", "content", "text", "http", "query"}
LBL = {"label", "class", "classification", "type", "target", "y", "clase", "etiqueta", "attack"}
ATAQUE = {"anom", "anomalous", "anomalo", "anomaly", "attack", "ataque",
          "malicious", "bad", "1", "true", "yes"}

def main():
    if len(sys.argv) < 2:
        print("uso: python3 csv_a_corpus.py dataset.csv [col_peticion col_etiqueta]"); return
    src = sys.argv[1]
    req_col = sys.argv[2] if len(sys.argv) > 3 else None
    lbl_col = sys.argv[3] if len(sys.argv) > 3 else None

    with open(src, encoding="utf-8", errors="ignore", newline="") as fh:
        r = csv.DictReader(fh)
        cols = r.fieldnames or []
        if not req_col:
            req_col = next((c for c in cols if c and c.lower() in REQ), None)
        if not lbl_col:
            lbl_col = next((c for c in cols if c and c.lower() in LBL), None)
        if not req_col or not lbl_col:
            print("Columnas del CSV:", cols)
            print("No pude auto-detectar. Repite indicando columnas:")
            print(f"  python3 csv_a_corpus.py {src} <col_peticion> <col_etiqueta>")
            return
        normal, ataque = [], []
        for row in r:
            pet = (row.get(req_col) or "").strip().replace("\n", " ")
            lab = (row.get(lbl_col) or "").strip().lower()
            if not pet:
                continue
            (ataque if lab in ATAQUE else normal).append(pet)

    with open("csic_normal.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(normal) + "\n")
    with open("csic_ataques.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(ataque) + "\n")
    print(f"peticion='{req_col}'  etiqueta='{lbl_col}'")
    print(f"normal={len(normal)} -> csic_normal.txt   ataques={len(ataque)} -> csic_ataques.txt")

if __name__ == "__main__":
    main()
