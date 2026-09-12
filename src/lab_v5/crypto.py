from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

ALLOWED_EXTENSIONS = frozenset({
    ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".gif", ".csv", ".zip",
})
KEY_NAME = "clave_laboratorio.key"
MANIFEST_NAME = "manifest.json"


def lab_base(base: Path | None = None) -> Path:
    return Path(base or os.environ.get("LAB_BASE", "laboratorio"))


def folders(base: Path | None = None) -> tuple[Path, Path, Path, Path]:
    root = lab_base(base)
    originals, encrypted, recovered, keys = (root / name for name in ("originales", "cifrados", "recuperados", "claves"))
    for folder in (originals, encrypted, recovered, keys):
        folder.mkdir(parents=True, exist_ok=True)
    return originals, encrypted, recovered, keys


def key_file(base: Path | None = None) -> Path:
    return folders(base)[3] / KEY_NAME


def load_or_create_key(base: Path | None = None) -> bytes:
    path = key_file(base)
    if path.exists():
        return path.read_bytes()
    key = Fernet.generate_key()
    path.write_bytes(key)
    return key


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def demo_files(base: Path | None = None) -> list[Path]:
    originals, _, _, _ = folders(base)
    sample = originals / "ejemplo.txt"
    if not sample.exists():
        sample.write_text("Archivo ficticio para la demostracion V5.\n", encoding="utf-8")
    return [sample]


def discover(base: Path | None = None) -> list[Path]:
    originals, _, _, _ = folders(base)
    return sorted(path for path in originals.rglob("*") if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS)


def simulate(base: Path | None = None) -> dict:
    originals, _, _, _ = folders(base)
    files = discover(base)
    return {"cantidad": len(files), "archivos": [str(path.relative_to(originals)) for path in files]}


def encrypt_copies(base: Path | None = None) -> dict:
    originals, encrypted, _, _ = folders(base)
    cipher = Fernet(load_or_create_key(base))
    records = []
    for source in discover(base):
        relative = source.relative_to(originals)
        target = encrypted / (str(relative) + ".enc")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(cipher.encrypt(source.read_bytes()))
        records.append({"archivo": str(relative), "cifrado": str(target.relative_to(encrypted)), "sha256": sha256(source)})
    (encrypted / MANIFEST_NAME).write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"cantidad": len(records), "archivos": [record["archivo"] for record in records]}


def recover_copies(base: Path | None = None) -> dict:
    _, encrypted, recovered, _ = folders(base)
    cipher = Fernet(load_or_create_key(base))
    manifest_path = encrypted / MANIFEST_NAME
    records = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    restored = []
    for record in records:
        source = encrypted / record["cifrado"]
        target = recovered / record["archivo"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(cipher.decrypt(source.read_bytes()))
        restored.append({"archivo": record["archivo"], "sha256": sha256(target), "coincide": sha256(target) == record["sha256"]})
    return {"cantidad": len(restored), "archivos": restored}
