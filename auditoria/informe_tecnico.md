# Informe Técnico — Test de Intrusión de Aplicación Web

| | |
|---|---|
| **Cliente / Alcance** | Aplicación web de comercio electrónico — *entorno de laboratorio autorizado* |
| **Tipo de prueba** | Caja negra, sin credenciales (external web app pentest) |
| **Metodología** | OWASP WSTG / PTES |
| **Autor** | [Tu nombre] — Pentester Junior |
| **Fecha** | 2026-11-26 |
| **Clasificación** | Confidencial · Versión 1.0 |

> ⚠️ Evaluación realizada en **entorno de laboratorio** (PortSwigger Web Security Academy + laboratorio propio aislado), con **autorización explícita** y fines **educativos**. No es un sistema de producción real.

---

## 1. Alcance y objetivos

- **Objetivo:** identificar y explotar vulnerabilidades en la capa de aplicación web alcanzables por un atacante externo no autenticado.
- **En alcance:** la aplicación web y sus parámetros (URL, formularios, cabeceras, cookies).
- **Fuera de alcance:** denegación de servicio (DoS), ataques de ingeniería social, infraestructura de red subyacente.
- **Ventana de pruebas:** sesión de laboratorio controlada.

## 2. Metodología

Se siguió un enfoque estructurado basado en OWASP WSTG:

1. **Reconocimiento y mapeo** de la aplicación y sus puntos de entrada.
2. **Identificación de vulnerabilidades** probando cada parámetro con cargas de prueba.
3. **Explotación** controlada para confirmar el impacto real (prueba de concepto).
4. **Post-explotación** limitada a demostrar el acceso/datos obtenidos.
5. **Documentación** de evidencias, impacto y remediación.

## 3. Herramientas utilizadas

| Herramienta | Uso |
|---|---|
| **Burp Suite** (Proxy, Repeater) | Interceptar y manipular peticiones HTTP |
| **Hackvertor** (extensión Burp) | Codificación de payloads para elusión de filtros |
| **Python + requests** (scripts propios) | Automatización de extracción en inyecciones a ciegas |
| **Navegador (DevTools)** | Análisis de XSS basado en DOM |
| **nmap** | Reconocimiento de superficie (laboratorio propio) |

## 4. Resumen de hallazgos

| ID | Hallazgo | Severidad | CVSS 3.1 |
|---|---|:---:|:---:|
| F-01 | Inyección SQL (múltiples instancias) | 🔴 Crítica | 9.8 |
| F-02 | Elusión de WAF mediante codificación XML | 🟠 Alta | 8.2 |
| F-03 | Inyección SQL a ciegas (blind / time-based) | 🟠 Alta | 8.6 |
| F-04 | Cross-Site Scripting (reflejado y DOM) | 🟡 Media | 6.1 |

---

## 5. Hallazgos detallados

### F-01 · Inyección SQL (múltiples instancias) — 🔴 Crítica

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 9.8 (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) |
| **Componente** | Parámetros de categoría/filtro, formulario de login y cookie `TrackingId` |
| **OWASP** | A03:2021 – Injection |

**Descripción.** La aplicación concatena directamente la entrada del usuario dentro de consultas SQL, sin separarla del código. Esto permite a un atacante alterar la lógica de la consulta y acceder a datos y funciones no autorizados.

**Pasos de reproducción (PoC):**

1. *Recuperación de datos ocultos* — en el parámetro de categoría:
   ```
   Gifts'--
   ```
   Comenta el resto de la condición y expone productos no publicados.

2. *Sacar todos los registros*:
   ```
   Gifts' OR 1=1--
   ```

3. *Bypass de autenticación* — en el campo usuario del login:
   ```
   administrator'--
   ```
   Permite iniciar sesión como **administrator sin conocer la contraseña**.

4. *Volcado de credenciales (UNION)*:
   ```
   ' UNION SELECT username, password FROM users--
   ```
   Extrae usuarios y contraseñas de la tabla `users`.

![Evidencia F-01: respuesta de la aplicación mostrando las credenciales extraídas](EVIDENCIA_sqli_union.png)
*Pie: volcado de la tabla `users` mediante UNION-based SQLi.*

**Impacto.** Compromiso total de la confidencialidad e integridad de la base de datos: robo de credenciales, acceso administrativo y manipulación de datos.

**Remediación.**
- **Consultas parametrizadas / sentencias preparadas** en todo el acceso a datos (defensa principal).
- Validación de entrada con listas blancas donde aplique.
- Principio de **mínimos privilegios** en la cuenta de base de datos.
- No exponer mensajes de error SQL al usuario.

**Referencias:** OWASP SQL Injection Prevention Cheat Sheet; CWE-89.

---

### F-02 · Elusión de WAF mediante codificación XML — 🟠 Alta

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 8.2 |
| **Componente** | Endpoint de comprobación de stock (entrada XML) |
| **OWASP** | A03:2021 – Injection |

**Descripción.** El endpoint procesa XML enviado por el usuario y cuenta con un WAF que bloquea palabras clave SQL (`UNION`, `SELECT`…). Sin embargo, codificando el payload como **entidades XML hexadecimales** (`&#x..;`), el WAF no reconoce las palabras, pero el parser XML las decodifica antes de ejecutar la consulta, logrando la inyección.

**Pasos de reproducción (PoC):**

En el valor de `<storeId>`, usando codificación de entidades (p. ej. con Hackvertor):
```
<storeId><@hex_entities>1 UNION SELECT username||'~'||password FROM users<@/hex_entities></storeId>
```
El WAF ve `&#x31;&#x20;&#x55;…` en lugar de `1 UNION SELECT…` y lo deja pasar; el servidor devuelve las credenciales.

![Evidencia F-02: respuesta con las credenciales pese al WAF](EVIDENCIA_waf_bypass.png)
*Pie: inyección satisfactoria tras ofuscar el payload con entidades XML.*

**Impacto.** Igual que F-01 (compromiso de la base de datos), demostrando además que **el WAF no es una defensa suficiente** por sí solo.

**Remediación.**
- Corregir la inyección subyacente con consultas parametrizadas (no depender del WAF).
- Configurar el parser XML y el WAF para **normalizar/decodificar** la entrada **antes** de inspeccionarla.
- Deshabilitar el procesamiento de entidades externas en el parser XML.

**Referencias:** CWE-89; OWASP WSTG-INPV-05.

---

### F-03 · Inyección SQL a ciegas (blind / basada en tiempo) — 🟠 Alta

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 8.6 |
| **Componente** | Cookie `TrackingId` |
| **OWASP** | A03:2021 – Injection |

**Descripción.** La aplicación es vulnerable a inyección SQL aunque **no devuelve los resultados** de la consulta. Se puede inferir información observando un "semáforo": un cambio en la respuesta, un error condicionado o un **retardo temporal**.

**Pasos de reproducción (PoC):**

1. *Confirmación por retardo* (PostgreSQL), en la cookie `TrackingId`:
   ```
   TrackingId=x'||pg_sleep(10)--
   ```
   La respuesta tarda ~10 s → inyección confirmada.

2. *Extracción de la contraseña* (apilando consulta y condicionando el retardo):
   ```
   x'%3BSELECT CASE WHEN (username='administrator'
       AND SUBSTRING(password,N,1)='c') THEN pg_sleep(3) ELSE pg_sleep(0) END FROM users--
   ```
   Repitiendo carácter a carácter se reconstruye la contraseña. Se automatizó con un **script Python propio** (`extraer_password_time.py`), midiendo el tiempo de respuesta para cada hipótesis.

![Evidencia F-03: cronómetro de Burp mostrando el retardo de 10 s](EVIDENCIA_blind_time.png)
*Pie: retardo inducido que confirma la inyección a ciegas.*

**Impacto.** Extracción completa de datos sensibles (incluidas credenciales) de forma sigilosa, sin que la aplicación muestre errores ni resultados.

**Remediación.** Consultas parametrizadas; evitar diferencias observables (tiempos/errores) derivadas de la entrada; monitorización de consultas anómalamente lentas.

**Referencias:** CWE-89; PortSwigger Blind SQLi.

---

### F-04 · Cross-Site Scripting (reflejado y basado en DOM) — 🟡 Media

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 6.1 (`AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`) |
| **Componente** | Funcionalidad de búsqueda del blog |
| **OWASP** | A03:2021 – Injection (XSS) |

**Descripción.** La aplicación inserta entrada controlada por el usuario en el HTML/JavaScript de la página sin sanearla, permitiendo la ejecución de JavaScript en el navegador de la víctima.

**Pasos de reproducción (PoC):**

1. *XSS reflejado* (contexto HTML, sin codificación) — en el buscador:
   ```
   <script>alert(1)</script>
   ```

2. *XSS basado en DOM* (sink `document.write`, fuente `location.search`) — en el buscador:
   ```
   "><svg onload=alert(1)>
   ```
   La entrada se escribe dentro de un atributo `<img src="...">`; el payload cierra la etiqueta e inyecta un `<svg>` cuyo `onload` ejecuta el script.

![Evidencia F-04: ventana de alerta ejecutada por el XSS](EVIDENCIA_xss_alert.png)
*Pie: ejecución de `alert()` como prueba de concepto de XSS.*

**Impacto.** Robo de cookies de sesión (si no son `HttpOnly`), ejecución de acciones en nombre de la víctima, redirección a phishing y defacement en el contexto del usuario.

**Remediación.**
- **Codificación de salida** según el contexto (HTML, atributo, JS, URL).
- **Content-Security-Policy (CSP)** restrictiva.
- Cookies de sesión con atributo **`HttpOnly`**.
- Evitar sinks peligrosos (`document.write`, `innerHTML`) con datos no confiables; usar librerías de saneamiento (DOMPurify).

**Referencias:** CWE-79; OWASP XSS Prevention Cheat Sheet.

---

## 6. Conclusiones

La aplicación presenta una **debilidad sistémica frente a inyección** (SQL y XSS), con **cuatro hallazgos** que van de media a crítica. La causa raíz común es la **falta de separación entre datos y código** (consultas concatenadas, salida sin codificar). La corrección pasa por adoptar **consultas parametrizadas** y **codificación de salida** de forma consistente, además de no delegar la seguridad únicamente en el WAF.

Se recomienda una **re-evaluación** tras aplicar las correcciones para verificar su eficacia.

## 7. Anexos

- **Scripts de explotación propios:** `scripts/extraer_password_time.py`, `extraer_password_blind.py`, `extraer_password_errores.py`, `extraer_visible_error.py`.
- **Referencia técnica completa:** `sqli_referencia_completa.md`, `xss_referencia_completa.md`.
- **Evidencias:** sustituir los marcadores `EVIDENCIA_*.png` por las capturas reales de cada prueba.

---

<sub>Documento confidencial. Realizado en entorno de laboratorio autorizado, con fines educativos. Las técnicas aquí descritas no deben emplearse contra sistemas sin autorización escrita.</sub>
