from __future__ import annotations

from pathlib import Path

MARKER_NAME = "SIMULACION_RANSOMWARE.txt"


def _files_in_lab(data_dir: Path) -> list[Path]:
    data_dir = data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return sorted(
        path
        for path in data_dir.rglob("*")
        if path.is_file() and path.name != MARKER_NAME and not path.name.endswith(".simulado")
    )


def simulate(data_dir: Path) -> str:
    affected: list[str] = []
    for source in _files_in_lab(data_dir):
        destination = source.with_name(source.name + ".simulado")
        source.rename(destination)
        affected.append(destination.name)

    marker = data_dir / MARKER_NAME
    marker.write_text(
        "SIMULACION CONTROLADA\n"
        "Los archivos fueron renombrados; no fueron cifrados.\n"
        f"Archivos afectados: {len(affected)}\n",
        encoding="utf-8",
    )
    return f"SIMULACION_COMPLETADA: {len(affected)} archivos"


def recover(data_dir: Path) -> str:
    recovered: list[str] = []
    data_dir = data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(data_dir.rglob("*.simulado")):
        destination = source.with_name(source.name.removesuffix(".simulado"))
        if not destination.exists():
            source.rename(destination)
            recovered.append(destination.name)

    marker = data_dir / MARKER_NAME
    marker.unlink(missing_ok=True)
    return f"RECUPERACION_COMPLETADA: {len(recovered)} archivos"
