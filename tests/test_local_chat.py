import pytest
from macs.local_chat import LocalAgentChatServer


def test_server_defaults_to_loopback_and_generates_token():
    server = LocalAgentChatServer()
    assert server.host == "127.0.0.1"
    assert len(server.access_token) >= 32
    assert server.connected_agents == ()
    assert server.history == ()


def test_server_rejects_short_tokens_and_invalid_history_sizes():
    with pytest.raises(ValueError, match="32 characters"):
        LocalAgentChatServer(access_token="too-short")
    with pytest.raises(ValueError, match="history_size"):
        LocalAgentChatServer(history_size=0)


def test_decode_requires_json_object():
    assert LocalAgentChatServer._decode('{"type":"join"}') == {"type": "join"}
    with pytest.raises(ValueError):
        LocalAgentChatServer._decode('["not", "an", "object"]')


def test_bounded_string_rejects_missing_and_oversized_values():
    assert LocalAgentChatServer._bounded_string("  ARIA  ", 10) == "ARIA"
    assert LocalAgentChatServer._bounded_string("", 10) == ""
    assert LocalAgentChatServer._bounded_string("too long", 3) == ""
