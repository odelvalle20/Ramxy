from __future__ import annotations

import json
import os
import socket
import uuid
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

DEMO_FILENAMES = (
    "DEMO_LAB_documento1.txt",
    "DEMO_LAB_documento2.txt",
    "DEMO_LAB_reporte.txt",
)
KEY_FILENAME = "demo.key"
REGISTRATION_FILENAME = "registro_victima.json"
MARKER_FILENAME = "DEMO_CIFRADO_RANSOMWARE.txt"


def demo_base() -> Path:
    return Path(os.environ.get("LAB_BASE", r"C:\LAB_RANSOMWARE"))


def data_dir(base: Path | None = None) -> Path:
    path = (base or demo_base()) / "Datos"
    path.mkdir(parents=True, exist_ok=True)
    return path


def key_path(base: Path | None = None) -> Path:
    path = base or demo_base()
    path.mkdir(parents=True, exist_ok=True)
    return path / KEY_FILENAME


def load_or_create_key(base: Path | None = None) -> bytes:
    path = key_path(base)
    if path.exists():
        return path.read_bytes()
    key = Fernet.generate_key()
    path.write_bytes(key)
    return key


def ensure_demo_files(base: Path | None = None) -> list[Path]:
    folder = data_dir(base)
    samples = {
        DEMO_FILENAMES[0]: "Contenido ficticio del documento 1.\n",
        DEMO_FILENAMES[1]: "Contenido ficticio del documento 2.\n",
        DEMO_FILENAMES[2]: "Reporte ficticio del laboratorio V4.\n",
    }
    paths: list[Path] = []
    for name, content in samples.items():
        path = folder / name
        if not path.exists() and not path.with_name(name + ".enc").exists():
            path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def encrypt_demo(base: Path | None = None) -> str:
    folder = data_dir(base)
    cipher = Fernet(load_or_create_key(base))
    processed: list[str] = []
    for name in DEMO_FILENAMES:
        source = folder / name
        encrypted = folder / (name + ".enc")
        if source.exists() and not encrypted.exists():
            encrypted.write_bytes(cipher.encrypt(source.read_bytes()))
            source.unlink()
            processed.append(encrypted.name)
    marker = folder / MARKER_FILENAME
    marker.write_text(
        "DEMO CRIPTOGRAFICA CONTROLADA\n"
        "Solo se procesan los tres nombres DEMO_LAB_*.txt.\n"
        f"Archivos cifrados: {len(processed)}\n",
        encoding="utf-8",
    )
    return f"CIFRADO_DEMO_COMPLETADO: {len(processed)} archivos"


def recover_demo(base: Path | None = None) -> str:
    folder = data_dir(base)
    cipher = Fernet(load_or_create_key(base))
    processed: list[str] = []
    for name in DEMO_FILENAMES:
        encrypted = folder / (name + ".enc")
        restored = folder / name
        if encrypted.exists() and not restored.exists():
            try:
                restored.write_bytes(cipher.decrypt(encrypted.read_bytes()))
            except InvalidToken as error:
                restored.unlink(missing_ok=True)
                raise ValueError("demo.key no corresponde a los archivos .enc") from error
            encrypted.unlink()
            processed.append(restored.name)
    (folder / MARKER_FILENAME).unlink(missing_ok=True)
    return f"RECUPERACION_DEMO_COMPLETADA: {len(processed)} archivos"


def load_or_create_registration(base: Path | None = None) -> dict[str, str]:
    path = (base or demo_base()) / REGISTRATION_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    registration = {"id": "LAB-" + uuid.uuid4().hex[:6].upper(), "hostname": socket.gethostname()}
    path.write_text(json.dumps(registration, indent=2), encoding="utf-8")
    return registration
