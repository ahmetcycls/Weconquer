from fastapi import APIRouter, Request
from db import db

create_project_router = APIRouter()
@create_project_router.post("/create_project/")
async def post_login(request: Request):


    pass