from __future__ import annotations

import argparse
import getpass

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlador web/API del laboratorio V5")
    parser.add_argument("--server", default="http://127.0.0.1:5000")
    args = parser.parse_args()
    server = args.server.rstrip("/")
    token = getpass.getpass("Token LAB_ADMIN_TOKEN: ")
    headers = {"X-LAB-TOKEN": token}
    while True:
        print("\n=== CONTROLADOR LAB V5 ===")
        print("1. Listar agentes")
        print("2. Simular")
        print("3. Cifrar copias")
        print("4. Recuperar copias")
        print("5. Ver ordenes")
        print("6. Salir")
        option = input("Opcion: ").strip()
        try:
            if option == "1":
                print(requests.get(server + "/api/agentes", headers=headers, timeout=5).json())
            elif option in {"2", "3", "4"}:
                agent = input("ID del agente: ").strip()
                command = {"2": "SIMULAR", "3": "CIFRAR_COPIAS", "4": "RECUPERAR_COPIAS"}[option]
                print(requests.post(server + "/api/ordenes", headers=headers, json={"agente": agent, "comando": command}, timeout=5).json())
            elif option == "5":
                print(requests.get(server + "/api/ordenes", headers=headers, timeout=5).json())
            elif option == "6":
                return
        except requests.RequestException as error:
            print("Servidor no disponible:", error)


if __name__ == "__main__":
    main()
