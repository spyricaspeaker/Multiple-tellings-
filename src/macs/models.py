"""Typed data models for MACS protocol v0.1."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    display_name: str
    software_version: str

    def __post_init__(self) -> None:
        for field_name in ("agent_id", "display_name", "software_version"):
            value = getattr(self, field_name)
            if not value or len(value) > 128:
                raise ValueError(f"{field_name} must contain 1-128 characters")


@dataclass(frozen=True)
class HandshakeMessage:
    protocol_version: str
    sender: AgentIdentity
    recipient_id: str
    nonce: str
    timestamp: int
    capabilities: tuple[str, ...]
    signature: str = ""

    def __post_init__(self) -> None:
        if self.protocol_version != "0.1":
            raise ValueError("protocol_version must be 0.1 for this implementation")
        if not self.recipient_id or len(self.recipient_id) > 128:
            raise ValueError("recipient_id must contain 1-128 characters")
        if len(self.nonce) < 16 or len(self.nonce) > 128:
            raise ValueError("nonce must contain 16-128 characters")
        if len(self.capabilities) > 64:
            raise ValueError("at most 64 capabilities may be declared")
        if any(not item or len(item) > 64 for item in self.capabilities):
            raise ValueError("each capability must contain 1-64 characters")

    def unsigned_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("signature", None)
        payload["capabilities"] = sorted(self.capabilities)
        return payload


@dataclass(frozen=True)
class HandshakeResult:
    accepted: bool
    agent_id: str
    protocol_version: str
    negotiated_capabilities: tuple[str, ...]
    reason: str
