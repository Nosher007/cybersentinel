import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Tracks all active WebSocket connections."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        """Send a JSON message to all connected clients."""
        for ws in self.active:
            await ws.send_text(json.dumps(message))


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Echo back — basic plumbing test (TICKET-004)
            await ws.send_text(json.dumps({"echo": data}))
    except WebSocketDisconnect:
        manager.disconnect(ws)
