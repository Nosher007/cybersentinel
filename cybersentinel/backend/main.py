import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CyberSentinel",
    description="AI-powered cybersecurity simulation and threat analysis engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from routers import websocket  # when run directly from backend/
except ModuleNotFoundError:
    from backend.routers import websocket  # when run from project root

app.include_router(websocket.router)

# Routers added as built:
# from routers import attack, threats
# app.include_router(attack.router)
# app.include_router(threats.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cybersentinel-backend"}
