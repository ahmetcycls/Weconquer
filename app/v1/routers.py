from .endpoints import user_router, project_router, task_router, dashboard_router, personality_test_router
from fastapi import APIRouter


api_router = APIRouter()

api_router.include_router(user_router.router, prefix="/users", tags=["Users"])
api_router.include_router(project_router.router, prefix="/projects", tags=["Projects"])
api_router.include_router(task_router.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(dashboard_router.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(personality_test_router.router, prefix="/personality-tests", tags=["Personality Tests"])