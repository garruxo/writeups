<!--
  PLANTILLA DE WRITEUP  ·  copia este archivo para cada lab/máquina
  - Rellena el texto donde pone [ ... ]
  - Donde pone ![Captura: ...](PEGA_AQUI_LA_IMAGEN) arrastra tu captura en GitHub
    (al soltar la imagen, GitHub te genera el enlace solo; borra PEGA_AQUI_LA_IMAGEN)
  - Las líneas entre <!-- --> son notas para ti y NO se ven en GitHub.
  - Borra estas instrucciones de arriba cuando acabes.
-->

# [Nombre del fallo] — [qué conseguiste]
<!-- Ej: SQL Injection ciega — robo de la contraseña del administrador -->

| | |
|---|---|
| **Tipo** | [SQLi / XSS / IDOR / ...] |
| **Plataforma** | [PortSwigger / HTB / THM / lab propio] |
| **Dificultad** | [Apprentice / Practitioner / fácil / media] |
| **Fecha** | [DD/MM/AAAA] |
| **Herramientas** | [Burp Suite, Python, nmap...] |

---

## Resumen
[2-3 frases: qué fallo era, qué conseguiste y por qué importa.]

---

## Objetivo y entorno
[Qué había que lograr y en qué aplicación. Credenciales de prueba si las había.]

---

## 1 · Reconocimiento / Detección
[Cómo descubriste el fallo, con qué herramienta y qué te hizo sospechar.]

![Captura: la herramienta detectando el fallo](PEGA_AQUI_LA_IMAGEN)
<!-- Ej: Burp Repeater mostrando el error / el comportamiento raro. Pon una flecha al dato clave. -->
*Pie de foto: [qué se ve en la imagen].*

---

## 2 · Explotación
[Los pasos del ataque, en orden. Explica el porqué, no solo el comando.]

**Paso 1 — [qué haces]**
```
[comando o payload aquí]
```

![Captura: el payload y la respuesta](PEGA_AQUI_LA_IMAGEN)
*Pie de foto: [qué se ve].*

**Paso 2 — [qué haces]**
[texto...]

![Captura: el resultado / la prueba final](PEGA_AQUI_LA_IMAGEN)
<!-- La "prueba de concepto": el dato robado, el acceso, el "Congratulations", etc. -->
*Pie de foto: [qué se ve].*

---

## 3 · Impacto
[Qué podría hacer un atacante real con esto. Habla de riesgo para el negocio:
robo de datos, acceso a cuentas, etc.]

---

## 4 · Cómo se arregla (remediación)
[La defensa. Ej: consultas parametrizadas, validación de entrada, codificar la
salida... Esto demuestra que piensas como defensor, no solo como atacante.]

---

## Lo que aprendí
[1-2 líneas con la idea clave que te llevas. Demuestra que lo entendiste, no que
lo copiaste.]

---
<sub>Realizado en entorno de laboratorio / con autorización. Solo con fines educativos.</sub>
