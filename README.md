# Laboratorio remoto controlado

Implementación reproducible del laboratorio descrito en `Guia_Laboratorio v3.pdf`.

El proyecto demuestra un flujo de *tasking* remoto acotado:

```text
agente -> registro -> polling -> orden permitida -> operación local -> telemetría
```

La simulación **no cifra archivos**, no ejecuta comandos remotos y no accede a carpetas personales. Solo renombra archivos ficticios dentro del directorio de laboratorio y luego restaura sus nombres.

## Qué hace exactamente

La repo representa tres papeles: un servidor, un controlador y uno o más agentes. En esta primera versión el servidor y las operaciones locales están implementados y probados; el flujo se ejecuta en `127.0.0.1` para que pueda validarse en una sola máquina.

1. El agente se identifica con un ID como `LAB-A1B2C3` y se registra en `/registro`.
2. El servidor guarda el ID, hostname, IP, estado, hora de conexión y último resultado en `victimas.json`.
3. El controlador solicita una orden para ese ID. Solo se aceptan `SIMULAR` y `RECUPERAR`.
4. La orden queda en una cola en memoria hasta que el agente consulta `/poll`.
5. El agente ejecuta la operación local dentro de la carpeta `Datos` y comunica el resultado en `/resultado`.

### ¿Encripta los archivos?

**No.** El nombre del laboratorio alude a una simulación de ransomware, pero este código no implementa cifrado. `SIMULAR` hace solamente esto:

- busca archivos dentro de `Datos`;
- cambia `documento1.txt` por `documento1.txt.simulado`;
- crea `SIMULACION_RANSOMWARE.txt` como marcador visible;
- informa cuántos archivos fueron renombrados.

El contenido de cada archivo permanece igual. No se usa una clave, algoritmo criptográfico ni extensión de cifrado. La operación no borra datos y no puede apuntar a Documentos, Escritorio, perfiles o unidades de red mediante el flujo documentado.

### ¿Cómo se recuperan?

`RECUPERAR` recorre únicamente los archivos que terminan en `.simulado`. Para cada uno, quita ese sufijo si el nombre original todavía no existe. Después elimina `SIMULACION_RANSOMWARE.txt` y reporta el número de archivos restaurados. Por ejemplo:

```text
documento1.txt       -> SIMULAR -> documento1.txt.simulado
documento1.txt.simulado -> RECUPERAR -> documento1.txt
```

La recuperación es una reversión de nombres, no un descifrado. Por eso solo revierte esta simulación controlada y no recuperaría archivos cifrados por un ransomware real.

### Qué no hace

- No ejecuta comandos recibidos desde la red.
- No ejecuta shell, PowerShell ni código Python remoto.
- No cifra, elimina, comprime ni exfiltra archivos.
- No se propaga ni establece persistencia.
- No modifica archivos fuera de la carpeta de laboratorio.
- No sustituye una solución de respuesta a incidentes ni una copia de seguridad.

## Qué contiene

- `src/lab_sim/server.py`: servidor Flask con registro, polling, cola de órdenes y estado.
- `src/lab_sim/agent_operations.py`: operaciones locales seguras de simulación y recuperación.
- `tests/`: pruebas del contrato HTTP y de las operaciones sobre archivos temporales.
- `docs/architecture.md`: arquitectura, límites y decisiones de seguridad.
- `docs/runbook.md`: ejecución paso a paso y pruebas manuales.
- `docs/architecture.md`: explicación detallada del flujo HTTP y los estados.
- `Guia_Laboratorio v3.pdf`: material original de referencia.

## Requisitos

- Python 3.11 o posterior.
- Entorno virtual recomendado.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
py -m pip install -e .
```

## Pruebas

```powershell
py -m pytest -q
```

Las pruebas usan `tmp_path` y el cliente de pruebas de Flask: no necesitan red, máquinas virtuales ni archivos reales del usuario.

## Ejecutar el servidor local

```powershell
$env:LAB_DATA_DIR = "$PWD\.lab-data"
py -m lab_sim.server
```

El servidor escucha en `127.0.0.1:5000` por defecto. Para ver el estado:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/estado
```

Para registrar una víctima de laboratorio y poner una orden en cola:

```powershell
$body = @{ id = 'LAB-A1B2C3'; hostname = 'victima-demo' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/registro -Method Post -ContentType 'application/json' -Body $body

$body = @{ id = 'LAB-A1B2C3'; comando = 'SIMULAR' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/ordenar -Method Post -ContentType 'application/json' -Body $body
```

## Uso responsable

Ejecuta el laboratorio únicamente en una VM aislada o en una carpeta temporal con archivos ficticios. No lo apuntes a Documentos, Escritorio, perfiles, unidades de red ni datos institucionales. Consulta [docs/runbook.md](docs/runbook.md) antes de usarlo.
