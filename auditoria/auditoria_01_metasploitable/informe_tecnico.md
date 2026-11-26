# Informe Técnico — Test de Intrusión "Servidor Interno" (Auditoría #1)

| | |
|---|---|
| **Cliente / Alcance** | ACME Corp (ficticio) — servidor interno · `192.168.56.104` |
| **Sistema real** | Metasploitable 2 (laboratorio vulnerable, red host-only) |
| **Tipo de prueba** | Caja negra, sin credenciales (red interna) |
| **Metodología** | OWASP / PTES |
| **Autor** | [Tu nombre] |
| **Fecha** | 2026-11-26 · Versión 0.1 (borrador) |

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

<!-- Siguiente hallazgo: copia este bloque como F-02 -->

### F-02 · [siguiente — pendiente de explotar]

## 7. Conclusiones
[Al final: causa raíz, prioridad, re-test.]

## 8. Anexos
- Salida completa de nmap, capturas de cada explotación.

---
<sub>Confidencial. Laboratorio autorizado, fines educativos.</sub>
