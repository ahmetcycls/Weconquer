from fastapi import APIRouter, HTTPException, Body
from app.domain.task_tree.repository_impl import create_task_under_node, update_task_by_node_id, create_task_under_node_manual, delete_node_and_subnodes, delete_subnodes_and_their_relationships

import logging


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import json
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

async def create_task_endpoint(payload: TaskCreatePayload, sio, sid):
    try:
        tasks_dicts = [task.dict(by_alias=True, exclude_none=True) for task in payload.task_details]
        results = await create_task_under_node_manual(payload.user_id, payload.project_node_id, tasks_dicts,
                                                payload.parent_node_id, sio, sid)
        return results
    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        await sio.emit('error', {'detail': str(e)}, room=sid)

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
            results = await create_task_under_node_manual(payload.user_id, payload.project_node_id, tasks_dicts, payload.parent_node_id, sio, sid)

            await sio.emit('added_node', {'data': results}, room=sid)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await sio.emit('error', {'detail': str(e)}, room=sid)

    @sio.event
    async def delete_node_and_subnodes_socket(sid, data):
        try:
            print(data)
            results = delete_node_and_subnodes(data["user_id"], data['node_id'], data['project_node_id'])
            await sio.emit('graph_update', {'data': results}, room=sid)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await sio.emit('error', {'detail': str(e)}, room=sid)

    @sio.event
    async def delete_subnodes_and_their_relationships_socket(sid, data):
        try:
            print("deleteeeee")
            print(data)
            results = delete_subnodes_and_their_relationships(data["user_id"], data['project_node_id'], data['node_id'] )
            # results = delete_direct_subnodes_only(data['node_id'])

            await sio.emit('graph_update', {'data': results}, room=sid)
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await sio.emit('error', {'detail': str(e)}, room=sid)

