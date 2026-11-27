#!/usr/bin/env python3
"""
Red team CSRF contra MI Fortaleza local. Levanta un sitio "atacante" en OTRO
origen (127.0.0.1:9000) que auto-envia un POST cruzado a /logout, y comprueba
si SameSite frena el ataque. Navegador real (Chromium). Solo laboratorio propio.
"""
import threading, http.server, socketserver
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

FORT = "http://localhost:8000"       # victima
EVIL = "http://127.0.0.1:9000"       # atacante (otro 'site')
if urlparse(FORT).hostname not in ("localhost", "127.0.0.1", "::1"):
    raise SystemExit("Solo laboratorio local. Abortado.")

PAGINA = b"""<!doctype html><title>pagina atacante</title>
<h1>Gatitos gratis</h1>
<form id=f method=POST action="http://localhost:8000/logout"></form>
<script>document.getElementById('f').submit()</script>"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","text/html")
        self.end_headers(); self.wfile.write(PAGINA)
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 9000), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

def admin_status(pg):
    return pg.goto(FORT + "/admin").status

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    # 1) login real de la victima (guarda el token CSRF que entrega el servidor)
    pg.goto(FORT + "/")
    datos = pg.evaluate("""async()=>{
        const r=await fetch('/login',{method:'POST',
          headers:{'Content-Type':'application/x-www-form-urlencoded'},
          body:'email=daniel@fortaleza.lab&password=Pa$$w0rd-Fuerte-2026!'});
        return await r.json();}""")
    csrf = datos.get("csrf")
    print(f"  login victima ok={datos.get('ok')}  (csrf recibido: {bool(csrf)})")
    print(f"  sesion activa? /admin -> {admin_status(pg)}  (200 = dentro)")

    # 2) ATAQUE CSRF: la web atacante (otro origen) fuerza logout con un <form>
    #    (un form NO puede poner la cabecera X-CSRF-Token)
    pg.goto(EVIL + "/"); pg.wait_for_timeout(800)
    tras = admin_status(pg)
    print(f"\n  tras visitar la web atacante -> /admin -> {tras}  "
          f"{'BLOQUEADO (sesion intacta)' if tras==200 else 'CSRF FUNCIONO <<<'}")

    # 3) control: logout legitimo desde el propio sitio CON el token CSRF -> SI funciona
    pg.goto(FORT + "/")
    pg.evaluate(f"""async()=>{{await fetch('/logout',{{method:'POST',
        headers:{{'X-CSRF-Token':'{csrf}'}}}});}}""")
    print(f"\n  control: logout propio CON token -> /admin -> {admin_status(pg)}  "
          f"(401 = el endpoint legitimo SI funciona)")
    b.close()
srv.shutdown()
