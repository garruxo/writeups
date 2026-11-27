#!/usr/bin/env python3
"""
Almacen de estado para la Fortaleza.
Con VARIOS workers (gunicorn), la memoria de cada proceso NO se comparte:
una sesion creada en el worker A no existe en el B. Solucion: un almacen
compartido (Redis). Este modulo da la MISMA interfaz con dos backends:
  - RedisStore: produccion (estado compartido entre workers).
  - MemStore:   desarrollo / 1 worker (en memoria).
Se elige Redis si existe REDIS_URL y responde; si no, memoria.
"""
import time, os, json

class MemStore:
    def __init__(self):
        self._kv = {}            # clave -> (valor, expira_epoch|None)
    def _vivo(self, k):
        v = self._kv.get(k)
        if not v:
            return None
        val, exp = v
        if exp and time.time() > exp:
            self._kv.pop(k, None); return None
        return val
    def get(self, k):
        return self._vivo(k)
    def set(self, k, val, ttl=None):
        self._kv[k] = (val, time.time() + ttl if ttl else None)
    def delete(self, k):
        self._kv.pop(k, None)
    def incr(self, k, ttl=None):
        cur = int(self._vivo(k) or 0) + 1
        exp = self._kv.get(k, (None, None))[1]
        if ttl and not exp:
            exp = time.time() + ttl
        self._kv[k] = (cur, exp); return cur
    def decr(self, k):
        cur = max(int(self._vivo(k) or 0) - 1, 0)
        exp = self._kv.get(k, (None, None))[1]
        self._kv[k] = (cur, exp); return cur
    def jget(self, k):
        v = self._vivo(k); return json.loads(v) if v else None
    def jset(self, k, obj, ttl=None):
        self.set(k, json.dumps(obj), ttl)
    def keys(self, prefijo):
        now = time.time()
        return [k for k, (val, exp) in list(self._kv.items())
                if k.startswith(prefijo) and (not exp or exp > now)]

class RedisStore:
    def __init__(self, cliente):
        self.r = cliente
    @staticmethod
    def _s(v):
        return v.decode() if isinstance(v, (bytes, bytearray)) else v
    def get(self, k):
        return self._s(self.r.get(k))
    def set(self, k, val, ttl=None):
        self.r.set(k, val, ex=ttl)
    def delete(self, k):
        self.r.delete(k)
    def incr(self, k, ttl=None):
        n = self.r.incr(k)
        if ttl and n == 1:
            self.r.expire(k, ttl)
        return n
    def decr(self, k):
        return max(self.r.decr(k), 0)
    def jget(self, k):
        v = self.get(k); return json.loads(v) if v else None
    def jset(self, k, obj, ttl=None):
        self.set(k, json.dumps(obj), ttl)
    def keys(self, prefijo):
        return [self._s(k) for k in self.r.scan_iter(match=prefijo + "*")]

def crear_almacen():
    """Devuelve (almacen, nombre_backend)."""
    url = os.environ.get("REDIS_URL")
    if url:
        try:
            import redis
            c = redis.from_url(url, socket_connect_timeout=2)
            c.ping()
            return RedisStore(c), "redis"
        except Exception as e:
            print(f"[almacen] Redis no disponible ({e}); uso memoria")
    return MemStore(), "memoria"
