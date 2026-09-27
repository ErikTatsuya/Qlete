from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.dependencies import require_admin
from src.schemas import AnswerResult, AnswerSubmission, QuizCreate, QuizRead
from src.services.quizzes import check_answer, create_quiz, list_quizzes


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