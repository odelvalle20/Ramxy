# Correspondencia con la guía V4

| Elemento de la guía | Implementación |
| --- | --- |
| PC1 servidor + controlador | `servidor/servidor_lab.py` y `servidor/Controlador.py` |
| PC2/PC3 agente | `agente/agente_lab.py` |
| `192.168.100.10:5000` | Valor predeterminado del CLI; configurable con `--server` |
| ID `LAB-XXXXXX` | Generado y guardado en `registro_victima.json` |
| Polling de 3 segundos | `--interval 3` por defecto |
| `CIFRAR_DEMO` | Fernet sobre tres TXT exactos |
| `RECUPERAR_DEMO` | Descifra con la misma `demo.key` y elimina `.enc` |
| Clave local | `LAB_BASE\demo.key`, ignorada por Git |
| Estado | `victimas.json`, ignorado por Git |
| PyInstaller | Instrucción en `docs/runbook.md` |
| Pruebas de fallo | Tests y sección de fallos del runbook |

La implementación conserva los límites de la guía: no hay comandos arbitrarios, persistencia automática, propagación ni procesamiento fuera de los datos ficticios de la demo.
