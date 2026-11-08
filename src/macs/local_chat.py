"""Loopback WebSocket gateway that lets local agents join a shared MACS chat."""
from __future__ import annotations

import asyncio
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any

import websockets
from websockets.exceptions import ConnectionClosed

MAX_MESSAGE_CHARS = 8_000
DEFAULT_HISTORY_SIZE = 100


@dataclass(frozen=True)
class LocalChatMessage:
    sender_id: str
    sender_name: str
    text: str
    timestamp: float

    def as_dict(self) -> dict[str, Any]:
        return {"type": "message", "sender_id": self.sender_id,
                "sender_name": self.sender_name, "text": self.text,
                "timestamp": self.timestamp}


class LocalAgentChatServer:
    """Authenticated local chat room. Binds to loopback by default.

    First client frame:
      {"type":"join","agent_id":"...","display_name":"...","token":"..."}
    Later frames:
      {"type":"message","text":"..."}
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765, *,
                 access_token: str | None = None,
                 history_size: int = DEFAULT_HISTORY_SIZE) -> None:
        if history_size < 1:
            raise ValueError("history_size must be at least 1")
        self.host = host
        self.port = port
        self.access_token = access_token or secrets.token_urlsafe(32)
        if len(self.access_token) < 32:
            raise ValueError("access_token must contain at least 32 characters")
        self.history_size = history_size
        self._server = None
        self._peers: dict[Any, tuple[str, str]] = {}
        self._history: list[LocalChatMessage] = []
        self._lock = asyncio.Lock()

    @property
    def history(self) -> tuple[LocalChatMessage, ...]:
        return tuple(self._history)

    @property
    def connected_agents(self) -> tuple[dict[str, str], ...]:
        return tuple({"agent_id": agent_id, "display_name": name}
                     for agent_id, name in self._peers.values())

    async def start(self) -> "LocalAgentChatServer":
        if self._server is not None:
            raise RuntimeError("local chat server is already running")
        self._server = await websockets.serve(
            self._handle_peer, self.host, self.port, max_size=16_384,
            ping_interval=20, ping_timeout=20)
        return self

    async def stop(self) -> None:
        if self._server is None:
            return
        self._server.close()
        await self._server.wait_closed()
        self._server = None
        self._peers.clear()

    async def _handle_peer(self, websocket) -> None:
        peer_identity = None
        try:
            raw_join = await asyncio.wait_for(websocket.recv(), timeout=10)
            join = self._decode(raw_join)
            if join.get("type") != "join":
                await websocket.close(code=4401, reason="first frame must be join")
                return
            token = join.get("token")
            if not isinstance(token, str) or not hmac.compare_digest(token, self.access_token):
                await websocket.close(code=4403, reason="invalid local-agent token")
                return
            agent_id = self._bounded_string(join.get("agent_id"), 128)
            display_name = self._bounded_string(join.get("display_name"), 128)
            if not agent_id or not display_name:
                await websocket.close(code=4400, reason="agent_id and display_name required")
                return
            async with self._lock:
                if any(existing_id == agent_id for existing_id, _ in self._peers.values()):
                    await websocket.close(code=4409, reason="agent_id already connected")
                    return
                peer_identity = (agent_id, display_name)
                self._peers[websocket] = peer_identity
                history = [item.as_dict() for item in self._history]
            await websocket.send(json.dumps({"type": "joined", "agent_id": agent_id,
                                             "history": history}))
            async for raw in websocket:
                payload = self._decode(raw)
                if payload.get("type") != "message":
                    await websocket.send(json.dumps({"type": "error",
                        "error": "only message frames are accepted after joining"}))
                    continue
                body = payload.get("text")
                if not isinstance(body, str) or not body.strip() or len(body) > MAX_MESSAGE_CHARS:
                    await websocket.send(json.dumps({"type": "error",
                        "error": f"text must contain 1-{MAX_MESSAGE_CHARS} characters"}))
                    continue
                await self._broadcast(LocalChatMessage(agent_id, display_name,
                                                       body.strip(), time.time()))
        except (asyncio.TimeoutError, ValueError, TypeError, json.JSONDecodeError):
            await websocket.close(code=4400, reason="invalid or missing join frame")
        except ConnectionClosed:
            pass
        finally:
            if peer_identity is not None:
                async with self._lock:
                    self._peers.pop(websocket, None)

    @staticmethod
    def _decode(raw: str | bytes) -> dict[str, Any]:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if len(raw) > 16_384:
            raise ValueError("frame too large")
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("frame must be a JSON object")
        return value

    @staticmethod
    def _bounded_string(value: Any, limit: int) -> str:
        if not isinstance(value, str):
            return ""
        value = value.strip()
        return value if 0 < len(value) <= limit else ""

    async def _broadcast(self, message: LocalChatMessage) -> None:
        async with self._lock:
            self._history.append(message)
            self._history = self._history[-self.history_size:]
            peers = tuple(self._peers)
        frame = json.dumps(message.as_dict())
        if peers:
            await asyncio.gather(*(peer.send(frame) for peer in peers),
                                 return_exceptions=True)
