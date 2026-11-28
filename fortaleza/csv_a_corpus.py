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

REQ = {"url", "request", "payload", "req", "uri", "path", "content", "text", "http",
       "query", "sentence", "sample", "data", "raw", "input"}
LBL = {"label", "class", "classification", "type", "target", "y", "clase", "etiqueta",
       "attack", "labels", "category"}
# Palabras que, si aparecen en la etiqueta, marcan ATAQUE.
ATAQUE = ("anom", "anomal", "attack", "ataque", "malic", "bad", "intrus", "sqli",
          "xss", "injection")
NORMAL = ("normal", "benign", "valid", "legit", "clean", "0", "false", "no")

def es_ataque(lab):
    lab = lab.strip().lower()
    if lab in ("1", "true", "yes", "si"):
        return True
    if lab in NORMAL:
        return False
    return any(k in lab for k in ATAQUE)

def main():
    if len(sys.argv) < 2:
        print("uso: python3 csv_a_corpus.py dataset.csv [col_peticion col_etiqueta]"); return
    src = sys.argv[1]
    req_col = sys.argv[2] if len(sys.argv) > 3 else None
    lbl_col = sys.argv[3] if len(sys.argv) > 3 else None

    # utf-8-sig quita el BOM (﻿) que traen muchos CSV y que estropea el
    # nombre de la primera columna (p.ej. '﻿Sentence' -> 'Sentence').
    with open(src, encoding="utf-8-sig", errors="ignore", newline="") as fh:
        r = csv.DictReader(fh)
        cols = r.fieldnames or []
        if not req_col:
            req_col = next((c for c in cols if c and c.lower().lstrip("﻿") in REQ), None)
        if not lbl_col:
            lbl_col = next((c for c in cols if c and c.lower().lstrip("﻿") in LBL), None)
        if not req_col or not lbl_col:
            print("Columnas del CSV:", cols)
            print("No pude auto-detectar. Repite indicando columnas (sin < >):")
            print(f"  python3 csv_a_corpus.py {src} COL_PETICION COL_ETIQUETA")
            sys.exit(1)   # salir con error para que el script lo detecte
        normal, ataque = [], []
        for row in r:
            pet = (row.get(req_col) or "").strip().replace("\n", " ")
            lab = (row.get(lbl_col) or "")
            if not pet:
                continue
            (ataque if es_ataque(lab) else normal).append(pet)

    with open("csic_normal.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(normal) + "\n")
    with open("csic_ataques.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(ataque) + "\n")
    print(f"peticion='{req_col}'  etiqueta='{lbl_col}'")
    print(f"normal={len(normal)} -> csic_normal.txt   ataques={len(ataque)} -> csic_ataques.txt")

if __name__ == "__main__":
    main()
