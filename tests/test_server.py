from pathlib import Path

from lab_sim.server import create_app


VICTIM = {"id": "LAB-A1B2C3", "hostname": "victima-demo", "ip": "127.0.0.1"}


def test_register_poll_order_and_result_flow(tmp_path: Path):
    client = create_app(tmp_path).test_client()

    registered = client.post("/registro", json=VICTIM)
    assert registered.status_code == 200
    assert registered.get_json() == {"ok": True}

    queued = client.post("/ordenar", json={"id": VICTIM["id"], "comando": "SIMULAR"})
    assert queued.status_code == 200

    polled = client.post("/poll", json={"id": VICTIM["id"]})
    assert polled.status_code == 200
    assert polled.get_json()["comando"] == "SIMULAR"

    completed = client.post(
        "/resultado",
        json={"id": VICTIM["id"], "estado": "SIMULACION_COMPLETADA", "resultado": "2 archivos"},
    )
    assert completed.status_code == 200
    state = client.get("/estado").get_json()[VICTIM["id"]]
    assert state["estado"] == "SIMULACION_COMPLETADA"
    assert state["ultimo_resultado"] == "2 archivos"


def test_rejects_invalid_ids_unknown_victims_and_commands(tmp_path: Path):
    client = create_app(tmp_path).test_client()

    assert client.post("/registro", json={"id": "INVALIDO"}).status_code == 400
    assert client.post("/ordenar", json={"id": VICTIM["id"], "comando": "SHELL"}).status_code == 400
    assert client.post("/ordenar", json={"id": VICTIM["id"], "comando": "SIMULAR"}).status_code == 404
    assert client.post("/poll", json={"id": VICTIM["id"]}).status_code == 404
