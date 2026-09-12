from pathlib import Path

from lab_v4.server import create_app

VICTIM = {"id": "LAB-A1B2C3", "hostname": "victima-demo", "ip": "192.168.100.20"}


def test_v4_registration_queue_and_result_flow(tmp_path: Path):
    client = create_app(tmp_path / "victimas.json").test_client()

    assert client.post("/registro", json=VICTIM).status_code == 200
    assert client.post("/ordenar", json={"id": VICTIM["id"], "comando": "CIFRAR_DEMO"}).status_code == 200
    assert client.post("/poll", json={"id": VICTIM["id"]}).get_json()["comando"] == "CIFRAR_DEMO"
    assert client.post("/resultado", json={"id": VICTIM["id"], "estado": "CIFRADO_DEMO_COMPLETADO", "resultado": "3 archivos"}).status_code == 200
    assert client.get("/estado").get_json()[VICTIM["id"]]["estado"] == "CIFRADO_DEMO_COMPLETADO"

    assert client.post("/ordenar", json={"id": VICTIM["id"], "comando": "RECUPERAR_DEMO"}).status_code == 200
    assert client.post("/poll", json={"id": VICTIM["id"]}).get_json()["comando"] == "RECUPERAR_DEMO"


def test_server_rejects_arbitrary_commands_and_unknown_ids(tmp_path: Path):
    client = create_app(tmp_path / "victimas.json").test_client()

    assert client.post("/registro", json={"id": "INVALIDO"}).status_code == 400
    assert client.post("/ordenar", json={"id": VICTIM["id"], "comando": "POWERSHELL"}).status_code == 400
    assert client.post("/ordenar", json={"id": VICTIM["id"], "comando": "CIFRAR_DEMO"}).status_code == 404
