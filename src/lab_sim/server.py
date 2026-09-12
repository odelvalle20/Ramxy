from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

_ID_PATTERN = re.compile(r"LAB-[A-F0-9]{6}")


def create_app(data_dir: Path | None = None) -> Flask:
    data_dir = Path(data_dir or os.environ.get("LAB_DATA_DIR", ".lab-data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    database = data_dir / "victimas.json"
    lock = threading.Lock()
    pending: dict[str, str] = {}
    app = Flask(__name__)

    def load_database() -> dict:
        if not database.exists():
            return {}
        return json.loads(database.read_text(encoding="utf-8"))

    def save_database(value: dict) -> None:
        temporary = database.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(database)

    def valid_id(value: str | None) -> bool:
        return bool(_ID_PATTERN.fullmatch(value or ""))

    @app.get("/estado")
    def state():
        return jsonify(load_database())

    @app.post("/registro")
    def register():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        if not valid_id(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        with lock:
            database_value = load_database()
            previous = database_value.get(victim_id, {})
            database_value[victim_id] = {
                "id": victim_id,
                "hostname": payload.get("hostname", ""),
                "ip": payload.get("ip", ""),
                "estado": "CONECTADO",
                "ultima_conexion": datetime.now().isoformat(timespec="seconds"),
                "ultimo_resultado": previous.get("ultimo_resultado", ""),
            }
            save_database(database_value)
        return jsonify(ok=True)

    @app.post("/poll")
    def poll():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        if not valid_id(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        with lock:
            database_value = load_database()
            if victim_id not in database_value:
                return jsonify(ok=False, error="No registrado"), 404
            database_value[victim_id]["estado"] = "CONECTADO"
            database_value[victim_id]["ultima_conexion"] = datetime.now().isoformat(timespec="seconds")
            save_database(database_value)
            command = pending.pop(victim_id, None)
        return jsonify(ok=True, comando=command)

    @app.post("/ordenar")
    def order():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        command = payload.get("comando")
        if not valid_id(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        if command not in ("SIMULAR", "RECUPERAR"):
            return jsonify(ok=False, error="Operacion no permitida"), 400
        with lock:
            database_value = load_database()
            if victim_id not in database_value:
                return jsonify(ok=False, error="No registrado"), 404
            pending[victim_id] = command
        return jsonify(ok=True, mensaje=f"{command} puesta en cola")

    @app.post("/resultado")
    def result():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        if not valid_id(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        with lock:
            database_value = load_database()
            if victim_id not in database_value:
                return jsonify(ok=False, error="No registrado"), 404
            database_value[victim_id]["estado"] = payload.get("estado", "FINALIZADO")
            database_value[victim_id]["ultimo_resultado"] = payload.get("resultado", "")
            database_value[victim_id]["ultima_conexion"] = datetime.now().isoformat(timespec="seconds")
            save_database(database_value)
        return jsonify(ok=True)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("LAB_HOST", "127.0.0.1"), port=int(os.environ.get("LAB_PORT", "5000")))
