from __future__ import annotations

import json
import os
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ALLOWED_COMMANDS = frozenset({"SIMULAR", "CIFRAR_COPIAS", "RECUPERAR_COPIAS"})


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def create_app(state_path: Path | None = None, admin_token: str | None = None) -> Flask:
    state_path = Path(state_path or os.environ.get("LAB_STATE", "registros/state.json"))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    token = admin_token or os.environ.get("LAB_ADMIN_TOKEN", "CAMBIA_ESTE_TOKEN")
    lock = threading.Lock()
    agents: dict[str, dict] = {}
    orders: list[dict] = []
    app = Flask(__name__, template_folder="../../web")

    def authorized() -> bool:
        return secrets.compare_digest(request.headers.get("X-LAB-TOKEN", ""), token)

    def persist() -> None:
        state_path.write_text(json.dumps({"agentes": agents, "ordenes": orders[-100:]}, indent=2, ensure_ascii=False), encoding="utf-8")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/salud")
    def health():
        return jsonify(estado="activo", hora=now(), version="V5")

    @app.post("/api/agentes/registrar")
    def register():
        payload = request.get_json(silent=True) or {}
        agent_id = str(payload.get("id", "")).strip()
        if not agent_id:
            return jsonify(error="Falta el ID del agente"), 400
        with lock:
            agents[agent_id] = {"id": agent_id, "equipo": payload.get("equipo", "desconocido"), "ip": request.remote_addr, "ultima_conexion": now(), "estado": "CONECTADO"}
            persist()
        return jsonify(ok=True)

    @app.post("/api/poll")
    def poll():
        payload = request.get_json(silent=True) or {}
        agent_id = str(payload.get("id", "")).strip()
        with lock:
            if agent_id not in agents:
                return jsonify(error="Agente no registrado"), 404
            agents[agent_id].update(ultima_conexion=now(), estado="CONECTADO")
            pending = next((order for order in orders if order["agente"] == agent_id and order["estado"] == "PENDIENTE"), None)
            if pending:
                pending["estado"] = "ENTREGADA"
                pending["entregada"] = now()
            persist()
        return jsonify(comando=pending["comando"] if pending else None, orden_id=pending["id"] if pending else None)

    @app.post("/api/resultado")
    def result():
        payload = request.get_json(silent=True) or {}
        order_id = payload.get("orden_id")
        with lock:
            order = next((item for item in orders if item["id"] == order_id), None)
            if not order:
                return jsonify(error="Orden no encontrada"), 404
            order.update(estado=payload.get("estado", "COMPLETADA"), resultado=payload.get("resultado", ""), finalizada=now())
            persist()
        return jsonify(ok=True)

    @app.get("/api/agentes")
    def list_agents():
        if not authorized():
            return jsonify(error="No autorizado"), 401
        return jsonify(list(agents.values()))

    @app.get("/api/ordenes")
    def list_orders():
        if not authorized():
            return jsonify(error="No autorizado"), 401
        return jsonify(list(reversed(orders[-50:])))

    @app.post("/api/ordenes")
    def create_order():
        if not authorized():
            return jsonify(error="No autorizado"), 401
        payload = request.get_json(silent=True) or {}
        command, agent_id = payload.get("comando"), payload.get("agente")
        if command not in ALLOWED_COMMANDS:
            return jsonify(error="Comando no permitido"), 400
        if agent_id not in agents:
            return jsonify(error="Agente no registrado"), 404
        order = {"id": secrets.token_hex(8), "agente": agent_id, "comando": command, "estado": "PENDIENTE", "creada": now()}
        orders.append(order)
        persist()
        return jsonify(order), 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("LAB_HOST", "127.0.0.1"), port=int(os.environ.get("LAB_PORT", "5000")), debug=False)
