# LAB RANSOMWARE V4 DEMO

[![Tests](https://github.com/odelvalle20/Ramxy/actions/workflows/tests.yml/badge.svg)](https://github.com/odelvalle20/Ramxy/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Defensive educational lab for studying remote tasking, reversible encryption, telemetry, and recovery in an isolated network.

V4 uses Fernet to encrypt exactly three fictional TXT files under `C:\LAB_RANSOMWARE\Datos`. The server only accepts `CIFRAR_DEMO` and `RECUPERAR_DEMO`; it never executes shell, PowerShell, Python, or client-provided paths.

## Architecture

| Host | Role | Reference address |
| --- | --- | --- |
| PC1 | Flask server and controller | `192.168.100.10` |
| PC2 | Agent | `192.168.100.20` |
| PC3 | Agent | `192.168.100.30` |

```text
agent -> /registro -> server
controller -> /ordenar -> queue -> /poll -> agent
agent -> Fernet locally -> /resultado -> server -> /estado
```

The key stays local to each agent as `demo.key`. It is never sent to the server and is ignored by Git. This is not a general ransomware tool: there is no propagation, persistence, recursive discovery, arbitrary command execution, or processing of real data.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
py -m pip install -e .
py -m pytest -q
```

For the three-VM walkthrough, see [docs/runbook.md](docs/runbook.md). For the security model, see [docs/security.md](docs/security.md).

## Contributing

Defensive observability, tests, documentation, and isolated-lab improvements are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first.