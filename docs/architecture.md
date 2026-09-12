# Arquitectura y límites

## Flujo

1. El agente se registra con un identificador `LAB-XXXXXX`.
2. El servidor conserva identidad, hostname, IP, estado y último resultado en `victimas.json`.
3. El agente consulta `/poll` periódicamente.
4. El controlador pone en cola únicamente `SIMULAR` o `RECUPERAR`.
5. El agente consume una orden y opera solo dentro de su carpeta `Datos`.
6. El agente informa el resultado mediante `/resultado`.

## Componentes y responsabilidades

### Servidor

`src/lab_sim/server.py` crea una aplicación Flask. Su base de datos es un JSON local llamado `victimas.json`; cada escritura usa un archivo temporal y `replace()` para evitar dejar una escritura parcial. Un bloqueo protege las operaciones que leen y actualizan el estado.

### Controlador

El controlador representa la persona que observa `/estado` y solicita una operación para un ID. En la implementación HTTP, esa acción equivale a enviar `POST /ordenar` con `SIMULAR` o `RECUPERAR`.

### Agente

El agente representa el endpoint de laboratorio. Consulta `/poll`, consume una orden pendiente y ejecuta la operación local. La operación de archivos está separada en `agent_operations.py` para poder probarla con directorios temporales sin levantar una red.

## Contrato HTTP

| Endpoint | Función | Resultado relevante |
| --- | --- | --- |
| `GET /estado` | Lista víctimas y telemetría | JSON con `estado`, `ultima_conexion` y `ultimo_resultado` |
| `POST /registro` | Registra o actualiza una víctima | `200` si el ID es válido; `400` si no lo es |
| `POST /poll` | Entrega una orden pendiente una sola vez | `comando` es `SIMULAR`, `RECUPERAR` o `null` |
| `POST /ordenar` | Encola una operación permitida | `400` para cualquier comando distinto |
| `POST /resultado` | Guarda el resultado de la operación | Actualiza estado, resultado y hora |

Una víctima debe existir antes de recibir órdenes. Por eso una orden para un ID desconocido devuelve `404`. El `poll` consume la orden de la cola; una segunda consulta no vuelve a ejecutar la misma orden.

## Estados y recuperación

Los estados principales son `CONECTADO`, `EJECUTANDO`, `SIMULACION_COMPLETADA`, `RECUPERADO` y `ERROR`. La operación `SIMULAR` renombra archivos ficticios agregando `.simulado` y crea un marcador de texto. La operación `RECUPERAR` quita ese sufijo solo cuando el nombre original está libre y elimina el marcador.

Esto no es cifrado. No hay clave ni transformación criptográfica: el contenido de los archivos nunca cambia. En consecuencia, `RECUPERAR` no descifra nada; únicamente restaura nombres que el propio laboratorio modificó.

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
