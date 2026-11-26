# Informe Técnico — Test de Intrusión Web "Tienda Online" (Auditoría #2)

| | |
|---|---|
| **Cliente / Alcance** | Empresa de e-commerce (ficticia) — tienda online |
| **Sistema real** | OWASP Juice Shop (app web vulnerable, laboratorio) · `http://localhost:3000` |
| **Tipo de prueba** | Caja negra, aplicación web |
| **Metodología** | OWASP WSTG |
| **Autor** | [Tu nombre] |
| **Fecha** | 2026-11-26 · Versión 0.1 (borrador) |

> ⚠️ Laboratorio local, app vulnerable a propósito, fines educativos. Escenario: investigar un robo de datos de clientes a través de la web comercial.

## 1. Alcance y objetivos
- **Objetivo:** identificar las vulnerabilidades de la tienda que permitirían (o permitieron) el **robo de datos de clientes**.
- **En alcance:** la aplicación web `http://localhost:3000` y su API (`/rest/`, `/api/`).
- **Fuera de alcance:** DoS, infraestructura del host.

## 2. Metodología y herramientas (Fase 2-3)
| Fase | Herramientas |
|---|---|
| Reconocimiento | navegador + DevTools, `whatweb` |
| Mapeo / proxy | Burp Suite (interceptar la API) |
| Escaneo web | `nikto`, `nmap -p3000` |
| Explotación | manual, `sqlmap` |
| Credenciales | `john` / `hashcat` (crackear hashes robados) |

**Reconocimiento:**
```
whatweb http://localhost:3000
```
```
[PEGAR SALIDA]
```

## 3. Resumen de hallazgos
| ID | Hallazgo | Severidad | CVSS |
|---|---|:---:|:---:|
| F-01 | [ ] | [ ] | [ ] |

## 4. Hallazgos detallados (se rellenan al explotar)

### F-01 · [pendiente]

## 5. Conclusiones
[Al final.]

---
<sub>Confidencial. Laboratorio autorizado, fines educativos.</sub>
