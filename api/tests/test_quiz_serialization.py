import unittest
from datetime import datetime, timezone

from src.models import Question, Quiz
from src.services.quizzes import serialize_admin_quiz, serialize_quiz


class SerializeQuizTest(unittest.TestCase):
    def test_serialize_uses_materialized_question_list(self):
        quiz = Quiz(
            id=1,
            title="Quiz de teste",
            description="Descrição",
            created_at=datetime.now(timezone.utc),
        )
        quiz.questions = [
            Question(
                id=10,
                quiz_id=1,
                position=1,
                text="Qual a resposta correta?",
                alternative_1="A",
                alternative_2="B",
                alternative_3="C",
                alternative_4="D",
                correct_alternative=3,
                quiz=quiz,
            )
        ]

        payload = serialize_quiz(quiz, list(quiz.questions))

        self.assertEqual(payload.title, "Quiz de teste")
        self.assertEqual(payload.questions[0].text, "Qual a resposta correta?")
        self.assertEqual(payload.questions[0].alternatives, ["A", "B", "C", "D"])
        self.assertFalse(hasattr(payload.questions[0], "correct_alternative"))

    def test_admin_serialization_includes_correct_alternative(self):
        quiz = Quiz(
            id=1,
            title="Quiz de teste",
            description=None,
            created_at=datetime.now(timezone.utc),
        )
        question = Question(
            id=10,
            quiz_id=1,
            position=1,
            text="Qual a resposta correta?",
            alternative_1="A",
            alternative_2="B",
            alternative_3="C",
            alternative_4="D",
            correct_alternative=3,
            quiz=quiz,
        )
        quiz.questions = [question]

        payload = serialize_admin_quiz(quiz, [question])

        self.assertEqual(payload.questions[0].correct_alternative, 3)


if __name__ == "__main__":
    unittest.main()
