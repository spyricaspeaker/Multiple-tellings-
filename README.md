# Multi-Agent Communication System (MACS)

MACS is a small, transport-independent foundation for authenticated communication between independently running AI agents.

## Milestone 0.1

This first milestone defines agent identity, protocol compatibility, signed handshake messages, and a local replay guard. It deliberately does **not** grant agents unrestricted access to devices, accounts, files, or the network. Capabilities are declarations, not permissions. Any real-world action must be mediated by a separate policy/consent gateway.

## Repository layout

- `src/macs/models.py` — typed handshake data structures.
- `src/macs/handshake.py` — HMAC signing, verification, compatibility checks, and replay protection.
- `src/macs/local_chat.py` — authenticated loopback WebSocket chat for local agents.
- `docs/LOCAL_AGENTS.md` — setup and client connection guide.
- `tests/` — automated tests for valid and invalid handshakes.
- `docs/PROTOCOL.md` — protocol behavior and security boundaries.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
pytest
```

The two agents must independently provision the same high-entropy shared secret over a trusted channel. Do not commit secrets or put them in source code. For production, replace shared-secret provisioning with a managed identity system and rotate credentials.

## Add local agents to chat

See [docs/LOCAL_AGENTS.md](docs/LOCAL_AGENTS.md) for starting the local WebSocket chat gateway and connecting any local process with a private join token. The default listener is loopback-only.

## Current status

Protocol/library prototype only. No public network listener or autonomous tool execution is included yet.
