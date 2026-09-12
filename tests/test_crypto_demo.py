from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from lab_v4.crypto_demo import (
    DEMO_FILENAMES,
    MARKER_FILENAME,
    encrypt_demo,
    ensure_demo_files,
    key_path,
    recover_demo,
)


def test_encrypts_only_the_three_fixed_demo_files_and_recovers_bytes(tmp_path: Path):
    ensure_demo_files(tmp_path)
    outside = tmp_path / "Datos" / "NO_PROCESAR.txt"
    outside.write_text("fuera de la lista", encoding="utf-8")
    original = {name: (tmp_path / "Datos" / name).read_bytes() for name in DEMO_FILENAMES}

    assert encrypt_demo(tmp_path) == "CIFRADO_DEMO_COMPLETADO: 3 archivos"
    assert all((tmp_path / "Datos" / (name + ".enc")).exists() for name in DEMO_FILENAMES)
    assert all(not (tmp_path / "Datos" / name).exists() for name in DEMO_FILENAMES)
    assert outside.read_text(encoding="utf-8") == "fuera de la lista"
    assert (tmp_path / "Datos" / MARKER_FILENAME).exists()

    assert recover_demo(tmp_path) == "RECUPERACION_DEMO_COMPLETADA: 3 archivos"
    assert original == {name: (tmp_path / "Datos" / name).read_bytes() for name in DEMO_FILENAMES}
    assert not list((tmp_path / "Datos").glob("*.enc"))


def test_key_is_local_and_wrong_key_fails_without_leaving_plaintext(tmp_path: Path):
    ensure_demo_files(tmp_path)
    encrypt_demo(tmp_path)
    key_path(tmp_path).write_bytes(Fernet.generate_key())

    with pytest.raises(ValueError, match="demo.key"):
        recover_demo(tmp_path)
    assert not (tmp_path / "Datos" / DEMO_FILENAMES[0]).exists()
