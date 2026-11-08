import pytest

from macs import AgentIdentity, HandshakeError, HandshakeMessage, HandshakeVerifier, sign_handshake

SECRET = b"test-only-secret-material-at-least-32-bytes"


def make_message(**overrides):
    values = dict(
        protocol_version="0.1",
        sender=AgentIdentity("aria", "ARIA", "0.1.0"),
        recipient_id="nova",
        nonce="0123456789abcdef0123456789abcdef",
        timestamp=1_700_000_000,
        capabilities=("chat", "status"),
    )
    values.update(overrides)
    return HandshakeMessage(**values)


def test_valid_handshake_negotiates_intersection():
    verifier = HandshakeVerifier(
        local_agent_id="nova", shared_secret=SECRET, supported_capabilities=("chat", "telemetry")
    )
    signed = sign_handshake(make_message(), SECRET)
    result = verifier.verify(signed, now=1_700_000_000)
    assert result.accepted is True
    assert result.agent_id == "aria"
    assert result.negotiated_capabilities == ("chat",)


def test_invalid_signature_is_rejected():
    verifier = HandshakeVerifier(local_agent_id="nova", shared_secret=SECRET)
    with pytest.raises(HandshakeError, match="signature"):
        verifier.verify(make_message(signature="bad"), now=1_700_000_000)


def test_replayed_nonce_is_rejected():
    verifier = HandshakeVerifier(local_agent_id="nova", shared_secret=SECRET)
    signed = sign_handshake(make_message(), SECRET)
    verifier.verify(signed, now=1_700_000_000)
    with pytest.raises(HandshakeError, match="replayed"):
        verifier.verify(signed, now=1_700_000_000)


def test_stale_message_is_rejected():
    verifier = HandshakeVerifier(local_agent_id="nova", shared_secret=SECRET)
    signed = sign_handshake(make_message(), SECRET)
    with pytest.raises(HandshakeError, match="timestamp"):
        verifier.verify(signed, now=1_700_001_000)
