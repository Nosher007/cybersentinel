"""
CyberSentinel — FastAPI application entry point.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "").lower()
limiter = Limiter(key_func=get_remote_address, enabled=(ENVIRONMENT != "test"))


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


_hide_docs = ENVIRONMENT == "production"
app = FastAPI(
    title="CyberSentinel",
    description="AI-powered cybersecurity simulation and threat analysis engine",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if _hide_docs else "/docs",
    openapi_url=None if _hide_docs else "/openapi.json",
)

app.state.limiter = limiter
if ENVIRONMENT != "test":
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from routers import websocket, attack, threats
except ModuleNotFoundError:
    from backend.routers import websocket, attack, threats

app.include_router(websocket.router)
app.include_router(attack.router)
app.include_router(threats.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cybersentinel-backend"}
