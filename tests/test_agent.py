from pathlib import Path

from lab_v4.agent import execute
from lab_v4.crypto_demo import DEMO_FILENAMES, ensure_demo_files


def test_agent_executes_allowlisted_commands_and_reports_result(tmp_path: Path):
    ensure_demo_files(tmp_path)
    registration = {"id": "LAB-A1B2C3", "hostname": "test"}
    assert execute("CIFRAR_DEMO", tmp_path, "http://127.0.0.1:1", registration) == "CIFRADO_DEMO_COMPLETADO: 3 archivos"
    assert all((tmp_path / "Datos" / (name + ".enc")).exists() for name in DEMO_FILENAMES)
