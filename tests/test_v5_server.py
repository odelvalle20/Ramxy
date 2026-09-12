from pathlib import Path

from lab_v5.server import create_app


def test_v5_authentication_and_agent_order_flow(tmp_path: Path):
    client = create_app(tmp_path / "state.json", "secret").test_client()
    assert client.get("/api/salud").get_json()["version"] == "V5"
    assert client.post("/api/agentes/registrar", json={"id": "agent-1", "equipo": "PC2"}).status_code == 200
    assert client.get("/api/agentes").status_code == 401
    headers = {"X-LAB-TOKEN": "secret"}
    order = client.post("/api/ordenes", headers=headers, json={"agente": "agent-1", "comando": "CIFRAR_COPIAS"})
    assert order.status_code == 201
    order_id = order.get_json()["id"]
    poll = client.post("/api/poll", json={"id": "agent-1"}).get_json()
    assert poll["comando"] == "CIFRAR_COPIAS"
    assert poll["orden_id"] == order_id
    assert client.post("/api/resultado", json={"orden_id": order_id, "estado": "OK", "resultado": "1"}).status_code == 200


def test_v5_rejects_unknown_commands_and_agents(tmp_path: Path):
    client = create_app(tmp_path / "state.json", "secret").test_client()
    headers = {"X-LAB-TOKEN": "secret"}
    assert client.post("/api/ordenes", headers=headers, json={"agente": "missing", "comando": "SIMULAR"}).status_code == 404
    assert client.post("/api/ordenes", headers=headers, json={"agente": "missing", "comando": "SHELL"}).status_code == 400
