from pydantic import BaseModel


class AI_copilot(BaseModel):
    history: list = []
    input: str
    metadata: dict
    user_id: str | None = None
    project_id: str | None = None



