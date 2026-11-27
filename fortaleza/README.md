# 🏰 La Fortaleza — Laboratorio de Defensa Activa

> Una web deliberadamente **blindada** y el sistema que la **detecta, la defiende y responde** a los ataques — en entorno seguro y legal. Proyecto de aprendizaje y demostración de habilidades en seguridad defensiva (blue team).

**Autor:** Daniel Garrucho García · **Perfil:** Pentester junior / Blue team en formación

---

## La idea

No existe el sistema *"impenetrable"* — todo deja rastro y toda defensa tiene límites. El objetivo profesional real no es la perfección, es la **resiliencia**:

> **Aguantar lo conocido · Detectar lo desconocido · Responder solo.**

La Fortaleza demuestra, con código que funciona, que entiendo cómo se construye esa resiliencia capa a capa — y cómo se **ataca** cada capa para comprobar que aguanta.

---

## Qué demuestra (habilidades)

| Capa | Qué hace | Habilidad que demuestra |
|---|---|---|
| 🧱 **Muro** | Web con SQL parametrizado, hashing scrypt, cabeceras de seguridad, validación de entrada y rate-limit | Desarrollo seguro (OWASP Top 10) |
| 👁️ **Ojos** | WAF que inspecciona cada petición (SQLi, XSS, path traversal) y detecta herramientas de ataque por su User-Agent | Detección de intrusiones, firmas |
| 🦀 **Lapa** | Auto-baneo del IP intruso: 3 strikes → `403` + *tarpit*. Baneo dentro del propio perímetro (legal) | Respuesta automática / defensa activa |
| 🪤 **Trampa** | *Honeytokens*: cebos que ningún usuario legítimo toca; tocarlos delata al intruso al instante | Deception / detección temprana |
| 🧠 **Cerebro** | Mide el *clock skew* (deriva del reloj físico vía TCP timestamps) para reconocer una máquina aunque cambie de IP | Análisis forense de red, fingerprinting |

Todo se maneja desde un **panel de control interactivo** (`fortaleza.sh`).

---

## Cómo probarlo

```bash
python3 app.py            # arranca la web blindada (127.0.0.1:8000)
# o, con menú:
bash fortaleza.sh
```

Desde el panel: **1** arranca · **4** ataca y ves el muro rebotar · repite **4** y la lapa **te banea** · **6** muestra el log de intrusos · **5** mide el *clock skew*.

---

## Resultados reales (comprobados)

- **SQLi `' OR 1=1--`** en el login → rechazado (consulta parametrizada + WAF).
- **Fuerza bruta** → cortada al 4.º intento (rate-limit).
- **3 ataques seguidos** → IP **baneada** 120 s con *tarpit* de 2 s; hasta sus peticiones legítimas caen.
- **Scanner (sqlmap/nikto)** → bloqueado por User-Agent.
- **Clock skew** → mide la huella del reloj físico por conexión, resistiendo incluso la aleatorización de *offset* que Linux aplica como contramedida.

Cada acción del intruso queda registrada en un log de seguridad pensado para alimentar un IDS/fail2ban a nivel de sistema.

---

## Decisiones de diseño honestas

- **Baneo dentro del perímetro, nunca "hack back".** Contraatacar a la máquina del atacante es el mismo delito que él comete. La lapa cierra *mi* puerta y lo marca; nunca toca su equipo.
- **Límites reconocidos.** El *clock skew* no funciona contra Tor ni con `tcp_timestamps=0`; el baneo vive en memoria. Un buen profesional **conoce y documenta** los límites de sus defensas.
- **No es un producto de seguridad para producción.** Es un laboratorio y una demostración; en un cliente real se despliegan herramientas probadas (ModSecurity, fail2ban, Wazuh…). Lo que este proyecto demuestra es que **sé cómo y por qué funcionan**.

---

## Contexto del portfolio

Este laboratorio acompaña a mis **auditorías completas** (informes ejecutivo, técnico y forense) y mis **referencias de SQLi y XSS**, en este mismo repositorio.

---

<sub>⚠️ Proyecto educativo. Todas las pruebas se realizan en laboratorio aislado y autorizado, sobre sistemas propios.</sub>
