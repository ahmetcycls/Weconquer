from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    user_id: str
    email: EmailStr
    tier_type: str | None
    user_status: str | None
    swipe_count: int | None
    swipe_limit: int | None
    sex: str | None
    country: str | None
    auth_provider_id: str
    family_name: str | None
    given_name: str | None
    locale: str | None