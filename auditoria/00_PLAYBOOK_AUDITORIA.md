# 🧭 Playbook de Auditoría Web — pasos fijos (memoriza esto)

> La idea: **siempre las mismas 7 fases, en el mismo orden**. Si repites este
> ciclo en cada auditoría, se te queda el concepto. Cada fase tiene su "qué hago"
> y su "qué apunto" (lo que luego va al informe).

```
1. Alcance  →  2. Reconocimiento  →  3. Escaneo/Enum  →  4. Vulns  →
5. Explotación  →  6. Post-explotación  →  7. Informe (ejec + técnico)
```

---

## Fase 1 · Alcance y reglas
**Qué hago:** defino QUÉ puedo tocar (IP/dominio), qué NO, y cuándo. Confirmo **autorización**.
**Qué apunto:** objetivo, IPs/URLs en alcance, exclusiones, fechas.
> ⚖️ Sin autorización escrita no se toca nada. Siempre.

## Fase 2 · Reconocimiento
**Qué hago:** recojo información del objetivo sin "hacer ruido".
- Web: tecnologías (Wappalyzer), `robots.txt`, cabeceras, subdominios.
- Red: rango, hosts vivos (`ping`, `arp-scan`).
**Qué apunto:** tecnologías detectadas, versiones, superficie visible.
```bash
whatweb http://OBJETIVO
curl -sI http://OBJETIVO           # cabeceras
```

## Fase 3 · Escaneo y enumeración
**Qué hago:** descubro puertos, servicios y versiones; enumero cada servicio.
```bash
nmap -sC -sV -oN nmap_inicial.txt OBJETIVO       # puertos + scripts + versiones
nmap -p- --min-rate 5000 -oN nmap_full.txt OBJETIVO   # todos los puertos
# Web:
gobuster dir -u http://OBJETIVO -w /usr/share/wordlists/dirb/common.txt
nikto -h http://OBJETIVO
```
**Qué apunto:** puertos abiertos, servicio+versión de cada uno, rutas encontradas.

## Fase 4 · Análisis de vulnerabilidades
**Qué hago:** por cada servicio/entrada, pienso "¿qué puede fallar aquí?".
- Web: SQLi, XSS, IDOR, LFI/path traversal, upload, auth débil, CSRF, SSRF…
- Versiones viejas → busco CVEs (`searchsploit SERVICIO VERSION`).
**Qué apunto:** vulnerabilidades candidatas y dónde.

## Fase 5 · Explotación
**Qué hago:** confirmo cada vuln con una **prueba de concepto (PoC)** controlada.
**Qué apunto (clave para el informe):**
- El **payload/comando exacto**.
- La **captura** de la prueba (el "Congratulations", el dato robado, el shell…).
- Qué conseguí (datos, acceso, nivel).

## Fase 6 · Post-explotación
**Qué hago (si procede y está en alcance):** escalada de privilegios, pivotar, ver alcance del daño. **Sin romper nada.**
**Qué apunto:** hasta dónde se podría llegar (impacto real).

## Fase 7 · Informe
**Qué hago:** relleno las 2 plantillas:
- **Ejecutivo** (`plantilla_informe_ejecutivo.md`): para dirección, sin tecnicismos, riesgo e impacto de negocio.
- **Técnico** (`plantilla_informe_tecnico.md`): por hallazgo → severidad **CVSS**, PoC, evidencia, **remediación**.

**Severidad rápida (CVSS orientativo):**
| | CVSS | Ejemplos |
|---|---|---|
| 🔴 Crítica | 9.0–10 | RCE, SQLi con volcado total, auth bypass |
| 🟠 Alta | 7.0–8.9 | SQLi ciega, LFI, bypass de WAF |
| 🟡 Media | 4.0–6.9 | XSS, IDOR puntual, info disclosure |
| 🟢 Baja | 0.1–3.9 | Cabeceras ausentes, versiones expuestas |

---

## ✅ Checklist de una tirada (para marcar en cada auditoría)
- [ ] 1. Alcance y autorización confirmados
- [ ] 2. Reconocimiento (tecnologías/cabeceras)
- [ ] 3. `nmap` completo + enumeración web (gobuster/nikto)
- [ ] 4. Lista de vulns candidatas
- [ ] 5. Explotación con PoC + **capturas**
- [ ] 6. Post-explotación / impacto
- [ ] 7. Informe ejecutivo + técnico rellenados

> Repite este checklist en CADA auditoría. Cuando lo hagas sin mirar, el concepto ya es tuyo. 💪
