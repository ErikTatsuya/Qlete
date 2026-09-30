from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.dependencies import require_admin
from src.models import Task
from src.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


async def _serialize_task(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.get("/tasks", response_model=list[TaskRead], dependencies=[Depends(require_admin)])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    tasks = (await db.scalars(select(Task).order_by(Task.created_at.desc()))).all()
    return [_serialize_task(task) for task in tasks]


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(
        title=payload.title,
        description=payload.description,
        completed=payload.completed,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return await _serialize_task(task)


@router.get("/tasks/{task_id}", response_model=TaskRead, dependencies=[Depends(require_admin)])
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")
    return await _serialize_task(task)


@router.patch("/tasks/{task_id}", response_model=TaskRead, dependencies=[Depends(require_admin)])
async def update_task(task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.completed is not None:
        task.completed = payload.completed

    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return await _serialize_task(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")

    await db.delete(task)
    await db.commit()
