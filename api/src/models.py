from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    questions: Mapped[list["Question"]] = relationship(
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.position",
    )


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint("position BETWEEN 1 AND 10", name="ck_questions_position_range"),
        CheckConstraint("correct_alternative BETWEEN 1 AND 4", name="ck_questions_correct_alternative_range"),
        UniqueConstraint("quiz_id", "position", name="uq_questions_quiz_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    alternative_1: Mapped[str] = mapped_column(Text, nullable=False)
    alternative_2: Mapped[str] = mapped_column(Text, nullable=False)
    alternative_3: Mapped[str] = mapped_column(Text, nullable=False)
    alternative_4: Mapped[str] = mapped_column(Text, nullable=False)
    correct_alternative: Mapped[int] = mapped_column(nullable=False, default=1)
    quiz: Mapped[Quiz] = relationship(back_populates="questions")