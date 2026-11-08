# Multi-Agent Communication System (MACS)

MACS is a transport-independent foundation for authenticated communication between independently running AI agents. Its core product experience is **multi-agent brainstorming**: agents independently propose ideas, challenge one another, combine useful insights, and synthesize solutions for the user.

## Core feature: Multi-Agent Brainstorming

A user starts a session with a question or goal. Participating agents contribute independent proposals, review and improve one another's work, and produce an attributed synthesis that separates agreement, disagreement, assumptions, and next experiments.

The starter roles are configurable:
- **ARIA:** creative possibilities and alternative approaches.
- **NOVA:** experimentation, prototypes, and assumption testing.
- **ATLAS:** technical feasibility, architecture, and constraints.
- **ECHO:** context, connections, and continuity.
- **Coordinator:** facilitation, bounded rounds, and final synthesis.

Agents can be local or remote as long as they satisfy the MACS protocol. The brainstorming feature does not itself grant tool permissions. External actions must pass through a separate authorization gateway.

See [docs/MULTI_AGENT_BRAINSTORMING.md](docs/MULTI_AGENT_BRAINSTORMING.md) for the workflow, message types, coordination rules, safety boundaries, milestones, and acceptance criteria.

## Milestone 0.1

The initial protocol defines agent identity, protocol compatibility, signed handshake messages, and a local replay guard. It deliberately does **not** grant agents unrestricted access to devices, accounts, files, or the network. Capabilities are declarations, not permissions. Any real-world action must be mediated by a separate policy/consent gateway.

## Repository layout

- `src/macs/models.py` — typed handshake data structures.
- `src/macs/handshake.py` — HMAC signing, verification, compatibility checks, and replay protection.
- `src/macs/local_chat.py` — authenticated loopback WebSocket chat for local agents.
- `docs/MULTI_AGENT_BRAINSTORMING.md` — core brainstorming feature specification and implementation plan.
- `docs/LOCAL_AGENTS.md` — setup and client connection guide.
- `tests/` — automated tests for valid and invalid handshakes.

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

Protocol/library prototype only. The brainstorming workflow is specified as a core feature; its session coordinator, proposal/review message types, and synthesis engine are planned milestones, not yet implemented. No public network listener or autonomous tool execution is included yet.
