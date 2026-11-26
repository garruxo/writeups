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
| F-01 | SQLi en el login → acceso como administrador | 🔴 Crítica | 9.8 |
| F-02 | SQLi en el buscador → robo de datos de clientes | 🔴 Crítica | 9.8 |

## 4. Hallazgos detallados

### F-01 · Inyección SQL en el login (acceso como administrador) — 🔴 Crítica

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 9.8 — bypass de autenticación |
| **Componente** | Formulario de login (`POST /rest/user/login`) |
| **OWASP** | A03:2021 – Injection · CWE-89 |

**Descripción.** El campo de email del login se concatena en la consulta SQL sin sanear. Inyectando una condición siempre verdadera se **omite la autenticación** y se accede como el primer usuario (administrador).

**Pasos de reproducción (PoC):**
```
En el campo Email:  ' OR 1=1--
En Password:        cualquier cosa
-> Inicia sesión como administrador (admin@juice-sh.op)
```
![Evidencia F-01: sesión iniciada como admin](EVIDENCIA_f01_admin.png)

**Impacto.** Acceso total a la cuenta de administrador sin credenciales: gestión de la tienda, pedidos y datos.

**Remediación.** Consultas parametrizadas en la autenticación; nunca concatenar la entrada. Bloqueo de intentos y 2FA.

### F-02 · [en progreso — robo de datos vía SQLi en el buscador]

## 5. Conclusiones
[Al final.]

---
<sub>Confidencial. Laboratorio autorizado, fines educativos.</sub>
