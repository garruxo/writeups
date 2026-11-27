# La Fortaleza — Roadmap

Laboratorio de **defensa activa** (legal, dentro del propio perímetro) para portfolio.

## Capas base
- [x] **Capa 1 · Muro** — web blindada (`app.py`): SQL parametrizado, scrypt, headers, rate-limit, honeytoken.
- [ ] **Capa 2 · Ojos** — IDS (Suricata) + logging que caza el ataque.
- [ ] **Capa 3 · Lapa** — fail2ban: banea solo el IP intruso (iptables).
- [ ] **Capa 4 · Trampa** — honeytoken / canarytoken propio.

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
