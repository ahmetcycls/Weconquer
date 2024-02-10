from fastapi import APIRouter, HTTPException
from app.domain.AI_copilot.models import AI_copilot
from app.domain.AI_copilot.AI_logic import AI

router = APIRouter()
@router.post("/AI_copilot")
async def AI_copilot_router(payload: AI_copilot):
    try:
        user_input = payload.input
        payload.history.append({"role": "user", "content": user_input})
        response_of_AI = AI(payload)
        return {"response": response_of_AI}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
