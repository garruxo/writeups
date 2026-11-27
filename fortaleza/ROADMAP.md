# La Fortaleza — Roadmap

Laboratorio de **defensa activa** (legal, dentro del propio perímetro) para portfolio.

## Capas base
- [x] **Capa 1 · Muro** — web blindada (`app.py`): SQL parametrizado, scrypt, headers, rate-limit, honeytoken.
- [x] **Capa 2 · Ojos** — logging de seguridad + WAF que inspecciona y caza (SQLi/XSS/traversal/scanners).
- [x] **Capa 3 · Lapa (en la app)** — auto-baneo del IP intruso: 3 strikes -> 403 + tarpit 2s. Baneo en el perimetro = legal.
  - [x] **Nivel OS: fail2ban -> iptables** — al EXPULSAR, banea la IP en el
    cortafuegos en TODOS los puertos (toda la maquina), 24h. Filtro+jail en
    `fail2ban/`, instalador `instalar_fail2ban.sh`. Regex verificado.
- [x] **Capa 4 · Trampa** — honeytoken (cebos que nadie legitimo toca; tocarlos = strike directo).
- [x] **Cerebro v1** — clock skew por conexion (`cerebro_clockskew.py`): huella del reloj fisico.
- [x] **Panel** — `fortaleza.sh`: control interactivo con menu.
- [x] **Sesion real** — login emite token opaco (cookie HttpOnly+SameSite), zona
  `/admin` protegida por rol en el servidor. Abre ensayos de escalada de
  privilegios, robo/fijacion de sesion, IDOR.
- [x] **Limite anti-DoS** en `/stream` (MAX_STREAMS concurrentes).
- [x] **Cerebro IA** — detector de anomalias (`cerebro_ia.py`): IsolationForest +
  novedad de rango + z-score. Caza ataques novedosos que la regex NO ve
  (6/6 en prueba, 0 falsos positivos). Integrado como 4a capa del WAF.
- [x] **CSRF token** y candado etico (solo-localhost) en los atacantes.
- [x] **Tercer cerebro ("no me fio de ti")** — expediente por IP con sospecha
  ponderada; al cruzar el umbral EXPULSA al intruso. `/api/ataques` (JSON).
- [x] **Mapa de ataques en vivo** (`dashboard.html` en `/mapa`) — panel SOC con
  expedientes, barras de sospecha, badges de frontera y mapamundi.
- [x] **Cuarta capa "Extranjeria"** — al expulsar, investiga el ORIGEN (subred);
  si reincide, CIERRA LA FRONTERA a toda la subred (no vuelve ni cambiando de
  IP). No se cierran fronteras a la LAN propia (IPs privadas exentas).
- [x] **Panel con subcarpetas** (`fortaleza.sh`): Control / Analisis / IA /
  Produccion. Sin comandos que recordar.

## Produccion (nivel experto) — ver PRODUCCION.md
- [x] **Estado compartido** (`almacen.py`): Redis o memoria (fallback). Sesiones,
  expedientes, rate-limit y contador de streams movidos al almacen.
- [x] **gunicorn** (`gunicorn_conf.py`): varios workers, gthread para `/stream`.
- [x] **HTTPS/TLS** probado (cookie `Secure`); **nginx** como proxy inverso
  (`nginx-fortaleza.conf`) con IP real del cliente (XFF de confianza).
- [x] **Despliegue en 1 comando** (`desplegar.sh`).
- [ ] Verificar el backend Redis en Kali (arrancar con `REDIS_URL`).
- [x] **IA entrenada y evaluada** (train/test): Recall 91.4%, FP 0.0%,
  Precision 100%, F1 95.5% sobre datos no vistos (`python3 cerebro_ia.py`).

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
