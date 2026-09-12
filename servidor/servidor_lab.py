"""Punto de entrada del servidor V4. Ejecutar desde PC1."""
from lab_v4.server import app

if __name__ == "__main__":
    import os
    app.run(host=os.environ.get("LAB_HOST", "0.0.0.0"), port=int(os.environ.get("LAB_PORT", "5000")))
