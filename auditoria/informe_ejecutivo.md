# Informe Ejecutivo — Evaluación de Seguridad de Aplicación Web

| | |
|---|---|
| **Cliente / Alcance** | Aplicación web de comercio electrónico — *entorno de laboratorio autorizado* |
| **Tipo de prueba** | Test de intrusión de caja negra (OWASP) sobre aplicación web |
| **Autor** | [Tu nombre] — Pentester Junior |
| **Fecha** | 2026-11-26 |
| **Clasificación** | Confidencial |
| **Versión** | 1.0 |

> ⚠️ **Nota de contexto:** esta evaluación se ha realizado en un **entorno de laboratorio de formación** (PortSwigger Web Security Academy y laboratorio propio aislado), con **autorización explícita** y con fines **educativos y de portfolio**. No corresponde a un sistema de producción de un cliente real.

---

## 1. Resumen ejecutivo

Se ha llevado a cabo una evaluación de seguridad sobre la aplicación web objetivo con el fin de identificar vulnerabilidades explotables por un atacante externo sin credenciales. La prueba se centró en los riesgos más críticos para aplicaciones web (OWASP Top 10).

**El resultado global es de riesgo CRÍTICO.** Se confirmó que un atacante no autenticado puede **comprometer por completo la base de datos** de la aplicación (incluyendo credenciales de usuarios y administradores) y **ejecutar código en el navegador de otros usuarios**, mediante vulnerabilidades de **inyección SQL** y **Cross-Site Scripting (XSS)**. Varias de estas debilidades se explotaron de principio a fin durante la prueba, obteniendo acceso administrativo y extrayendo datos sensibles.

Estas vulnerabilidades son **conocidas, de alto impacto y fáciles de corregir** con prácticas de desarrollo seguro estándar. Su explotación no requiere herramientas avanzadas ni información privilegiada.

---

## 2. Valoración global del riesgo

| Nivel de riesgo global | **🔴 CRÍTICO** |
|---|---|

### Resumen de hallazgos por severidad

| Severidad | Nº de hallazgos |
|---|:---:|
| 🔴 Crítica | 1 |
| 🟠 Alta | 2 |
| 🟡 Media | 1 |
| 🟢 Baja | 0 |
| **Total** | **4** |

### Mapa de hallazgos

| ID | Hallazgo | Severidad |
|---|---|:---:|
| **F-01** | Inyección SQL (múltiples instancias) | 🔴 Crítica |
| **F-02** | Elusión de WAF mediante codificación XML | 🟠 Alta |
| **F-03** | Inyección SQL a ciegas (blind / basada en tiempo) | 🟠 Alta |
| **F-04** | Cross-Site Scripting (XSS reflejado y basado en DOM) | 🟡 Media |

---

## 3. Impacto para el negocio

Si estas vulnerabilidades existieran en un sistema de producción, el impacto sería directo y grave:

- **Fuga de datos de clientes.** Un atacante puede volcar la base de datos completa: nombres de usuario, contraseñas, datos personales y, potencialmente, datos de pago. Esto supone un incidente notificable bajo el **RGPD**, con riesgo de **sanciones económicas** y **daño reputacional**.
- **Suplantación y acceso administrativo.** Se demostró el acceso como **administrador sin conocer su contraseña**, lo que permitiría manipular pedidos, precios, usuarios y contenido.
- **Ataques a los propios usuarios.** Mediante XSS, un atacante puede robar sesiones, realizar acciones en nombre de la víctima o redirigirla a páginas fraudulentas (**phishing**), erosionando la confianza en la marca.
- **Evasión de defensas.** Se comprobó que incluso con un filtro de seguridad (WAF) activo, el ataque puede **ofuscarse para esquivarlo**, por lo que no basta con "poner un WAF".

---

## 4. Recomendaciones estratégicas

Priorizadas por impacto frente a esfuerzo:

1. **Corregir las inyecciones SQL de inmediato (prioridad máxima).** Adoptar **consultas parametrizadas** en todo el acceso a datos. Es la medida de mayor impacto y bajo coste.
2. **Implantar codificación de salida y CSP** para erradicar el XSS en todos los contextos (HTML, atributos, JavaScript).
3. **No depender del WAF como única defensa.** El WAF es una capa adicional, no un sustituto del código seguro; configurarlo para normalizar/decodificar la entrada antes de inspeccionarla.
4. **Integrar seguridad en el ciclo de desarrollo (SDLC):** revisiones de código, análisis estático (SAST) y pruebas de seguridad recurrentes antes de cada despliegue.
5. **Formación en desarrollo seguro** para el equipo técnico, centrada en OWASP Top 10.

---

## 5. Conclusión

La aplicación evaluada presenta vulnerabilidades **críticas y explotables** que permitirían a un atacante comprometer la confidencialidad e integridad de los datos. Las correcciones propuestas son **bien conocidas y de implementación directa**. Se recomienda **priorizar la remediación de las inyecciones SQL** y realizar una **re-evaluación** una vez aplicadas las correcciones para verificar su eficacia.

El detalle técnico de cada hallazgo, con pasos de reproducción y remediación específica, se encuentra en el **Informe Técnico** adjunto.

---

<sub>Documento confidencial. Realizado en entorno de laboratorio autorizado, con fines educativos. Las técnicas descritas no deben emplearse contra sistemas sin autorización escrita.</sub>
