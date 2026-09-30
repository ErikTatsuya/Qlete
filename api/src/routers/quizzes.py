from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.dependencies import require_admin
from src.schemas import AnswerResult, AnswerSubmission, QuizAdminRead, QuizCreate, QuizRead
from src.services.quizzes import (
    check_answer,
    create_quiz,
    delete_quiz,
    get_admin_quiz,
    list_quizzes,
    update_quiz,
)


router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


@router.get("", response_model=list[QuizRead])
async def get_quizzes(db: AsyncSession = Depends(get_db)):
    return await list_quizzes(db)


@router.post("", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
async def post_quiz(
    payload: QuizCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin),
):
    return await create_quiz(db, payload)


@router.get("/{quiz_id}/admin", response_model=QuizAdminRead)
async def get_quiz_admin_details(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin),
):
    quiz = await get_admin_quiz(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz não encontrado.")
    return quiz


@router.put("/{quiz_id}", response_model=QuizRead)
async def put_quiz(
    quiz_id: int,
    payload: QuizCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin),
):
    quiz = await update_quiz(db, quiz_id, payload)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz não encontrado.")
    return quiz


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin),
):
    if not await delete_quiz(db, quiz_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz não encontrado.")


@router.post("/{quiz_id}/questions/{question_id}/answer", response_model=AnswerResult)
async def post_answer(
    quiz_id: int,
    question_id: int,
    payload: AnswerSubmission,
    db: AsyncSession = Depends(get_db),
):
    result = await check_answer(db, quiz_id, question_id, payload.alternative)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pergunta não encontrada.")
    return result