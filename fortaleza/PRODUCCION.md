# La Fortaleza en producción (nivel experto)

Del servidor de desarrollo de Flask a un despliegue real: **gunicorn** (varios
workers) + **Redis** (estado compartido) + **HTTPS** (TLS).

## Por qué cambia todo con varios workers

El servidor de desarrollo es **un proceso**. En producción se usan **varios
workers** para aguantar carga. Pero entonces la memoria de cada worker es suya:

> Una sesión creada en el worker A **no existe** en el worker B.
> (Comprobado: login en :8000 → `/admin` 200; misma cookie en :8001 → **401**.)

Por eso el estado compartido (sesiones, expedientes, baneos, rate-limit, contador
de streams) se mueve a **Redis**. La Fortaleza usa `almacen.py`, que habla con
Redis si hay `REDIS_URL`, y si no, cae a memoria (desarrollo).

## Puesta en marcha (laboratorio, 1 comando)

```bash
pip install -r requirements.txt
sudo apt install redis-server && sudo service redis-server start
bash desplegar.sh          # gunicorn + Redis + TLS en https://localhost:8443
```

## Puesta en marcha real (nginx como proxy TLS)

```bash
# gunicorn escucha en claro en 127.0.0.1:8000; nginx pone el TLS delante
TRUSTED_PROXIES=127.0.0.1 REDIS_URL=redis://localhost:6379/0 \
    gunicorn -c gunicorn_conf.py app:app
# nginx: copia nginx-fortaleza.conf a /etc/nginx/sites-available/ y actívalo
```

`nginx` pasa la **IP real del cliente** en `X-Forwarded-For`; la Fortaleza solo
la cree si la conexión viene del proxy de confianza (`TRUSTED_PROXIES`), para que
nadie la falsee. Y `X-Forwarded-Proto: https` activa la cookie `Secure`.

## Piezas

| Fichero | Qué es |
|---|---|
| `almacen.py` | Estado compartido: Redis o memoria (fallback) |
| `gunicorn_conf.py` | Workers, hilos (gthread para `/stream`), preload |
| `nginx-fortaleza.conf` | Proxy inverso + TLS + IP real del cliente |
| `desplegar.sh` | Arranque en un comando (gunicorn+Redis+TLS) |
| `requirements.txt` | Dependencias |

## Verificado

- **HTTPS real:** TLS → 200; la cookie lleva `Secure; HttpOnly; SameSite=Strict`.
- **Problema multi-worker:** demostrado (sesión no compartida sin Redis).
- **Refactor del estado al almacén:** probado con backend en memoria (toda la
  funcionalidad sigue igual). El backend Redis usa llamadas estándar de
  `redis-py`; verifícalo en tu Kali arrancando con `REDIS_URL`.

## Notas honestas

- **Estado atómico (resuelto):** el expediente usa contador (`incrby`), lista de
  eventos (`lpush`) y clave de baneo con TTL -> sin lee-modifica-escribe, sin
  carreras. El `MemStore` de desarrollo va protegido con lock.
- **Mensajes y mapa (resuelto):** el muro vive en el almacen (compartido, acotado
  a 50); `/mapa` y `/api/ataques` solo desde la LAN propia o siendo admin.
- El contador de `/stream` podría descuadrarse si un worker muere a mitad de una
  conexión (caso extremo, impacto menor y autolimitado).
- El certificado es autofirmado (laboratorio). En real: Let's Encrypt.
