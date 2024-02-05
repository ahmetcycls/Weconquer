from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class Project(BaseModel):
    project_id: int
    description: str
    type: str | None
    tier: str
