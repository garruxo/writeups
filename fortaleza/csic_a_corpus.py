#!/usr/bin/env python3
"""
Convierte un fichero RAW del dataset CSIC 2010 (peticiones HTTP completas) en un
corpus para la IA: una peticion por linea ('path?query body'), igual formato que
el que captura la Fortaleza con LOG_TRAFICO.
Uso: python3 csic_a_corpus.py entrada_csic.txt salida_corpus.txt
"""
import sys, re
from urllib.parse import urlsplit

def parsear(entrada):
    reqs = []
    cur = None
    hdr_fin = False
    with open(entrada, encoding="latin-1", errors="ignore") as fh:
        for linea in fh:
            l = linea.rstrip("\n")
            m = re.match(r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+(\S+)\s+HTTP/', l)
            if m:
                if cur:
                    reqs.append(cur)
                sp = urlsplit(m.group(2))
                path = sp.path + (('?' + sp.query) if sp.query else '')
                cur = {"path": path, "body": ""}
                hdr_fin = False
            elif cur is not None:
                if l.strip() == "":
                    hdr_fin = True                     # fin de cabeceras
                elif hdr_fin and ("=" in l) and not re.match(r'^[A-Za-z-]+:\s', l):
                    cur["body"] = l.strip()            # cuerpo del POST
    if cur:
        reqs.append(cur)
    return reqs

def main():
    if len(sys.argv) != 3:
        print("uso: python3 csic_a_corpus.py entrada_csic.txt salida.txt"); sys.exit(1)
    reqs = parsear(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as out:
        for r in reqs:
            linea = r["path"] + ((" " + r["body"]) if r["body"] else "")
            out.write(linea.replace("\n", " ").strip() + "\n")
    print(f"{len(reqs)} peticiones -> {sys.argv[2]}")

if __name__ == "__main__":
    main()
