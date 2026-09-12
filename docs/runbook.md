# Runbook V4

## 1. Preparar la red

Crea tres VMs o equipos autorizados en una red Host-Only/interna. No uses carpetas compartidas con datos reales y no publiques el puerto 5000 en Internet.

- PC1: servidor y controlador.
- PC2: agente.
- PC3: agente.

En PC1 confirma la IP con `ipconfig`. Si no es `192.168.100.10`, pasa la URL correcta con `--server`.

## 2. Instalar dependencias

En PC1:

```powershell
py -m pip install flask requests cryptography
```

En PC2 y PC3:

```powershell
py -m pip install requests cryptography
```

Para desarrollo y pruebas locales:

```powershell
py -m pip install -r requirements-dev.txt
py -m pip install -e .
py -m pytest -q
```

## 3. Iniciar PC1

Desde la raíz del repo:

```powershell
$env:LAB_DB = 'C:\LAB_RANSOMWARE\Servidor\victimas.json'
py servidor\servidor_lab.py
```

El servidor escucha en `0.0.0.0:5000`. En una red privada, permite TCP 5000 únicamente en el perfil privado de Windows Firewall si hace falta.

En otra consola de PC1:

```powershell
py servidor\Controlador.py --server http://192.168.100.10:5000
```

## 4. Iniciar PC2 y PC3

En cada VM, usa una base propia. El agente crea los tres TXT ficticios, `registro_victima.json` y `demo.key`.

PC2:

```powershell
py agente\agente_lab.py --server http://192.168.100.10:5000 --base C:\LAB_RANSOMWARE
```

PC3 debe usar su propia carpeta local y puede iniciar con el mismo comando. No copies `demo.key` entre víctimas: cada agente tiene su propia clave.

Para una prueba de una sola consulta, útil durante desarrollo:

```powershell
py agente\agente_lab.py --server http://127.0.0.1:5000 --base .lab-data --once
```

## 5. Demostración

1. En el controlador selecciona `1` y verifica PC2/PC3 en estado `CONECTADO`.
2. Abre los tres TXT ficticios y confirma que contienen texto de laboratorio.
3. Selecciona `2`, introduce un ID y envía `CIFRAR_DEMO`.
4. Espera el siguiente polling y comprueba los tres archivos `.enc`.
5. Consulta el estado: debe mostrar `CIFRADO_DEMO_COMPLETADO`.
6. Selecciona `3`, introduce el mismo ID y envía `RECUPERAR_DEMO`.
7. Comprueba que reaparecen los TXT y desaparecen los `.enc`.

## 6. Generar el EXE opcional

En una máquina de preparación con Python:

```powershell
py -m pip install requests cryptography pyinstaller
pyinstaller --onefile --noconsole agente\agente_lab.py
```

Prueba primero el `.py`. Copia manualmente el EXE a las VMs autorizadas. No se incorpora persistencia automática.

## 7. Fallos esperados

- Comando `POWERSHELL`, `SHELL` o cualquier otro: HTTP `400`, `Comando no permitido`.
- ID no registrado: HTTP `404`.
- Servidor apagado: el agente continúa intentando sin modificar archivos.
- Clave `demo.key` sustituida: recuperación falla con error de token y no crea un TXT plano parcial.
- Archivo fuera de los tres nombres permitidos: permanece intacto.
