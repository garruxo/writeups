#!/usr/bin/env python3
"""
Cerebro SUPERVISADO de la Fortaleza.
A diferencia de cerebro_ia.py (NO supervisado: solo ve trafico normal y marca lo
raro), este SI aprende de ejemplos etiquetados de ataque y de normal. Lee el
CONTENIDO de la peticion con TF-IDF de n-gramas de caracteres y clasifica con
regresion logistica. Es el enfoque estandar para deteccion de ataques web y
suele superar de largo al no supervisado en recall.

Uso:
  python3 cerebro_super.py csic_normal.txt csic_ataques.txt
Compara su resultado con el de cerebro_ia.py sobre los MISMOS ficheros.
Requiere scikit-learn.
"""
import sys, random
from urllib.parse import unquote_plus

MUESTRA_MAX = 80000   # tope por clase para que entrene rapido

def leer(fichero):
    with open(fichero, encoding="utf-8", errors="ignore") as fh:
        return [unquote_plus(l.strip()) for l in fh if l.strip()]

def muestra(xs, n):
    if len(xs) > n:
        random.seed(1); return random.sample(xs, n)
    return xs

def main():
    if len(sys.argv) != 3:
        print("uso: python3 cerebro_super.py normal.txt ataques.txt"); return
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import recall_score, precision_score, f1_score, confusion_matrix
    except ImportError:
        print("Falta scikit-learn:  sudo apt install python3-sklearn"); return

    normal = muestra(leer(sys.argv[1]), MUESTRA_MAX)
    ataque = muestra(leer(sys.argv[2]), MUESTRA_MAX)
    if len(normal) < 20 or len(ataque) < 20:
        print("Hacen falta mas muestras."); return

    X = normal + ataque
    y = [0] * len(normal) + [1] * len(ataque)     # 0=normal, 1=ataque

    # Split 80/20 ESTRATIFICADO: el modelo no ve el test al entrenar
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=1, stratify=y)

    print(f"[SUPERVISADO]  entrenando con {len(Xtr)} (normal+ataque), "
          f"evaluando con {len(Xte)} no vistos...\n")

    # TF-IDF de n-gramas de caracteres: 'lee' la forma del texto (UNION, <script>, ../)
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4),
                          min_df=3, max_features=40000, sublinear_tf=True)
    Xtr_v = vec.fit_transform(Xtr)
    Xte_v = vec.transform(Xte)

    clf = LogisticRegression(max_iter=1000, class_weight="balanced", C=4.0)
    clf.fit(Xtr_v, ytr)
    pred = clf.predict(Xte_v)

    rec = recall_score(yte, pred)
    prec = precision_score(yte, pred)
    f1 = f1_score(yte, pred)
    tn, fp, fn, tp = confusion_matrix(yte, pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else 0

    print(f"  Recall (deteccion de ataques) : {rec*100:5.1f}%   ({tp}/{tp+fn})")
    print(f"  Falsos positivos (FP rate)    : {fpr*100:5.2f}%   ({fp}/{fp+tn})")
    print(f"  Precision                     : {prec*100:5.1f}%")
    print(f"  F1-score                      : {f1*100:5.1f}%")
    print("\n  (supervisado: aprende de ataques etiquetados y lee el contenido;")
    print("   compara con cerebro_ia.py, que es NO supervisado sobre los mismos datos.)")

if __name__ == "__main__":
    main()
