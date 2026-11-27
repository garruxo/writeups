#!/usr/bin/env python3
"""
La Fortaleza - Capa 1 (el muro) + ganchos para la Capa 3/4 (lapa y trampa).
Web deliberadamente BLINDADA para practicar defensa en entorno seguro.
Autor: Daniel Garrucho Garcia
Dependencias: solo Flask.  Hashing: hashlib.scrypt (libreria estandar).
"""
import hashlib, hmac, os, sqlite3, time, logging, re
from collections import defaultdict
from urllib.parse import unquote_plus
from flask import Flask, request, jsonify, Response, g

APP_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(APP_DIR, "fortaleza.db")
LOG_PATH = os.path.join(APP_DIR, "fortaleza_seguridad.log")

app = Flask(__name__)

# ---- Log de seguridad (lo lee fail2ban en la Capa 3) --------------------
# Logger propio y aislado: SOLO lineas SECURITY, sin ruido de Flask.
sec = logging.getLogger("fortaleza")
sec.setLevel(logging.INFO)
sec.propagate = False
_h = logging.FileHandler(LOG_PATH)
_h.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
sec.addHandler(_h)

def alerta(motivo, extra=""):
    """Escribe una linea que fail2ban sabra parsear: ... ip=<IP> ..."""
    ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
    sec.info(f"SECURITY intruso ip={ip} motivo={motivo} path={request.path} {extra}".strip())

# ---- Hashing fuerte (scrypt, con sal por usuario) -----------------------
def hash_pw(password, salt=None):
    salt = salt or os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return salt.hex() + "$" + h.hex()

def verify_pw(password, stored):
    try:
        salt_hex, h_hex = stored.split("$")
        calc = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex),
                              n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(calc.hex(), h_hex)   # comparacion en tiempo constante
    except Exception:
        return False

# ---- Base de datos (consultas SIEMPRE parametrizadas) -------------------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE, pw TEXT)")
    if not con.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        con.execute("INSERT INTO users(email,pw) VALUES(?,?)",
                    ("daniel@fortaleza.lab", hash_pw("Pa$$w0rd-Fuerte-2026!")))
    con.commit(); con.close()

# ---- Rate limiting por IP (frena el fuerza bruta) -----------------------
intentos = defaultdict(list)   # ip -> [timestamps]
MAX_INTENTOS, VENTANA = 5, 60  # 5 intentos por minuto

def rate_limited(ip):
    ahora = time.time()
    intentos[ip] = [t for t in intentos[ip] if ahora - t < VENTANA]
    intentos[ip].append(ahora)
    return len(intentos[ip]) > MAX_INTENTOS

# ---- WAF + Lapa (auto-baneo del IP intruso) -----------------------------
# Inspecciona cada peticion. Al intruso que insiste, le corta el acceso solo
# (403 + tarpit). Baneo EN LA APP = dentro de nuestro perimetro = legal.
def normaliza(s):
    """Desarma la ofuscacion ANTES de inspeccionar: minusculas, quita
    comentarios /* */ y colapsa espacios. Asi UNION/**/SELECT y uNiOn  SeLeCt
    acaban siendo lo mismo: 'union select'. (La misma idea del forense.)"""
    s = s.lower()
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)   # comentarios -> espacio
    s = re.sub(r"\s+", " ", s)                       # colapsa espacios/tabs/saltos
    return s

WAF = [
    ("sqli", re.compile(
        r"union\s+select"                       # volcado
        r"|\b(or|and)\s+\d+\s*=\s*\d+"          # or 1=1, and 2=2...
        r"|\b(or|and)\s+'[^']*'\s*=\s*'"        # or 'a'='a'
        r"|\|\|\s*\d"                            # 1 || 1=1
        r"|sleep\s*\(|pg_sleep|benchmark\s*\(|waitfor\s+delay"  # time-based
        r"|information_schema|\bfrom\s+users\b")),  # enumeracion
    ("xss",  re.compile(r"<script|onerror\s*=|onload\s*=|javascript:|<svg|<img[^>]+src")),
    ("traversal", re.compile(r"\.\./|\.\.\\|/etc/passwd|/etc/shadow")),
]
SCANNERS = re.compile(r"sqlmap|nikto|nmap|dirbuster|gobuster|masscan|hydra|wpscan|acunetix|nuclei", re.I)
STRIKES = defaultdict(int)   # ip -> nº de acciones sospechosas
BANS = {}                    # ip -> epoch hasta cuando esta baneado
LIMITE_STRIKES, BAN_SEG = 3, 120

def _ip():
    # Identidad = IP REAL de la conexion TCP (request.remote_addr).
    # NO se usa X-Forwarded-For: lo pone el cliente y se falsea para
    # evadir el baneo. En produccion tras un proxy de confianza, se
    # confiaria en XFF solo si remote_addr es ese proxy conocido.
    return request.remote_addr or "desconocido"

def strike(motivo, extra=""):
    """Suma un strike al IP y, al llegar al limite, lo banea (la lapa)."""
    ip = _ip()
    STRIKES[ip] += 1
    alerta(motivo, extra)
    if STRIKES[ip] >= LIMITE_STRIKES and ip not in BANS:
        BANS[ip] = time.time() + BAN_SEG
        alerta("BANEADO", f"strikes={STRIKES[ip]} durante={BAN_SEG}s")

@app.before_request
def guardia():
    ip = _ip()
    # 1) ¿ya baneado? -> tarpit (lo pega) + 403
    if ip in BANS:
        if time.time() < BANS[ip]:
            time.sleep(2)
            return jsonify(error="IP bloqueada"), 403
        del BANS[ip]; STRIKES[ip] = 0          # expira el baneo
    # 2) herramienta de ataque por el User-Agent
    ua = request.headers.get("User-Agent", "")
    if SCANNERS.search(ua):
        strike("scanner", f"ua={ua[:40]!r}")
        return jsonify(error="Peticion rechazada"), 403
    # 3) firma de ataque en ruta + query + cuerpo (DECODIFICA %20 y NORMALIZA)
    objetivo = request.path + " " + unquote_plus(request.query_string.decode("latin1", "ignore"))
    try:
        objetivo += " " + unquote_plus(request.get_data(as_text=True)[:8000])
    except Exception:
        pass
    objetivo = normaliza(objetivo)             # desarma la ofuscacion
    for nombre, rx in WAF:
        if rx.search(objetivo):
            strike(f"waf_{nombre}", f"patron en {request.path}")
            return jsonify(error="Peticion rechazada por el WAF"), 403

# ---- Validacion de entrada ----------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}$")

# ---- Cabeceras de seguridad en TODAS las respuestas ---------------------
@app.after_request
def cabeceras(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    resp.headers.pop("Server", None)
    return resp

# ---- Rutas --------------------------------------------------------------
@app.route("/")
def home():
    return Response(
        "<!doctype html><meta charset=utf-8><title>La Fortaleza</title>"
        "<h1>🏰 La Fortaleza</h1><p>Web blindada. Intenta entrar.</p>"
        "<form method=post action=/login>"
        "email <input name=email> clave <input name=password type=password>"
        "<button>Entrar</button></form>", mimetype="text/html")

@app.route("/stream")
def stream():
    """Conexion larga para medir clock skew: manda un chunk cada 0.2s ~120s.
    Una sola conexion TCP -> tsval lineal -> skew medible (el offset aleatorio
    de Linux solo cambia el arranque, no la pendiente)."""
    def gen():
        for _ in range(600):
            yield "keepalive\n"
            time.sleep(0.2)
    return Response(gen(), mimetype="text/plain")

@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr
    if rate_limited(ip):
        alerta("rate_limit")                       # demasiados intentos -> sospechoso
        return jsonify(error="Demasiados intentos. Espera."), 429

    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    if not EMAIL_RE.match(email):                  # validacion: ni intento con basura
        alerta("entrada_invalida", f"email={email[:40]!r}")
        return jsonify(error="Datos invalidos"), 400

    # Consulta PARAMETRIZADA: el ' OR 1=1-- es solo texto, no rompe nada.
    row = db().execute("SELECT pw FROM users WHERE email = ?", (email,)).fetchone()

    if row and verify_pw(password, row["pw"]):
        return jsonify(ok=True, msg="Bienvenido, Daniel")
    alerta("login_fallido", f"email={email!r}")    # <- fail2ban cuenta estos
    return jsonify(error="Credenciales incorrectas"), 401

# ---- TRAMPA (Capa 4): cebos que nadie legitimo toca jamas ----------------
TRAMPAS = ["/.env", "/wp-login.php", "/admin.php", "/backup.sql",
           "/phpmyadmin", "/.git/config", "/config.php.bak"]

@app.route("/<path:ruta>")
def honeytoken(ruta):
    p = "/" + ruta
    if p in TRAMPAS:
        strike("honeytoken", f"cebo={p}")          # tocar esto = intruso 100% seguro (suma strike)
        return jsonify(error="Not found"), 404      # le respondemos normal, pero ya esta marcado
    return jsonify(error="Not found"), 404

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=8000, threaded=True)
