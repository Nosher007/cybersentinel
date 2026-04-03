"""
TICKET-013 — WebSocket router.
Streams simulation logs from the engine queue to all connected clients.
"""
import asyncio
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
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        """Send a JSON message to all connected clients."""
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


manager = ConnectionManager()


async def broadcast_from_engine():
    """
    Background task: reads logs from the engine queue and
    broadcasts them to all connected WebSocket clients.
    """
    from backend.routers.attack import engine
    while True:
        try:
            log = await asyncio.wait_for(engine.queue.get(), timeout=1.0)
            await manager.broadcast({"type": "log", "log": log})
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # Keep connection alive — client can send pings
            data = await ws.receive_text()
            await ws.send_text(json.dumps({"type": "ack", "message": data}))
    except WebSocketDisconnect:
        manager.disconnect(ws)
