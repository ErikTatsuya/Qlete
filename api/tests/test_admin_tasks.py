import unittest
from datetime import datetime, timezone

from src.models import Task
from src.schemas import TaskCreate, TaskRead


class AdminTaskModelsTest(unittest.TestCase):
    def test_task_model_can_be_created(self):
        task = Task(
            id=1,
            title="Revisar relatório",
            description="Validar os dados antes do deploy.",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.assertEqual(task.title, "Revisar relatório")
        self.assertFalse(task.completed)

    def test_task_create_schema_requires_title(self):
        payload = TaskCreate(title="Concluir revisão", description="Teste", completed=False)
        self.assertEqual(payload.title, "Concluir revisão")
        self.assertEqual(payload.description, "Teste")

    def test_task_read_schema_transforms_fields(self):
        task = TaskRead(
            id=2,
            title="Deploy",
            description="Publicar API",
            completed=True,
            created_at="2026-09-27T12:00:00+00:00",
            updated_at="2026-09-27T12:15:00+00:00",
        )
        self.assertTrue(task.completed)
        self.assertEqual(task.title, "Deploy")


if __name__ == "__main__":
    unittest.main()
