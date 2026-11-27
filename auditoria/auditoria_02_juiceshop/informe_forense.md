# Informe Forense (DFIR) — Brecha de datos en la tienda online

| | |
|---|---|
| **Caso** | Robo de datos de clientes a través de la web comercial |
| **Sistema** | OWASP Juice Shop (laboratorio) · `http://localhost:3000` |
| **Analista** | [Tu nombre] |
| **Fecha del análisis** | 2026-11-27 |
| **Clasificación** | Confidencial |

> ⚠️ Ejercicio en laboratorio aislado, con fines educativos. El "atacante" y la "víctima" son del propio entorno de prácticas.

## 1. Resumen del incidente
[2-3 frases: qué pasó, cómo se detectó, qué datos se vieron afectados. Se rellena al final.]

## 2. Metodología forense (fases DFIR)
Identificación → **Preservación** (copia + hash) → Análisis → Documentación → Lecciones aprendidas.

## 3. Evidencias recogidas (cadena de custodia)
| Evidencia | Origen | Hash SHA-256 | Fecha/hora recogida |
|---|---|---|---|
| `evidencia_juiceshop.log` | Logs del servidor (contenedor Docker) | [pegar hash] | [fecha] |

## 4. Análisis — reconstrucción del ataque

**Comandos de análisis usados:**
```
grep "products/search" evidencia_juiceshop.log
grep -i "union"        evidencia_juiceshop.log
grep "rest/user/login" evidencia_juiceshop.log
grep " 500 "           evidencia_juiceshop.log
```

**Hallazgos (pegar líneas reales de los logs):**
```
[PEGAR LAS LÍNEAS DEL ATAQUE]
```

## 5. Cronología del ataque (timeline)
| Hora | Acción del atacante | Evidencia |
|---|---|---|
| [hh:mm] | Sondeo de inyección en el buscador (`'))--`) | log |
| [hh:mm] | Error 500 por nº de columnas (UNION) | log |
| [hh:mm] | Volcado de la tabla Users (UNION 10 cols) | log |
| [hh:mm] | Bypass de login (`' OR 1=1--`) | log |

## 6. Indicadores de compromiso (IOCs)
- **IP del atacante:** [p.ej. 172.17.0.1 / 127.0.0.1]
- **Endpoints atacados:** `/rest/products/search`, `/rest/user/login`
- **Payloads:** `')) UNION SELECT ... FROM Users--`, `' OR 1=1--`
- **User-Agent:** [del log]

## 7. Alcance / datos comprometidos
[Qué se robó: tabla Users completa → correos + hashes MD5 de todos los clientes.]

## 8. Causa raíz
[Inyección SQL (falta de consultas parametrizadas) + contraseñas en MD5 sin sal.]

## 9. Contención, erradicación y recuperación
- **Contención:** [bloquear IP, deshabilitar endpoint vulnerable]
- **Erradicación:** [parchear el SQLi, migrar hashes a bcrypt]
- **Recuperación:** [forzar reseteo de contraseñas, notificar a afectados/AEPD]

## 10. Lecciones aprendidas
[Qué fallo organizativo/técnico lo permitió y cómo evitarlo.]

---
<sub>Confidencial. Laboratorio autorizado, fines educativos. Cadena de custodia preservada mediante hash.</sub>
