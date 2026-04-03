"""
CyberSentinel — FastAPI application entry point.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background task that streams engine logs to WebSocket clients
    try:
        from backend.routers.websocket import broadcast_from_engine
    except ModuleNotFoundError:
        from routers.websocket import broadcast_from_engine

    task = asyncio.create_task(broadcast_from_engine())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="CyberSentinel",
    description="AI-powered cybersecurity simulation and threat analysis engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from routers import websocket, attack
except ModuleNotFoundError:
    from backend.routers import websocket, attack

app.include_router(websocket.router)
app.include_router(attack.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cybersentinel-backend"}
