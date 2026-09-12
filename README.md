# Laboratorio remoto controlado

Implementación reproducible del laboratorio descrito en `Guia_Laboratorio v3.pdf`.

El proyecto demuestra un flujo de *tasking* remoto acotado:

```text
agente -> registro -> polling -> orden permitida -> operación local -> telemetría
```

La simulación **no cifra archivos**, no ejecuta comandos remotos y no accede a carpetas personales. Solo renombra archivos ficticios dentro del directorio de laboratorio y luego restaura sus nombres.

## Qué contiene

- `src/lab_sim/server.py`: servidor Flask con registro, polling, cola de órdenes y estado.
- `src/lab_sim/agent_operations.py`: operaciones locales seguras de simulación y recuperación.
- `tests/`: pruebas del contrato HTTP y de las operaciones sobre archivos temporales.
- `docs/architecture.md`: arquitectura, límites y decisiones de seguridad.
- `docs/runbook.md`: ejecución paso a paso y pruebas manuales.
- `Guia_Laboratorio v3.pdf`: material original de referencia.

## Requisitos

- Python 3.11 o posterior.
- Entorno virtual recomendado.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
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
