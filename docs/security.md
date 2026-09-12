# Seguridad y alcance

Este proyecto es una demo académica de coordinación remota y criptografía reversible. Aunque cifra realmente los tres TXT de demostración, no es un ransomware operativo general.

## Barreras de alcance

- Solo dos órdenes literales.
- Solo tres nombres exactos.
- Solo una carpeta `Datos` fija bajo `LAB_BASE`.
- Sin recursividad.
- Sin shell, PowerShell, WMI, PsExec, ejecución remota, propagación o persistencia.
- Sin gestión centralizada de claves: `demo.key` nunca sale del agente.
- La red recomendada es privada y aislada.

## Manejo de la clave

`demo.key` es una clave Fernet local de demostración. No la subas a Git, no la compartas entre víctimas y no la uses para proteger información real. Perderla impide la recuperación de los `.enc`.

## Datos permitidos

Los TXT deben ser ficticios y creados por el agente. No apuntes el laboratorio a perfiles de usuario, Documentos, Escritorio, unidades de red, carpetas compartidas, información institucional o equipos sin autorización.

## Detección y observabilidad

Para una práctica defensiva, instrumenta la red y las VMs con Sysmon, Windows Event Logs o un SIEM. Observa conexiones periódicas al puerto 5000, creación de `.enc`, eliminación de TXT y uso de la clave local. Hazlo en snapshots desechables y conserva los logs como evidencia.
