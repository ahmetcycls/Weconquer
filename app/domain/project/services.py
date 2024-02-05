# app/domain/project/services.py

from typing import Optional
from app.infrastructure.database.relational_db.db import db

async def check_project_exists_for_user(user_id: int) -> bool:
    # Assuming you have a function in `db` to query PostgreSQL
    # Adjust `path` and `method` according to your API design
    response = await db(path=f"projects?user_id=eq.{user_id}", method="get")
    return len(response) > 0
