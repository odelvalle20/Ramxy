# Arquitectura y límites

## Flujo

1. El agente se registra con un identificador `LAB-XXXXXX`.
2. El servidor conserva identidad, hostname, IP, estado y último resultado en `victimas.json`.
3. El agente consulta `/poll` periódicamente.
4. El controlador pone en cola únicamente `SIMULAR` o `RECUPERAR`.
5. El agente consume una orden y opera solo dentro de su carpeta `Datos`.
6. El agente informa el resultado mediante `/resultado`.

## Decisiones de seguridad

- Los identificadores se validan con `LAB-[A-F0-9]{6}`.
- Cualquier comando distinto de `SIMULAR` y `RECUPERAR` se rechaza.
- Las operaciones no ejecutan shell, Python recibido por red ni comandos arbitrarios.
- `simulate()` únicamente añade `.simulado`; no cifra ni elimina contenido.
- `recover()` solo revierte archivos `.simulado` y elimina el marcador de demostración.
- Las pruebas usan directorios temporales y verifican que un archivo fuera de `Datos` permanece intacto.
- El servidor local usa `127.0.0.1`; la topología con varias VMs de la guía puede reproducirse después en una red aislada.

## Diferencias frente a la guía PDF

La guía fija direcciones `192.168.100.x` y rutas Windows para una demostración con tres equipos. Esta repo empieza por una variante local y portable para poder probarla de forma segura en una sola máquina. Las decisiones de red y empaquetado con PyInstaller quedan como extensión documentada, no como requisito para validar el comportamiento principal.
