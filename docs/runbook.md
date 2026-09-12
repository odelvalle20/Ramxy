# Runbook de demostración

## 1. Preparar el entorno

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
py -m pip install -e .
```

## 2. Ejecutar las pruebas

```powershell
py -m pytest -q
```

Resultado esperado: todas las pruebas pasan y no se modifica ningún archivo fuera de los directorios temporales creados por pytest.

## 3. Probar el flujo HTTP

En una terminal:

```powershell
$env:LAB_DATA_DIR = "$PWD\.lab-data"
py -m lab_sim.server
```

En otra terminal:

```powershell
$body = @{ id = 'LAB-A1B2C3'; hostname = 'victima-demo' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/registro -Method Post -ContentType 'application/json' -Body $body

$body = @{ id = 'LAB-A1B2C3'; comando = 'SIMULAR' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/ordenar -Method Post -ContentType 'application/json' -Body $body
Invoke-RestMethod http://127.0.0.1:5000/estado
```

## 4. Simular y recuperar

La orden de simulación no encripta el contenido. Para demostrar la operación local sobre archivos ficticios, crea una carpeta temporal y llama a las funciones:

```powershell
@("documento1.txt", "documento2.txt") | ForEach-Object { New-Item -ItemType File -Path ".lab-data\Datos\$_" -Force }
py -c "from pathlib import Path; from lab_sim.agent_operations import simulate, recover; p=Path('.lab-data/Datos'); print(simulate(p)); print(recover(p))"
```

El resultado esperado es `SIMULACION_COMPLETADA: 2 archivos` seguido de `RECUPERACION_COMPLETADA: 2 archivos`. Durante la simulación los nombres terminan en `.simulado`; el contenido no se cifra ni se elimina. La recuperación quita ese sufijo y borra el marcador `SIMULACION_RANSOMWARE.txt`.

## 5. Pruebas de fallo

- Registrar un ID que no siga `LAB-XXXXXX`: debe responder `400`.
- Ordenar `SHELL`, `EXEC` u otra operación: debe responder `400`.
- Ordenar una víctima no registrada: debe responder `404`.
- Detener el servidor: un agente real debe seguir intentando, sin cambiar archivos.
- Reiniciar el servidor y repetir el registro: debe aparecer nuevamente en `/estado`.

## 6. Evidencia recomendada

Conserva una captura de la salida de `py -m pytest -q` y otra de `/estado` después de registrar una víctima. No incluyas datos reales: usa únicamente nombres ficticios y directorios temporales.
