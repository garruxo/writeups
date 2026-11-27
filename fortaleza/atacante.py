#!/usr/bin/env python3
"""
atacante.py - RED TEAM contra MI PROPIA Fortaleza (http://localhost:8000).
Prueba tecnicas de evasion del WAF/lapa para encontrar huecos y despues
taparlos (purple team). Uso exclusivo sobre el laboratorio propio.

Uso: arranca la Fortaleza (python3 app.py) y luego:  python3 atacante.py
"""
import urllib.request, urllib.parse, urllib.error

URL = "http://localhost:8000"

# CANDADO ETICO: esta herramienta SOLO ataca el laboratorio propio (localhost).
# Auditar un sistema ajeno sin permiso por escrito es delito.
from urllib.parse import urlparse as _up
if _up(URL).hostname not in ("localhost", "127.0.0.1", "::1"):
    raise SystemExit("Solo para el laboratorio local (localhost). Abortado.")

def pedir(path, headers=None):
    req = urllib.request.Request(URL + path, headers={"User-Agent": "curl/8"} | (headers or {}))
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"err:{e}"

def q(payload):
    return "/?q=" + urllib.parse.quote(payload)

def prueba(nombre, status):
    evadio = (status == 200)              # 200 = paso sin que el WAF lo cortara
    marca = "EVADIO  <<<" if evadio else "bloqueado"
    print(f"  [{status}] {nombre:<48} -> {marca}")
    return evadio

def main():
    print(f"\n=== RED TEAM contra la Fortaleza ({URL}) ===\n")
    print("-- Evasion de firma del WAF (SQLi) --")
    prueba("A) ' OR 1=1--            (payload clasico)", pedir(q("' OR 1=1--")))
    prueba("B) ' OR 2=2--            (cambio el numero)", pedir(q("' OR 2=2-- -")))
    prueba("C) UNION/**/SELECT       (comentario en vez de espacio)", pedir(q("1 UNION/**/SELECT password FROM users")))
    prueba("D) uNiOn  SeLeCt         (mayus/minus + espacios)", pedir(q("1 uNiOn   SeLeCt password FROM users")))
    prueba("E) 1 || 1=1              (OR con ||)", pedir(q("1 || 1=1")))

    print("\n-- Evasion del scanner-detector (User-Agent) --")
    prueba("F) sqlmap con UA normal  (--random-agent)", pedir(q("x' AND 1=1"), {"User-Agent": "Mozilla/5.0"}))

    print("\n-- Evasion de la LAPA (rate-limit / baneo por IP) --")
    print("   Rotando X-Forwarded-For para que cada peticion parezca otra IP:")
    baneos = 0
    for i in range(8):
        s = pedir("/.env", {"X-Forwarded-For": f"10.0.0.{i}"})   # honeytoken, deberia sumar strike
        if s == 403:
            baneos += 1
    print(f"   -> peticiones bloqueadas por baneo: {baneos}/8",
          "(si 0, EVADIO: nunca acumula strikes en una sola IP) <<<" if baneos == 0 else "")

if __name__ == "__main__":
    main()
