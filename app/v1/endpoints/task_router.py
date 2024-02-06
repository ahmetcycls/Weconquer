from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from app.domain.task_tree.repository_impl import create_task_under_node, update_task_by_short_id

router = APIRouter()

class TaskCreatePayload(Body):
    parent_short_id: str
    task_details: Dict
class TaskUpdatePayload(Body):
    short_id: str
    update_details: Dict
@router.post("/tasks/create/")
def create_task_endpoint(payload: TaskCreatePayload):
    try:
        task_short_id = create_task_under_node(payload.parent_short_id, payload.task_details)
        return {"message": "Task created successfully", "taskShortId": task_short_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")

@router.patch("/tasks/update/")
def update_task_endpoint(payload: TaskUpdatePayload):
    try:
        updated_task = update_task_by_short_id(payload.short_id, payload.update_details)
        return {"message": "Task updated successfully", "updatedTask": updated_task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")

