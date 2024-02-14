from fastapi import APIRouter, HTTPException
# from app.domain.AI_copilot.models import AI_copilot
from pydantic import BaseModel
from app.domain.AI_copilot.ai_logic import ai, prompt
from app.domain.AI_copilot.models import AI_copilot
router = APIRouter()
from app.v1.endpoints.project_router import get_project_graph_in_readable_format, ProjectReadRequest
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
@router.post("/")
async def AI_copilot_router(payload: AI_copilot):
    try:
        if not payload.history:
            projectReadRequest = ProjectReadRequest(project_node_id=payload.project_node_id, user_id=payload.user_id)
            response_graph_readable = await get_project_graph_in_readable_format(projectReadRequest)
            payload.history.append({"role": "system", "content": prompt.format(response_graph_readable)})
        payload.history.append({"role": "user", "content": payload.input})

        response_of_AI = await ai(payload)
        return {"response": response_of_AI}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
