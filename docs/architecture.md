# Arquitectura V4

## Topología

```text
PC1 192.168.100.10:5000
├── Flask: servidor_lab.py
└── Consola: Controlador.py

PC2 192.168.100.20              PC3 192.168.100.30
└── agente_lab.py/.exe           └── agente_lab.py/.exe
```

Todos los equipos deben estar en una red privada Host-Only o interna. PC2 y PC3 inician la comunicación hacia PC1; el servidor no inicia conexiones hacia las víctimas.

## Flujo

1. El agente crea o lee `registro_victima.json` y conserva un ID `LAB-XXXXXX`.
2. El agente hace `POST /registro` con ID y hostname.
3. El controlador obtiene víctimas con `GET /estado`.
4. El controlador pone en cola `CIFRAR_DEMO` o `RECUPERAR_DEMO` mediante `POST /ordenar`.
5. El agente consulta `POST /poll` cada tres segundos y consume una orden.
6. El agente ejecuta una función local de `crypto_demo.py`.
7. El agente informa el estado por `POST /resultado`.

## Contrato HTTP

| Método y ruta | Propósito | Restricción |
| --- | --- | --- |
| `GET /estado` | Ver víctimas y telemetría | Solo lectura |
| `POST /registro` | Registrar agente | ID `LAB-[A-F0-9]{6}` |
| `POST /poll` | Entregar una orden | Una orden se consume una vez |
| `POST /ordenar` | Encolar tarea | Solo dos literales permitidos |
| `POST /resultado` | Guardar estado y resultado | Requiere víctima registrada |

La allowlist del servidor es exactamente:

```text
CIFRAR_DEMO
RECUPERAR_DEMO
```

No existe un endpoint que reciba o ejecute una cadena de shell, PowerShell, Python o una ruta proporcionada por el cliente.

## Cifrado y recuperación

El agente trabaja únicamente sobre estos nombres en `LAB_BASE\Datos`:

```text
DEMO_LAB_documento1.txt
DEMO_LAB_documento2.txt
DEMO_LAB_reporte.txt
```

`CIFRAR_DEMO` lee cada TXT, lo cifra con Fernet, escribe `nombre.txt.enc` y elimina el TXT original. La clave se genera una vez en `LAB_BASE\demo.key` y permanece local al agente. El servidor solo coordina órdenes y recibe telemetría.

`RECUPERAR_DEMO` descifra cada `.enc` con la misma clave, recrea el TXT original y elimina el `.enc`. Una clave equivocada produce un error y no deja un archivo plano parcial.

La lista cerrada evita búsqueda recursiva y limita la demo a tres archivos didácticos. El contenido de esos archivos debe ser ficticio.
