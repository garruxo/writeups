# La Fortaleza — Roadmap

Laboratorio de **defensa activa** (legal, dentro del propio perímetro) para portfolio.

## Capas base
- [x] **Capa 1 · Muro** — web blindada (`app.py`): SQL parametrizado, scrypt, headers, rate-limit, honeytoken.
- [x] **Capa 2 · Ojos** — logging de seguridad + WAF que inspecciona y caza (SQLi/XSS/traversal/scanners).
- [x] **Capa 3 · Lapa (en la app)** — auto-baneo del IP intruso: 3 strikes -> 403 + tarpit 2s. Baneo en el perimetro = legal.
  - [ ] Nivel OS: fail2ban lee el log y banea en el firewall (iptables).
- [x] **Capa 4 · Trampa** — honeytoken (cebos que nadie legitimo toca; tocarlos = strike directo).
- [x] **Cerebro v1** — clock skew por conexion (`cerebro_clockskew.py`): huella del reloj fisico.
- [x] **Panel** — `fortaleza.sh`: control interactivo con menu.

> Nota lab: el baneo es en memoria. Si te baneas a ti mismo probando,
> reinicia (panel: 3 Parar -> 1 Arrancar) y se limpia.

## Proyecto "Simbionte" (sistema inmune — encadenar las capas)
- [ ] 🌀 **Laberinto** — tarpit: endpoints falsos infinitos para scanners/bots.
- [ ] 🦀 **Espejismo** — BD falsa con balizas; el dato robado delata al ladron al USARSE (downstream).
- [ ] 🧠 **Cerebro** — fingerprint del atacante (sobrevive al cambio de IP).
- [ ] 🛰️ **Centinela** — DFIR automatico: captura + IOCs + informe forense sellado.

## Reto abierto: "Cazador de Expertos"
Los expertos atacan desde **MV aislada + VPN/Tor** -> no se desenmascaran en caliente.
Contra expertos el objetivo CAMBIA: de *identificar* a **caracterizar + negar + inteligencia TTP**.
Señales que sobreviven a la MV/VPN (a investigar y medir):
- **Clock skew** (deriva del reloj via TCP timestamps) -> delata la maquina fisica aunque cambie IP.
- **JA3/JA4** (huella del handshake TLS) -> delata el toolkit.
- **Tempo/comportamiento** -> ritmo, orden de herramientas, zona horaria real.
Verdad honesta: un experto disciplinado vence casi todas las trampas.
Los expertos caen por **errores de OPSEC a lo largo del tiempo**, no por una trampa genial.
