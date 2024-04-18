from fastapi import APIRouter, HTTPException, FastAPI
# from app.domain.main_AI.models import main_AI
from pydantic import BaseModel
from app.domain.main_AI.main_AI import ai, prompt
from app.v1.endpoints.project_router import get_project_graph_in_readable_format, ProjectReadRequest
from app.domain.project.services import fetch_project_hierarchy
import logging



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AI_copilot(BaseModel):
    history: list = []
    input: str
    metadata: dict | None = None
    user_id: str | None = None
    project_node_id: str | None = None
    selected_model: str
    creative_mode: bool


def register_socketio_events(sio):
    @sio.event
    async def connect(sid, environ):
        logger.info(f"Connected: {sid}")

    @sio.event
    async def disconnect(sid):
        logger.info(f"Disconnected: {sid}")
    @sio.event
    async def AI_copilot_message(sid, data):
        print(data)
        payload = AI_copilot(**data)
        try:
            if not payload.history:
                response_graph_readable = await fetch_project_hierarchy(payload.project_node_id, payload.user_id)
                payload.history.append({"role": "system", "content": prompt})
                payload.history.insert(1, {"role": "assistant", "content": response_graph_readable})
            payload.history.append({"role": "user", "content": payload.input})

            response_of_AI = await ai(payload, sio, sid)
            await sio.emit('ai_copilot_response', {'response': response_of_AI.history}, room=sid)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await sio.emit('error', {'detail': str(e)}, room=sid)
