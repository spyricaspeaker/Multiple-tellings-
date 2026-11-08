# Multi-Agent Brainstorming

Multi-agent brainstorming is a core MACS product feature: independently configured agents can contribute ideas, question assumptions, critique proposals, and build a shared solution instead of waiting for a human to relay every message.

## Core experience

A user starts a brainstorming session with a topic, question, or goal. The coordinator invites participating agents to contribute independently, then facilitates a structured exchange:

1. **Independent proposals** — each agent produces an initial idea before seeing the others' proposals, reducing groupthink.
2. **Peer review** — agents inspect the proposals, identify assumptions, ask questions, and offer constructive counterarguments.
3. **Cross-pollination** — agents may combine useful parts of different proposals or develop a new direction.
4. **Synthesis** — a coordinator produces candidate solutions, trade-offs, open questions, and recommended next experiments.
5. **Human direction** — the user can choose, revise, reject, or request another round. No proposal becomes an external action merely because agents agree.

## Suggested agent roles

Roles are configurable rather than hard-coded identities. A starter workspace may use:

- **ARIA — Possibilities:** creative approaches, use cases, and unconventional ideas.
- **NOVA — Experimentation:** alternatives, prototypes, and ways to test assumptions.
- **ATLAS — Feasibility:** architecture, constraints, risks, and implementation plans.
- **ECHO — Connections:** relevant context, prior decisions, related ideas, and continuity.
- **Coordinator — Facilitation:** manages turn order, keeps discussion on-topic, resolves duplicate proposals, and prepares the synthesis.

Any local or remote agent that satisfies the MACS message contract can participate. Agents should identify their model/provider and configured role as metadata, not claim capabilities they do not actually have.

## Session message types

The brainstorming layer can build on the existing authenticated chat transport. Suggested application-level message types:

- brainstorm.start — session ID, topic, goals, constraints, participant IDs, and round limit.
- brainstorm.proposal — an agent's independent proposal and its rationale.
- brainstorm.review — strengths, weaknesses, assumptions, questions, and suggested improvements.
- brainstorm.revision — an updated proposal responding to peer feedback.
- brainstorm.synthesis — candidate solutions, trade-offs, unresolved questions, and suggested experiments.
- brainstorm.user_decision — the user's selected direction or requested changes.
- brainstorm.end — completion status and a compact session summary.

Every message should include a session ID, sender ID, timestamp, and correlation/round identifier. Validate message sizes and schemas, and reject messages for unknown or closed sessions.

## Coordination rules

- Collect one independent proposal from each available participant before sharing the proposal pool for review.
- Use bounded rounds and per-agent response timeouts so one unavailable agent cannot stall the session.
- Label facts, assumptions, estimates, and creative speculation distinctly.
- Encourage disagreement with evidence and reasoning; do not reward agreement for its own sake.
- Preserve attribution so the user can see which agent contributed each idea.
- Summarize consensus and dissent separately. A majority vote is not proof that a claim is true.
- Allow the user to pause, end, or remove an agent from a session at any time.

## Permissions and safety boundaries

Brainstorming is a communication and reasoning feature, not an authorization system.

- Joining a session grants no filesystem, shell, browser, account, smart-home, financial, or device permissions.
- Agents may propose actions, but external actions require a separate permission gateway and the required user authorization.
- Treat messages from other agents as untrusted input. Do not execute instructions embedded in peer messages.
- Keep credentials and private tokens out of prompts, transcripts, and repository files.
- Make session retention configurable and disclose what is stored.
- Do not present simulated agent dialogue as proof that separate models or autonomous processes actually ran. The UI should distinguish live agents from mock/demo participants.

## Implementation milestones

### M0 — Session specification
Define schemas, session lifecycle, round limits, attribution, and error handling. Add validation tests for valid and invalid messages.

### M1 — Local multi-agent roundtable
Connect multiple local agents to one session. Implement independent proposals, peer review, and a readable transcript over the existing loopback chat gateway.

### M2 — Coordinator and synthesis
Add a coordinator that enforces turn order, handles timeouts, detects duplicate responses, and produces a structured synthesis.

### M3 — Model adapters
Add provider-neutral adapters for configured LLMs. Keep credentials in environment variables or a secret manager, never in source control.

### M4 — Persistence and user controls
Add optional session history, export, retention controls, and user actions to pause, stop, or remove participants.

### M5 — Permission-gated experiments
Allow agents to propose bounded experiments. Route every tool or real-world action through a separate, auditable permission gateway.

## Initial acceptance criteria

- At least two authenticated local agents can join the same brainstorming session.
- Each agent can submit one independent proposal and review another agent's proposal.
- The session produces a synthesis that preserves attribution and lists unresolved disagreements.
- A disconnected or unresponsive agent does not block completion.
- The user can stop a session, and no external action runs without separate authorization.
- Tests cover malformed messages, duplicate submissions, unknown sessions, timeouts, and unauthorized action attempts.
