# Informe Ejecutivo — Evaluación de Seguridad "Servidor Interno" (Auditoría #1)

| | |
|---|---|
| **Cliente / Alcance** | ACME Corp (ficticio) — servidor interno `192.168.56.104` |
| **Sistema real** | Metasploitable 2 (laboratorio vulnerable, red host-only) |
| **Tipo de prueba** | Test de intrusión de red interna, caja negra, sin credenciales |
| **Autor** | [Tu nombre] — Pentester |
| **Fecha** | 2026-11-26 · Versión 1.0 · **CONFIDENCIAL** |

> ⚠️ Realizado en **laboratorio aislado** (host-only), con máquina vulnerable a propósito y **autorización**, con fines **educativos**.

---

## 1. Resumen ejecutivo

Se evaluó la seguridad de un servidor interno desde la perspectiva de un atacante situado en la misma red, **sin credenciales**. El resultado es de **riesgo CRÍTICO**: se logró el **control total del servidor (acceso root)** por **dos vías distintas e independientes**, y el **acceso completo a la base de datos** sin necesidad de contraseña.

Un atacante con acceso a la red podría, en minutos, **apoderarse del servidor y de todos sus datos**, e incluso usarlo como **trampolín** para atacar el resto de los sistemas internos.

---

## 2. Valoración global del riesgo

| Nivel de riesgo global | **🔴 CRÍTICO** |
|---|---|

| Severidad | Nº |
|---|:---:|
| 🔴 Crítica | 2 |
| 🟠 Alta | 1 |
| 🟡 Media | 0 |
| **Total** | **3** |

| ID | Hallazgo | Severidad |
|---|---|:---:|
| F-01 | Puerta trasera en el servicio FTP | 🔴 Crítica |
| F-02 | Base de datos accesible sin contraseña | 🟠 Alta |
| F-03 | Ejecución remota de comandos en Samba | 🔴 Crítica |

*(Se identificaron además otros servicios potencialmente vulnerables, pendientes de revisión en una segunda fase.)*

---

## 3. Impacto para el negocio

- **Toma de control total del servidor.** Un atacante obtiene privilegios de administrador (root) y puede leer, modificar o destruir cualquier información.
- **Fuga de datos.** La base de datos (clientes, credenciales…) es accesible sin barrera alguna. Sería un incidente notificable bajo **RGPD**, con riesgo de **sanción** y **daño reputacional**.
- **Efecto dominó.** El servidor comprometido serviría de **punto de pivote** para alcanzar otros equipos de la red interna.
- **Facilidad de ataque.** No se requieren técnicas avanzadas: las vulnerabilidades son conocidas y automatizables.

---

## 4. Recomendaciones estratégicas

1. **Dar de baja o actualizar el sistema de inmediato:** el software es antiguo y sin mantenimiento (prioridad máxima).
2. **Gestión de parches** continua para evitar versiones vulnerables conocidas.
3. **Hardening de configuración:** contraseñas robustas, eliminar accesos por defecto y restringir los servicios expuestos mediante **firewall**.
4. **Segmentación de red** para limitar el movimiento lateral en caso de compromiso.
5. **Re-evaluación** tras aplicar las correcciones.

---

## 5. Conclusión

El servidor evaluado es **altamente vulnerable** y permitiría un compromiso total con un esfuerzo mínimo. La causa de fondo es la **falta de actualización y de endurecimiento** del sistema. Las medidas correctoras son conocidas y de aplicación directa; se recomienda **priorizarlas** y realizar una **re-evaluación** posterior. El detalle técnico está en el **Informe Técnico** adjunto.

---
<sub>Confidencial. Realizado en laboratorio autorizado, con fines educativos.</sub>
