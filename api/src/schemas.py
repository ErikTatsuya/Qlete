from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
QuizTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class QuestionCreate(BaseModel):
    text: NonEmptyText
    alternatives: list[NonEmptyText] = Field(min_length=4, max_length=4)
    correct_alternative: int = Field(default=1, ge=1, le=4)


class QuizCreate(BaseModel):
    title: QuizTitle
    description: str | None = Field(default=None, max_length=2000)
    questions: list[QuestionCreate] = Field(min_length=1, max_length=10)


class QuestionRead(BaseModel):
    id: int
    position: int
    text: str
    alternatives: list[str]


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    created_at: str
    questions: list[QuestionRead]


class QuestionAdminRead(QuestionRead):
    correct_alternative: int


class QuizAdminRead(QuizRead):
    questions: list[QuestionAdminRead]


class AnswerSubmission(BaseModel):
    alternative: int = Field(ge=1, le=4)


class AnswerResult(BaseModel):
    selected_alternative: int
    correct_alternative: int
    is_correct: bool


class AdminLogin(BaseModel):
    username: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1, max_length=1024)


class AdminSession(BaseModel):
    username: str





