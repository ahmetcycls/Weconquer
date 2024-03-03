from fastapi import APIRouter, HTTPException, Body
from app.domain.task_tree.repository_impl import create_task_under_node, update_task_by_node_id, create_task_under_node_manual

import logging


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskDetail(BaseModel):
    title: str
    assigned_to: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    skills: List[str] = None
    subtasks: Optional[List['TaskDetail']] = None

TaskDetail.update_forward_refs()

class TaskCreatePayload(BaseModel):
    user_id: str
    project_node_id: str
    task_details: List[TaskDetail]  # This correctly represents the incoming JSON structure
    parent_node_id: Optional[str] = None

@router.post("/create/")  # Adjusted as per your correction
def create_task_endpoint(payload: TaskCreatePayload):
    try:
        tasks_dicts = [task.dict(by_alias=True, exclude_none=True) for task in payload.task_details]
        results = create_task_under_node(payload.user_id, payload.project_node_id, tasks_dicts, payload.parent_node_id)
        return {"message": "Tasks created successfully", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def register_socketio_events(sio):
    @sio.event
    async def connect(sid, environ):
        logger.info(f"Connected: {sid}")

    @sio.event
    async def disconnect(sid):
        logger.info(f"Disconnected: {sid}")
    @sio.event
    async def create_task_socket(sid, data):
        try:
            print(data)
            payload = TaskCreatePayload(**data)
            tasks_dicts = [task.dict(by_alias=True, exclude_none=True) for task in payload.task_details]
            results = create_task_under_node_manual(payload.user_id, payload.project_node_id, tasks_dicts, payload.parent_node_id, sio, sid)
            await sio.emit('added_node', {'data': results}, room=sid)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await sio.emit('error', {'detail': str(e)}, room=sid)