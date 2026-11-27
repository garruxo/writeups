# Informe Forense (DFIR) — Brecha de datos en la tienda online

| | |
|---|---|
| **Caso** | Robo de datos de clientes a través de la web comercial |
| **Sistema** | OWASP Juice Shop (laboratorio) · `http://localhost:3000` |
| **Analista** | [Tu nombre] |
| **Fecha del análisis** | 2026-11-27 |
| **Clasificación** | Confidencial |

> ⚠️ Ejercicio en laboratorio aislado, con fines educativos. El "atacante" y la "víctima" pertenecen al propio entorno de prácticas.

## 1. Resumen del incidente
Se detectó la **exfiltración de la base de datos de clientes** (correos y contraseñas) de la tienda online. El análisis del tráfico de red confirma que el atacante explotó una **inyección SQL** en el buscador de productos (`/rest/products/search`) mediante una consulta `UNION` para volcar la tabla `Users`. La evidencia (captura de red) fue preservada y sellada con hash.

## 2. Metodología forense (fases DFIR)
Identificación → **Preservación** (captura + hash) → Análisis → Documentación → Lecciones aprendidas.

## 3. Evidencias recogidas (cadena de custodia)
| Evidencia | Origen | Hash SHA-256 | Fecha/hora |
|---|---|---|---|
| `captura_ataque.pcap` | Captura de red (tcpdump, puerto 3000) | `ecf590b7944c964792ddb0e6d6093fd6634071daee0e515761bfe63388480b82` | 2026-11-27 ~18:00 |

**Preservación realizada:**
```
sudo tcpdump -i any -s 0 -w captura_ataque.pcap tcp port 3000
sha256sum captura_ataque.pcap
```

## 4. Análisis — reconstrucción del ataque
**Comando de análisis (extracción de peticiones HTTP):**
```
tshark -r captura_ataque.pcap -Y http.request -T fields -e frame.time -e ip.src -e http.request.full_uri
```

**Petición maliciosa capturada (decodificada):**
```
GET /rest/products/search?q=qwert')) UNION SELECT id,email,password,'4','5','6','7','8','9','10' FROM Users--
Origen: 127.0.0.1 (navegador) / 172.17.0.1 (gateway Docker)
```
El parámetro `q` cierra el contexto (`'))`), inyecta un `UNION SELECT` de 10 columnas y comenta el resto (`--`), devolviendo el contenido de la tabla `Users` (correo + hash de cada cliente).

## 5. Cronología del ataque (timeline)
| Hora (aprox.) | Acción del atacante | Evidencia |
|---|---|---|
| 18:0x | Sondeo de inyección en el buscador (`test'))--`) | pcap |
| 18:0x | Petición `UNION SELECT ... FROM Users` (volcado) — repetida | pcap |
| 18:0x | Descarga de `/favicon.ico` (navegación normal del navegador) | pcap |

> Para horas exactas por petición: `tshark -r captura_ataque.pcap -Y http.request -T fields -e frame.time -e http.request.full_uri`.

## 6. Indicadores de compromiso (IOCs)
- **IP de origen:** `127.0.0.1` (navegador) / `172.17.0.1` (gateway Docker).
- **Endpoint atacado:** `/rest/products/search` (parámetro `q`).
- **Payload:** `')) UNION SELECT id,email,password,... FROM Users--`
- **Patrón detectable:** peticiones a `/rest/products/search` que contengan `UNION SELECT` o `FROM Users`.

## 7. Alcance / datos comprometidos
Tabla **`Users` completa**: correos electrónicos y **hashes de contraseña (MD5 sin sal)** de todos los clientes. Al ser MD5, los hashes son **crackeables** (p. ej. `admin@juice-sh.op` → `admin123`), por lo que debe asumirse el **compromiso de credenciales en claro**.

## 8. Causa raíz
**Inyección SQL** por falta de consultas parametrizadas en `/rest/products/search`, agravada por el **almacenamiento de contraseñas en MD5 sin sal** (F-02 y F-03 del informe de auditoría).

## 9. Contención, erradicación y recuperación
- **Contención:** bloquear la IP de origen; desplegar regla WAF que detecte `UNION SELECT`/`FROM Users` en `q`; deshabilitar el endpoint vulnerable si es viable.
- **Erradicación:** corregir el SQLi con **consultas parametrizadas**; migrar el hashing a **bcrypt/argon2** con sal.
- **Recuperación:** **forzar el reseteo de contraseñas** de todos los clientes; notificar a los afectados y a la **AEPD** (RGPD, plazo 72 h); revisar logs por accesos indebidos.

## 10. Lecciones aprendidas
- **Punto ciego de registro:** la aplicación **no registraba las peticiones** (los logs del contenedor solo tenían el arranque). En producción es imprescindible un **log de acceso** y/o **WAF** con alertas para poder investigar.
- Validar/parametrizar toda entrada; nunca confiar en el filtro del cliente.
- Hashing fuerte de contraseñas desde el diseño.
- Monitorización y detección temprana (un `UNION SELECT` en el buscador debería disparar una alerta).

---
<sub>Confidencial. Laboratorio autorizado, fines educativos. Evidencia preservada mediante hash SHA-256 (cadena de custodia).</sub>
