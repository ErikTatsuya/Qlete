from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Question, Quiz
from src.schemas import (
    AnswerResult,
    QuestionAdminRead,
    QuestionRead,
    QuizAdminRead,
    QuizCreate,
    QuizRead,
)


async def list_quizzes(db: AsyncSession) -> list[QuizRead]:
    quizzes = (await db.scalars(
        select(Quiz).options(selectinload(Quiz.questions)).order_by(Quiz.created_at.desc())
    )).all()
    return [serialize_quiz(quiz, list(quiz.questions)) for quiz in quizzes]


async def create_quiz(db: AsyncSession, payload: QuizCreate) -> QuizRead:
    quiz = Quiz(title=payload.title, description=payload.description)
    quiz.questions = [
        Question(
            position=position,
            text=question.text,
            alternative_1=question.alternatives[0],
            alternative_2=question.alternatives[1],
            alternative_3=question.alternatives[2],
            alternative_4=question.alternatives[3],
            correct_alternative=question.correct_alternative,
        )
        for position, question in enumerate(payload.questions, start=1)
    ]

    try:
        db.add(quiz)
        await db.commit()
        await db.refresh(quiz)

        hydrated_quiz = await db.scalar(
            select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz.id)
        )
        if hydrated_quiz is None:
            raise RuntimeError("Quiz criado não foi encontrado após persistência.")
    except Exception:
        await db.rollback()
        raise

    materialized_questions = list(hydrated_quiz.questions)
    return serialize_quiz(hydrated_quiz, materialized_questions)


async def get_admin_quiz(db: AsyncSession, quiz_id: int) -> QuizAdminRead | None:
    quiz = await db.scalar(
        select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
    )
    if quiz is None:
        return None

    return serialize_admin_quiz(quiz, list(quiz.questions))


async def update_quiz(db: AsyncSession, quiz_id: int, payload: QuizCreate) -> QuizRead | None:
    quiz = await db.scalar(
        select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
    )
    if quiz is None:
        return None

    quiz.title = payload.title
    quiz.description = payload.description
    existing_questions = list(quiz.questions)

    try:
        for position, question_data in enumerate(payload.questions, start=1):
            if position <= len(existing_questions):
                question = existing_questions[position - 1]
            else:
                question = Question(position=position)
                quiz.questions.append(question)

            question.position = position
            question.text = question_data.text
            question.alternative_1 = question_data.alternatives[0]
            question.alternative_2 = question_data.alternatives[1]
            question.alternative_3 = question_data.alternatives[2]
            question.alternative_4 = question_data.alternatives[3]
            question.correct_alternative = question_data.correct_alternative

        for question in existing_questions[len(payload.questions):]:
            quiz.questions.remove(question)

        await db.commit()
        updated_quiz = await db.scalar(
            select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz.id)
        )
        if updated_quiz is None:
            raise RuntimeError("Quiz atualizado não foi encontrado após persistência.")
    except Exception:
        await db.rollback()
        raise

    return serialize_quiz(updated_quiz, list(updated_quiz.questions))


async def delete_quiz(db: AsyncSession, quiz_id: int) -> bool:
    quiz = await db.scalar(
        select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
    )
    if quiz is None:
        return False

    await db.delete(quiz)
    await db.commit()
    return True


async def check_answer(
    db: AsyncSession, quiz_id: int, question_id: int, alternative: int
) -> AnswerResult | None:
    question = await db.scalar(
        select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
    )
    if question is None:
        return None

    return AnswerResult(
        selected_alternative=alternative,
        correct_alternative=question.correct_alternative,
        is_correct=alternative == question.correct_alternative,
    )


def serialize_quiz(quiz: Quiz, questions: list[Question] | None = None) -> QuizRead:
    materialized_questions = questions if questions is not None else list(quiz.questions)

    return QuizRead(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_at=(quiz.created_at or datetime.now(timezone.utc)).isoformat(),
        questions=[
            QuestionRead(
                id=question.id,
                position=question.position,
                text=question.text,
                alternatives=[
                    question.alternative_1,
                    question.alternative_2,
                    question.alternative_3,
                    question.alternative_4,
                ],
            )
            for question in materialized_questions
        ],
    )


def serialize_admin_quiz(quiz: Quiz, questions: list[Question]) -> QuizAdminRead:
    public_quiz = serialize_quiz(quiz, questions)
    return QuizAdminRead(
        **public_quiz.model_dump(exclude={"questions"}),
        questions=[
            QuestionAdminRead(
                id=question.id,
                position=question.position,
                text=question.text,
                alternatives=[
                    question.alternative_1,
                    question.alternative_2,
                    question.alternative_3,
                    question.alternative_4,
                ],
                correct_alternative=question.correct_alternative,
            )
            for question in questions
        ],
    )