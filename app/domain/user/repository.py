from app.domain.user.models import User
from app.infrastructure.database.relational_db import db

async def get_user_data(user_id: str):
    query = f"users?auth_provider_id=eq.{user_id}"

    db_response = await db(path = query, method = "get")
    print(db_response.json())
    return User(**db_response.json()[0])