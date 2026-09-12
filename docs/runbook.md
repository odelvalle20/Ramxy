# Runbook de demostración

## 1. Preparar el entorno

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
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

## 4. Pruebas de fallo

- Registrar un ID que no siga `LAB-XXXXXX`: debe responder `400`.
- Ordenar `SHELL`, `EXEC` u otra operación: debe responder `400`.
- Ordenar una víctima no registrada: debe responder `404`.
- Detener el servidor: un agente real debe seguir intentando, sin cambiar archivos.
- Reiniciar el servidor y repetir el registro: debe aparecer nuevamente en `/estado`.

## 5. Evidencia recomendada

Conserva una captura de la salida de `py -m pytest -q` y otra de `/estado` después de registrar una víctima. No incluyas datos reales: usa únicamente nombres ficticios y directorios temporales.
