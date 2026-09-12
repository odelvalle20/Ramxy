from pathlib import Path

from lab_sim.agent_operations import MARKER_NAME, recover, simulate


def test_simulate_only_renames_files_inside_lab(tmp_path: Path):
    data_dir = tmp_path / "Datos"
    data_dir.mkdir()
    (data_dir / "documento1.txt").write_text("ficticio", encoding="utf-8")
    (data_dir / "ejemplo.pdf").write_bytes(b"pdf ficticio")
    outside = tmp_path / "fuera.txt"
    outside.write_text("intacto", encoding="utf-8")

    result = simulate(data_dir)

    assert result == "SIMULACION_COMPLETADA: 2 archivos"
    assert not (data_dir / "documento1.txt").exists()
    assert (data_dir / "documento1.txt.simulado").exists()
    assert (data_dir / "ejemplo.pdf.simulado").exists()
    assert (data_dir / MARKER_NAME).exists()
    assert outside.read_text(encoding="utf-8") == "intacto"


def test_recover_restores_files_and_removes_marker(tmp_path: Path):
    data_dir = tmp_path / "Datos"
    data_dir.mkdir()
    (data_dir / "documento1.txt").write_text("ficticio", encoding="utf-8")

    simulate(data_dir)
    result = recover(data_dir)

    assert result == "RECUPERACION_COMPLETADA: 1 archivos"
    assert (data_dir / "documento1.txt").exists()
    assert not (data_dir / "documento1.txt.simulado").exists()
    assert not (data_dir / MARKER_NAME).exists()
