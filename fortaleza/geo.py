#!/usr/bin/env python3
"""
Geolocalizacion offline de IPs para La Fortaleza.
Imita lo que hacen CrowdSec / banip / los modulos geo de iptables: una base de
datos LOCAL (MaxMind GeoLite2 o DB-IP, formato .mmdb) en vez de una API externa.
Ventajas: funciona sin internet, sin limites de API y bajo HTTPS.

Base de datos: ruta en GEOIP_DB (por defecto ./GeoLite2-City.mmdb).
Si falta la libreria geoip2 o la base, geolocalizar() devuelve None y el mapa
sigue funcionando (solo sin situar en el mapamundi).
"""
import os, functools

RUTA_DB = os.environ.get("GEOIP_DB",
                         os.path.join(os.path.dirname(os.path.abspath(__file__)), "GeoLite2-City.mmdb"))
_reader = None   # None=sin probar, False=no disponible, objeto=listo

def _lector():
    global _reader
    if _reader is False:
        return None
    if _reader is None:
        try:
            import geoip2.database
            if os.path.exists(RUTA_DB):
                _reader = geoip2.database.Reader(RUTA_DB)
            else:
                _reader = False; return None
        except Exception:
            _reader = False; return None
    return _reader

def disponible():
    return _lector() is not None

@functools.lru_cache(maxsize=8192)
def geolocalizar(ip):
    """Devuelve {pais, pais_nombre, ciudad, lat, lon} o None."""
    r = _lector()
    if not r:
        return None
    try:
        c = r.city(ip)
        return {
            "pais": c.country.iso_code,
            "pais_nombre": c.country.name,
            "ciudad": c.city.name,
            "lat": c.location.latitude,
            "lon": c.location.longitude,
        }
    except Exception:
        return None
