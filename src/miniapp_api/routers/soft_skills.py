"""Soft skills routers module"""
from asyncio import Queue, Semaphore
from fastapi import BackgroundTasks, Depends, APIRouter
import analytics

from miniapp_api import helpers


router = APIRouter()

task_queue = Queue()
semaphore = Semaphore(1)

async def queue_task_wrapper():
    """Queue task wrapper"""
    user_id = await task_queue.get()
    await analytics.update_user_data(user_id)
    semaphore.release()

async def process_task(user_id: int):
    """Process task"""
    await semaphore.acquire()
    await task_queue.put(user_id)
    await queue_task_wrapper()
    

@router.get(
    "/soft-skills"
)
async def update_user_soft_skills(
    user_id: int,
    background_tasks: BackgroundTasks,
    _service_auth: None = Depends(helpers.service_auth_dependency)
):
    """Update user soft skills"""
    background_tasks.add_task(process_task, user_id)
    return {"ok": True}
