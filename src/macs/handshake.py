"""Handshake signing and verification for MACS v0.1."""

import hashlib
import hmac
import json
import time
from collections.abc import Iterable

from .models import HandshakeMessage, HandshakeResult


class HandshakeError(ValueError):
    """Raised when a handshake fails validation."""


def _canonical_bytes(message: HandshakeMessage) -> bytes:
    return json.dumps(
        message.unsigned_payload(), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sign_handshake(message: HandshakeMessage, shared_secret: bytes) -> HandshakeMessage:
    """Return a copy of message signed with HMAC-SHA256."""
    if len(shared_secret) < 32:
        raise HandshakeError("shared_secret must be at least 32 bytes")
    signature = hmac.new(shared_secret, _canonical_bytes(message), hashlib.sha256).hexdigest()
    return HandshakeMessage(
        protocol_version=message.protocol_version,
        sender=message.sender,
        recipient_id=message.recipient_id,
        nonce=message.nonce,
        timestamp=message.timestamp,
        capabilities=message.capabilities,
        signature=signature,
    )


class HandshakeVerifier:
    """Verify signed requests and reject stale or replayed nonces."""

    def __init__(
        self,
        *,
        local_agent_id: str,
        shared_secret: bytes,
        supported_capabilities: Iterable[str] = (),
        clock_skew_seconds: int = 60,
    ) -> None:
        if len(shared_secret) < 32:
            raise HandshakeError("shared_secret must be at least 32 bytes")
        if clock_skew_seconds < 0:
            raise ValueError("clock_skew_seconds cannot be negative")
        self.local_agent_id = local_agent_id
        self._secret = shared_secret
        self._capabilities = frozenset(supported_capabilities)
        self._clock_skew = clock_skew_seconds
        self._seen_nonces: set[tuple[str, str]] = set()

    def verify(self, message: HandshakeMessage, *, now: int | None = None) -> HandshakeResult:
        current_time = int(time.time()) if now is None else now
        if message.recipient_id != self.local_agent_id:
            raise HandshakeError("handshake addressed to a different agent")
        if abs(current_time - message.timestamp) > self._clock_skew:
            raise HandshakeError("handshake timestamp outside allowed clock skew")
        expected = hmac.new(self._secret, _canonical_bytes(message), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, message.signature):
            raise HandshakeError("invalid handshake signature")
        nonce_key = (message.sender.agent_id, message.nonce)
        if nonce_key in self._seen_nonces:
            raise HandshakeError("replayed handshake nonce")
        self._seen_nonces.add(nonce_key)
        negotiated = tuple(sorted(set(message.capabilities) & self._capabilities))
        return HandshakeResult(
            accepted=True,
            agent_id=message.sender.agent_id,
            protocol_version=message.protocol_version,
            negotiated_capabilities=negotiated,
            reason="authenticated; capabilities intersected with local support",
        )
