from fastapi import APIRouter, Request
from domain.personality_test.models import SubmitAnswers
from domain.personality_test.service import get_question_batch, judge
from db import db
personality_test_router = APIRouter()


@personality_test_router.post("/start-or-continue-test")
async def start_or_continue_test(request: Request):
    batch = await get_question_batch((await request.json())['user_id'])

    return batch[0]

@personality_test_router.post("/submit-answers/")
async def submit_answers(answers: SubmitAnswers):
    # Score each answer and update the database
    scores = await judge(answers)

    return scores

@personality_test_router.post("/user_test_status/")
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

    return None