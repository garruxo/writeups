#!/usr/bin/env python3
"""
Red team de SESION contra MI Fortaleza local (http://localhost:8000).
Prueba: escalada de privilegios, token forjado, fijacion, hijacking,
invalidacion por logout y flags de la cookie. Solo laboratorio propio.
"""
import urllib.request as U, urllib.error, re
from urllib.parse import urlencode, urlparse

URL = "http://localhost:8000"
if urlparse(URL).hostname not in ("localhost", "127.0.0.1", "::1"):
    raise SystemExit("Solo laboratorio local. Abortado.")

def login(email, pw, cookie_previa=None):
    h = {"User-Agent": "curl/8"}
    if cookie_previa:
        h["Cookie"] = f"session={cookie_previa}"
    r = U.urlopen(U.Request(URL + "/login",
        data=urlencode({"email": email, "password": pw}).encode(), headers=h))
    setc = r.headers.get("Set-Cookie", "")
    m = re.search(r"session=([^;]+)", setc)
    return (m.group(1) if m else None), setc

def pide(path, cookie=None, extra=None, metodo=None):
    h = {"User-Agent": "curl/8"}
    if cookie:
        # si ya trae "session=" o varios pares, se usa tal cual; si no, se prefija
        h["Cookie"] = cookie if "=" in cookie else f"session={cookie}"
    if extra:
        h.update(extra)
    try:
        return U.urlopen(U.Request(URL + path, headers=h, method=metodo), timeout=8).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"err:{e}"

def R(nombre, status, esperado, nota=""):
    ok = (status == esperado)
    marca = "AGUANTA" if ok else "FALLA <<<"
    print(f"  [{status:>3}] {nombre:<46} (esperado {esperado})  {marca}  {nota}")

print(f"\n=== RED TEAM de SESION ({URL}) ===\n")
cli, _ = login("cliente@fortaleza.lab", "Cliente-2026-Segura!")
adm, setc_adm = login("daniel@fortaleza.lab", "Pa$$w0rd-Fuerte-2026!")

print("-- Escalada de privilegios --")
R("A) cliente -> /admin directo", pide("/admin", cli), 403)
R("B) cliente + cabecera X-Role: admin", pide("/admin", cli, {"X-Role": "admin"}), 403)
R("C) cliente + ?rol=admin en la URL", pide("/admin?rol=admin", cli), 403)
R("D) cliente + cookie extra rol=admin", pide("/admin", f"session={cli}; rol=admin"), 403)

print("\n-- Token forjado / fuerza bruta de token --")
R("E) token inventado", pide("/admin", "xxxxFORJADOxxxx"), 401)

print("\n-- Fijacion de sesion --")
fij, _ = login("daniel@fortaleza.lab", "Pa$$w0rd-Fuerte-2026!", cookie_previa="FIJADO-POR-ATACANTE")
R("F) token fijado por el atacante", pide("/admin", "FIJADO-POR-ATACANTE"), 401,
  "(el servidor emite token nuevo)")

print("\n-- Robo de sesion (hijacking) --")
R("G) cookie admin robada reutilizada", pide("/admin", adm), 200,
  "<- INHERENTE: quien roba el token entra")
print(f"     ¿cookie protegida? HttpOnly={'HttpOnly' in setc_adm}  SameSite={'SameSite' in setc_adm}")

print("\n-- Invalidacion por logout --")
pide("/logout", adm, metodo="POST")
R("H) cookie admin tras logout", pide("/admin", adm), 401, "(logout la invalida)")
