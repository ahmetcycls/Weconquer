from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.v1.routers import api_router, ai_copilot_router, task_router
import socketio

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

app.include_router(api_router, prefix="/app/v1")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4200","http://localhost:4200/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_copilot_router.register_socketio_events(sio)
task_router.register_socketio_events(sio)