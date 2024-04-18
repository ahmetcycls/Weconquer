from pydantic import BaseModel


class AI_copilot(BaseModel):
    history: list = []
    input: str
    metadata: dict | None = None
    user_id: str | None = None
    project_node_id: str | None = None
    selected_model: str
    creative_mode: bool
