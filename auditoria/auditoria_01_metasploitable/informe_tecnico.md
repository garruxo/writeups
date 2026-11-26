# Informe Técnico — Test de Intrusión "Servidor Interno" (Auditoría #1)

| | |
|---|---|
| **Cliente / Alcance** | ACME Corp (ficticio) — servidor interno · `IP_OBJETIVO` |
| **Sistema real** | Metasploitable 2 (laboratorio vulnerable, red host-only) |
| **Tipo de prueba** | Caja negra, sin credenciales (red interna) |
| **Metodología** | OWASP / PTES |
| **Autor** | [Tu nombre] |
| **Fecha** | 2026-11-26 · Versión 0.1 (borrador) |

> ⚠️ Laboratorio aislado host-only, máquina vulnerable a propósito, con fines educativos.

## 1. Alcance y objetivos
- **Objetivo:** identificar y explotar vulnerabilidades alcanzables en red interna sobre el host `IP_OBJETIVO`.
- **En alcance:** todos los servicios de red del host.
- **Fuera de alcance:** DoS, otros hosts de la red.

## 2. Metodología
Reconocimiento → Escaneo/Enum → Análisis de vulns → Explotación → Post-explotación → Informe.

## 3. Herramientas
| Herramienta | Uso |
|---|---|
| nmap | Escaneo de puertos/servicios/versiones |
| searchsploit | Buscar exploits por servicio+versión |
| Metasploit (msfconsole) | Explotación |
| (otras según hallazgo) | |

## 4. Reconocimiento y escaneo (Fase 2-3)

**Comando usado:**
```
nmap -sC -sV IP_OBJETIVO
```

**Salida (pegar aquí la real):**
```
[PEGAR SALIDA DE NMAP]
```

## 5. Análisis de vulnerabilidades (Fase 4) — candidatas a verificar

> Servicios típicos de este objetivo y el fallo que suele tener cada uno. Se **confirma** en la Fase 5.

| Puerto | Servicio/versión | Vulnerabilidad candidata | Severidad prev. |
|---|---|---|:---:|
| 21 | vsftpd 2.3.4 | Backdoor (CVE-2011-2523) → RCE root | 🔴 |
| 139/445 | Samba 3.0.20 | `usermap_script` (CVE-2007-2447) → RCE root | 🔴 |
| 6667 | UnrealIRCd 3.2.8.1 | Backdoor (CVE-2010-2075) → RCE | 🔴 |
| 1524 | bindshell | Shell root abierta (backdoor) | 🔴 |
| 3306 | MySQL 5.0.51a | root sin/con contraseña débil | 🟠 |
| 5900 | VNC | Contraseña débil (`password`) | 🟠 |
| 8180 | Tomcat | Credenciales por defecto → deploy WAR → RCE | 🟠 |
| 80 | Apache 2.2.8 / PHP 5.2.4 | Apps web vulnerables (DVWA, Mutillidae) | 🟠 |

## 6. Hallazgos detallados (Fase 5) — se rellenan al explotar

### F-01 · [pendiente de confirmar por explotación]
<!-- Al explotar: payload/comando exacto, captura, qué se consiguió, impacto, remediación -->

## 7. Conclusiones
[Al final: causa raíz, prioridad, re-test.]

## 8. Anexos
- Salida completa de nmap, capturas de cada explotación.

---
<sub>Confidencial. Laboratorio autorizado, fines educativos.</sub>
