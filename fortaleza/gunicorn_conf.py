# Configuracion de gunicorn para La Fortaleza (servidor WSGI de produccion).
# Arranque (con Redis):
#   REDIS_URL=redis://localhost:6379/0 gunicorn -c gunicorn_conf.py app:app
bind = "127.0.0.1:8000"     # nginx hace de proxy TLS delante (o usa --certfile en lab)
workers = 4                 # varios procesos -> el estado DEBE ser compartido (Redis)
threads = 2
worker_class = "gthread"    # hilos: necesarios para /stream (conexiones largas)
timeout = 180               # margen para /stream
preload_app = True          # carga la app (y el modelo IA) una vez y hace fork
accesslog = "-"
errorlog = "-"
