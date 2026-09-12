from pathlib import Path

from lab_v5.crypto import encrypt_copies, recover_copies, sha256, simulate


def test_v5_preserves_originals_and_recovers_copies(tmp_path: Path):
    originals = tmp_path / "originales"
    originals.mkdir()
    (originals / "demo.txt").write_text("contenido ficticio", encoding="utf-8")
    (originals / "ignored.exe").write_bytes(b"intacto")
    before = sha256(originals / "demo.txt")

    assert simulate(tmp_path)["cantidad"] == 1
    assert encrypt_copies(tmp_path)["cantidad"] == 1
    assert (originals / "demo.txt").exists()
    assert (tmp_path / "cifrados" / "demo.txt.enc").exists()

    result = recover_copies(tmp_path)
    assert result["cantidad"] == 1
    assert result["archivos"][0]["coincide"] is True
    assert sha256(tmp_path / "recuperados" / "demo.txt") == before
    assert (originals / "ignored.exe").read_bytes() == b"intacto"
