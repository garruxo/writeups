
# 🛡️ Writeups de Seguridad Web / AppSec

Documentación de mi aprendizaje práctico en **seguridad web y pentesting**: writeups de laboratorios resueltos, referencias técnicas y herramientas propias. Todo realizado en entornos de laboratorio autorizados (PortSwigger Web Security Academy, máquinas vulnerables de prueba y mi propio laboratorio aislado).

> 🎯 **Objetivo:** especializarme en seguridad de aplicaciones web (AppSec).

---

## 👤 Sobre mí
[1-2 líneas tuyas: quién eres y qué buscas. Ej: "Apasionado de la ciberseguridad, formándome a diario en seguridad ofensiva web con el objetivo de trabajar como pentester junior."]

- 📍 [Tu ciudad / España · Remoto]
- 💼 LinkedIn: [tu enlace]
- 📧 Contacto: [tu email]

---

## 🧰 Habilidades y herramientas
- **Vulnerabilidades web:** SQL Injection, Web Cache Deception (OWASP Top 10 en progreso).
- **Herramientas:** Burp Suite, nmap, Metasploit, sqlmap.
- **Scripting:** Python (automatización de explotación).
- **Metodología:** reconocimiento → explotación → post-explotación → reporte.
- **Laboratorio propio:** montaje de VMs con aislamiento de red (host-only).

---

## 📂 Writeups
| Lab / Máquina | Tipo | Plataforma | Writeup |
|---|---|---|---|
| SQL injection ciega con respuestas condicionales | SQLi | PortSwigger | [ver](writeups/sqli-blind-conditional.md) |
| Web Cache Deception (path delimiters) | WCD | PortSwigger | [ver](writeups/web-cache-deception.md) |

*(Voy añadiendo writeups conforme resuelvo laboratorios.)*

---

## 📘 Referencias técnicas
- [Metodología de pentesting](metodologia_pentest.md) — el proceso fase por fase.
- [SQL Injection — referencia completa](sqli_referencia_completa.md) — todas las técnicas con payloads.

---

## 🐍 Herramientas / scripts
- `scripts/` — scripts propios de explotación (ej. extracción automática en blind SQLi).

---

## ⚖️ Nota ética
Todo el contenido de este repositorio se ha realizado en **entornos de laboratorio** o con **autorización explícita**, con fines **educativos**. Las técnicas aquí documentadas no deben usarse contra sistemas sin permiso.