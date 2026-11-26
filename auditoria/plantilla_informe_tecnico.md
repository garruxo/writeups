<!-- PLANTILLA · Informe Técnico. Copia este archivo para cada auditoría. Repite el bloque "Fxx" por hallazgo. -->

# Informe Técnico — Test de Intrusión de [Objetivo]

| | |
|---|---|
| **Cliente / Alcance** | [Objetivo / IPs / URLs] |
| **Tipo de prueba** | [Caja negra / gris / blanca] |
| **Metodología** | OWASP WSTG / PTES |
| **Autor** | [Tu nombre] |
| **Fecha** | [AAAA-MM-DD] · Versión 1.0 |

> ⚠️ Realizado con [autorización / en laboratorio], fines [educativos].

## 1. Alcance y objetivos
- **Objetivo:** [ ]
- **En alcance:** [ ]
- **Fuera de alcance:** [DoS, ingeniería social, …]

## 2. Metodología
Reconocimiento → Escaneo/Enum → Análisis de vulns → Explotación → Post-explotación → Documentación.

## 3. Herramientas
| Herramienta | Uso |
|---|---|
| nmap | Escaneo de puertos/servicios |
| [ ] | [ ] |

## 4. Resumen de hallazgos
| ID | Hallazgo | Severidad | CVSS |
|---|---|:---:|:---:|
| F-01 | [ ] | [ ] | [ ] |
| F-02 | [ ] | [ ] | [ ] |

## 5. Hallazgos detallados

### F-01 · [Título] — [🔴/🟠/🟡/🟢 Severidad]
| Campo | Valor |
|---|---|
| **CVSS 3.1** | [puntuación + vector] |
| **Componente** | [parámetro / endpoint / servicio] |
| **OWASP / CWE** | [A0x:2021 / CWE-xx] |

**Descripción.** [Qué es el fallo y por qué ocurre.]

**Pasos de reproducción (PoC):**
```
[payload o comando exacto]
```
![Evidencia F-01: ...](EVIDENCIA_f01.png)
*Pie: [qué se ve].*

**Impacto.** [Qué consigue un atacante.]

**Remediación.** [La defensa concreta.]

**Referencias:** [OWASP / CWE / CVE].

<!-- Copia el bloque F-01 completo para F-02, F-03... -->

## 6. Conclusiones
[Causa raíz común, prioridad de corrección, recomendación de re-test.]

## 7. Anexos
- Scripts usados, salidas de nmap, evidencias completas.

---
<sub>Confidencial. Realizado con autorización, con fines educativos. No usar sin permiso escrito.</sub>
