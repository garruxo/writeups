#!/usr/bin/env python3
"""
Cerebro - Cazador de clock skew.
Mide la deriva del reloj fisico de cada IP a partir de los TCP timestamps
de una captura. Dos IPs distintas con el MISMO skew = la MISMA maquina
(p. ej. un atacante que cambia de IP por VPN).

Uso:
    sudo tcpdump -i any -s 0 -w captura.pcap tcp port 8000   # capturar
    python3 cerebro_clockskew.py captura.pcap

Requiere: tshark (Wireshark CLI). Solo lectura de la captura.
IMPORTANTE: captura >=2 min. Con menos, la cuantizacion del tsval se come
las derivas finas (30s -> error enorme; 120s -> ya fiable). Medido y validado.
Honesto: NO funciona si el atacante usa Tor (ves el reloj del nodo de
salida) o apaga los TCP timestamps (tcp_timestamps=0).
"""
import subprocess, sys
from collections import defaultdict

def extraer(pcap):
    """Saca (ip_origen, tiempo_captura, tsval) de cada paquete con timestamp."""
    out = subprocess.run(
        ["tshark", "-r", pcap, "-Y", "tcp.options.timestamp.tsval",
         "-T", "fields", "-e", "ip.src",
         "-e", "frame.time_epoch", "-e", "tcp.options.timestamp.tsval"],
        capture_output=True, text=True)
    datos = defaultdict(list)
    for linea in out.stdout.splitlines():
        p = linea.split("\t")
        if len(p) == 3 and p[0] and p[1] and p[2]:
            try:
                datos[p[0]].append((float(p[1]), int(p[2])))
            except ValueError:
                pass
    return datos

def regresion(puntos):
    """Ajuste lineal tsval = a*t + b. 'a' = Hz del reloj; su deriva = la huella."""
    n = len(puntos)
    if n < 10:
        return None
    t0 = puntos[0][0]
    xs = [t - t0 for t, _ in puntos]
    ys = [float(v) for _, v in puntos]
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den   # ticks/segundo
    b = my - a * mx
    # error de ajuste (cuanto de "limpia" es la recta)
    err = (sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys)) / n) ** 0.5
    return a, b, err, n

def huella_hz(a):
    """El reloj corre a ~250/1000 Hz; estimamos el nominal y la deriva en ppm."""
    for nominal in (1000, 250, 100, 10):
        if abs(a - nominal) / nominal < 0.05:     # dentro del 5% de un nominal conocido
            ppm = (a - nominal) / nominal * 1e6
            return nominal, ppm
    return None, None

def main():
    if len(sys.argv) != 2:
        print("uso: python3 cerebro_clockskew.py captura.pcap"); sys.exit(1)
    datos = extraer(sys.argv[1])
    if not datos:
        print("Sin TCP timestamps en la captura (¿Tor o tcp_timestamps=0?).")
        return
    print(f"\n{'IP origen':<20} {'Hz~':>6} {'skew(ppm)':>10} {'ajuste':>8} {'paq':>5}")
    print("-" * 54)
    huellas = []
    for ip, pts in sorted(datos.items()):
        r = regresion(sorted(pts))
        if not r:
            print(f"{ip:<20} (pocos paquetes)"); continue
        a, b, err, n = r
        nominal, ppm = huella_hz(a)
        hz = f"{nominal}" if nominal else f"{a:.0f}?"
        ppm_s = f"{ppm:+.1f}" if ppm is not None else "  ?"
        print(f"{ip:<20} {hz:>6} {ppm_s:>10} {err:>8.2f} {n:>5}")
        if ppm is not None:
            huellas.append((ip, round(ppm, 1)))
    # comparar: IPs distintas con skew casi igual = misma maquina fisica
    print()
    for i in range(len(huellas)):
        for j in range(i + 1, len(huellas)):
            ip1, p1 = huellas[i]; ip2, p2 = huellas[j]
            if abs(p1 - p2) < 2.0:   # mismo skew dentro de 2 ppm
                print(f"⚠️  {ip1} y {ip2} -> MISMO reloj ({p1} vs {p2} ppm). "
                      f"Probable MISMA maquina cambiando de IP.")

if __name__ == "__main__":
    main()
