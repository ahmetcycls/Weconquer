from fastapi import APIRouter, Request
from app.domain.personality_test.models import SubmitAnswers
from app.domain.personality_test.service import get_question_batch, judge
from app.infrastructure.database.relational_db import db


router = APIRouter()
@router.post("/start-or-continue-test")
async def start_test(request: Request):
    first_batch = await get_question_batch((await request.json())['user_id'])

    return first_batch[0]

@router.post("/submit-answers/")
async def submit_answers(answers: SubmitAnswers):
    scores = await judge(answers)

    return scores

@router.post("/user_test_status/")
async def test_status(request: Request):
    request = await request.json()
    user_id = request.get("user_id")
    query_to_get_session = f"user_test_sessions?auth_provider_id=eq.{user_id}"
    session_response = await db(path=query_to_get_session, method="get")

    if session_response.status_code == 200:
        session_response = session_response.json()
        print(session_response)
        if session_response == []:
            return {"test_status": "not-started"}

        if session_response.get("amount_of_batches_left") == 0:
            return {"test_status": "completed"}
        else:
            return {"test_status": "in-progress"}

