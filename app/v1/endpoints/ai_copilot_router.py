from fastapi import APIRouter, HTTPException, FastAPI
# from app.domain.AI_copilot.models import AI_copilot
from pydantic import BaseModel
from app.domain.AI_copilot.ai_logic import ai, prompt
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
                # projectReadRequest = ProjectReadRequest(project_node_id=payload.project_node_id, user_id=payload.user_id)
                response_graph_readable = await fetch_project_hierarchy(payload.project_node_id, payload.user_id)
                print("RESPONSE GRAPH READABLE", response_graph_readable)
                payload.history.append({"role": "system", "content": prompt})
                payload.history.insert(1, {"role": "assistant", "content": response_graph_readable})
                print(payload.history, "PAYLOAD HISTORY")
            payload.history.append({"role": "user", "content": payload.input})

            response_of_AI = await ai(payload, sio, sid)
            print("RESPONSE OF AI", response_of_AI.history)
            await sio.emit('ai_copilot_response', {'response': response_of_AI.history}, room=sid)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await sio.emit('error', {'detail': str(e)}, room=sid)
