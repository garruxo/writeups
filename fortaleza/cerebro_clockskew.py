#!/usr/bin/env python3
"""
Cerebro v2 - Cazador de clock skew (por conexion).
Mide la deriva del reloj fisico de cada maquina a partir de los TCP
timestamps, analizando CADA conexion (tcp.stream) por separado.

Por que por conexion: Linux (kernel >=4.10) aleatoriza el offset del
TCP timestamp en cada conexion nueva -> juntar muchas conexiones da una
recta imposible. Pero el offset solo cambia el ARRANQUE, no la PENDIENTE:
dentro de UNA conexion el reloj sigue siendo lineal. Por eso medimos por
stream y luego agrupamos por IP (la pendiente/skew es la huella).

Uso:
    python3 cerebro_clockskew.py captura.pcap

Requiere: tshark. Para un skew fiable hace falta UNA conexion larga
(>=60s, mejor 120s) con muchos paquetes: usa el endpoint /stream.
Honesto: NO funciona con Tor (ves el nodo de salida) ni con
tcp_timestamps=0. En loopback el skew sale ~0 (misma maquina).
"""
import subprocess, sys
from collections import defaultdict

MIN_PAQ, MIN_SPAN = 30, 20.0   # una conexion sirve si tiene >=30 paq y >=20s

def extraer(pcap):
    """(tcp.stream, ip.src) -> [(tiempo, tsval), ...]"""
    out = subprocess.run(
        ["tshark", "-r", pcap, "-Y", "tcp.options.timestamp.tsval",
         "-T", "fields", "-e", "tcp.stream", "-e", "ip.src",
         "-e", "frame.time_epoch", "-e", "tcp.options.timestamp.tsval"],
        capture_output=True, text=True)
    datos = defaultdict(list)
    for linea in out.stdout.splitlines():
        p = linea.split("\t")
        if len(p) == 4 and all(p):
            try:
                datos[(p[0], p[1])].append((float(p[2]), int(p[3])))
            except ValueError:
                pass
    return datos

def regresion(puntos):
    """Ajuste lineal tsval = a*t + b. 'a' = ticks/seg del reloj."""
    pts = sorted(puntos)
    n = len(pts)
    span = pts[-1][0] - pts[0][0]
    if n < MIN_PAQ or span < MIN_SPAN:
        return None
    t0 = pts[0][0]
    xs = [t - t0 for t, _ in pts]
    ys = [float(v) for _, v in pts]
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    b = my - a * mx
    err = (sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys)) / n) ** 0.5
    return a, err, n, span

def huella_hz(a):
    for nominal in (1000, 250, 100, 10):
        if abs(a - nominal) / nominal < 0.05:
            return nominal, (a - nominal) / nominal * 1e6
    return None, None

def mediana(xs):
    s = sorted(xs); m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2

def main():
    if len(sys.argv) != 2:
        print("uso: python3 cerebro_clockskew.py captura.pcap"); sys.exit(1)
    datos = extraer(sys.argv[1])
    if not datos:
        print("Sin TCP timestamps en la captura (¿Tor o tcp_timestamps=0?).")
        return

    print(f"\n{'conexion':>8} {'IP origen':<18} {'Hz~':>6} {'skew(ppm)':>10} {'ajuste':>8} {'paq':>5} {'dur(s)':>7}")
    print("-" * 70)
    por_ip = defaultdict(list)
    validas = 0
    for (stream, ip), pts in sorted(datos.items(), key=lambda kv: int(kv[0][0])):
        r = regresion(pts)
        if not r:
            continue
        a, err, n, span = r
        nominal, ppm = huella_hz(a)
        if ppm is None:
            continue
        validas += 1
        print(f"{stream:>8} {ip:<18} {nominal:>6} {ppm:>+10.1f} {err:>8.3f} {n:>5} {span:>7.1f}")
        por_ip[ip].append(ppm)

    if not validas:
        print("(ninguna conexion suficientemente larga: usa /stream, >=60s)")
        return

    print(f"\n=== Huella por maquina (mediana del skew de sus conexiones) ===")
    huellas = []
    for ip, ppms in sorted(por_ip.items()):
        med = mediana(ppms)
        print(f"  {ip:<18} -> {med:+.1f} ppm   ({len(ppms)} conexiones)")
        huellas.append((ip, round(med, 1)))

    for i in range(len(huellas)):
        for j in range(i + 1, len(huellas)):
            ip1, p1 = huellas[i]; ip2, p2 = huellas[j]
            if abs(p1 - p2) < 2.0:
                print(f"\n⚠️  {ip1} y {ip2} -> MISMO reloj ({p1} vs {p2} ppm). "
                      f"Probable MISMA maquina cambiando de IP.")

if __name__ == "__main__":
    main()
