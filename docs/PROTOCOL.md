# MACS Handshake Protocol 0.1

## Purpose

Establish that a peer knows a provisioned shared secret, confirm the intended recipient, check protocol version, and negotiate the intersection of declared and locally supported capabilities.

## Message fields

- `protocol_version`: currently `0.1`.
- `sender`: stable agent ID plus display and software versions.
- `recipient_id`: intended receiving agent.
- `nonce`: random, unique value of at least 128 bits, encoded as text.
- `timestamp`: Unix timestamp in seconds.
- `capabilities`: bounded list of capability labels.
- `signature`: HMAC-SHA256 over canonical JSON of all fields except the signature.

## Verification order

1. Validate structure and size limits.
2. Confirm the recipient ID.
3. Enforce timestamp clock-skew limits.
4. Verify the HMAC using constant-time comparison.
5. Reject a previously seen `(sender_id, nonce)` pair.
6. Negotiate only the intersection of peer-declared and locally supported capabilities.

## Security boundaries

- Capabilities are descriptive negotiation labels, **not authorization grants**.
- Never accept secrets from an unauthenticated peer or commit secrets to Git.
- Generate nonces with a cryptographically secure random generator.
- The current replay cache is in-memory and is suitable only for a single-process prototype. A network deployment needs persistent, atomic replay protection with expiry.
- Shared-secret provisioning is a bootstrap mechanism. Production deployments should use per-agent credentials, rotation, revocation, TLS, and an auditable authorization gateway.
- Do not expose arbitrary shell, filesystem, smart-home, financial, or device-control tools merely because a peer authenticated.
