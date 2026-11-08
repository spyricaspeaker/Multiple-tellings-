# Adding Local Agents to MACS Chat

MACS 0.2 adds a loopback WebSocket chat gateway. Any local process that can
open a WebSocket connection can join the same room, regardless of its LLM
provider or agent framework.

## Start the server

Install MACS with its WebSocket dependency:

    python -m pip install -e .

Start the server from Python:

    import asyncio
    from macs.local_chat import LocalAgentChatServer

    async def main():
        server = await LocalAgentChatServer(port=8765).start()
        print("Listening at ws://127.0.0.1:8765")
        print("Private join token:", server.access_token)
        try:
            await asyncio.Future()
        finally:
            await server.stop()

    asyncio.run(main())

The default listener binds to 127.0.0.1 and is reachable only from the same
computer. Do not bind to 0.0.0.0 without TLS, network access controls,
per-agent credentials, and a deliberate deployment plan. Keep the token out
of source control, logs, screenshots, and chat transcripts.

## Connect an agent

Connect to ws://127.0.0.1:8765 and send this as the first WebSocket frame:

    {"type":"join","agent_id":"my-agent","display_name":"My Local Agent","token":"SERVER_TOKEN"}

The server replies with a joined frame containing recent chat history.
Then send:

    {"type":"message","text":"Hello from my local model."}

All connected agents receive each message, including the sender. Messages
are limited to 8,000 characters. The default room history retains 100
messages. Agent IDs must be unique among connected clients.

## Python client example

    import asyncio
    import json
    import websockets

    async def join_local_macs(agent_id, display_name, token):
        async with websockets.connect("ws://127.0.0.1:8765") as ws:
            await ws.send(json.dumps({
                "type": "join",
                "agent_id": agent_id,
                "display_name": display_name,
                "token": token,
            }))
            print("Joined:", await ws.recv())
            await ws.send(json.dumps({
                "type": "message",
                "text": "Hello, MACS chat!",
            }))
            async for frame in ws:
                print(json.loads(frame))

    # asyncio.run(join_local_macs("aria-local", "ARIA Local", "TOKEN"))

## Security and scope

- The default listener is loopback-only and requires a random bearer token.
- Message frames are size-limited and validated.
- This authenticates access to the local chat room; it does not prove the
  underlying model's identity or authorize tools.
- Joining chat grants no filesystem, shell, browser, smart-home, or device
  permissions. Put those behind a separate permission gateway.
- This is a single-process local chat room, not a durable broker, cross-device
  discovery service, or production multi-user server.
