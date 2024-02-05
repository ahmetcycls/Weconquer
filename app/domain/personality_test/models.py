from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class Question(BaseModel):
    question_id: int
    question_text: str
    trait_type: str | None
    sub_trait: str
    question_prompt: str
    cheated: bool | None

class Answer(BaseModel):
    user_id: str | None
    question_id: int
    answer_text: str
    answer_score: int | None
    cheated: bool | None
    answered_in_seconds: str | None
    question_prompt: str
    trait_type: str
    sub_trait: str
    justification: str | None

class StartTestRequest(BaseModel):
    user_id: str

class QuestionBatch(BaseModel):
    batch_id: int
    question_ids: List[int]
    tier: str | None
    questions: List[Question] | None = []   # Define the Question model based on your needs

class SubmitAnswers(BaseModel):
    user_id: str
    answers: List[Answer]
class UserSession(BaseModel):
    session_id: int
    user_id: str | None
    finished_batches: List[int]
    amount_of_batches_left: int
    remaining_batches: List[int]
    auth_provider_id: str | None

class BatchPackage(BaseModel):
    package_id: int
    batch_ids: List[int]
    tier_type: str # Define the Question model based on your needs