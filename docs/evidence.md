# Evidencia

## Validación automatizada

Ejecutar:

```text
py -m pytest -q
```

La suite valida:

- cifrado Fernet de exactamente tres nombres;
- recuperación byte a byte;
- aislamiento de archivos fuera de la allowlist;
- fallo seguro con clave equivocada;
- registro, cola, polling, resultado y rechazo de comandos arbitrarios;
- ejecución local del agente aunque el reporte HTTP no esté disponible.

## Evidencia manual

Captura estos estados en una red privada con archivos ficticios:

1. PC2 y PC3 visibles como `CONECTADO`.
2. Los tres TXT antes de `CIFRAR_DEMO`.
3. Los tres `.enc` después del polling.
4. Estado `CIFRADO_DEMO_COMPLETADO`.
5. Los TXT restaurados después de `RECUPERAR_DEMO`.

No incluyas claves, datos personales ni rutas de usuario en las capturas.
