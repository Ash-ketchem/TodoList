from django.test import TestCase
from App.serializers import TaskSerializer
from App.models import Task, Tag
from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as VE


class TaskModelTestCase(TestCase):

    def setUp(self):
        """Setup initial task for testing."""
        # Common setup for all test cases
        self.tag1 = Tag.objects.create(name="python")
        self.tag2 = Tag.objects.create(name="react")
        self.task = Task.objects.create(
            title="Sample Task",
            description="Sample Description",
            status=Task.StatusChoices.OPEN,
        )
        self.task.tags.add(self.tag1, self.tag2)

    def test_task_repr(self):
        self.assertEqual(str(self.task), f"{self.task.title} : {self.task.status}")

    def test_tag_repr(self):
        self.assertEqual(str(self.tag1), f"{self.tag1.name}")

    def test_task_create_due_date(self):
        with self.assertRaises(ValidationError):
            Task.objects.create(
                title="Sample Task",
                description="Sample Description",
                status=Task.StatusChoices.OPEN,
                due_date=now().date() - timedelta(days=2),
            )

    def test_task_update_to_overdue_status_raises_error(self):
        data = {"status": Task.StatusChoices.OVERDUE}
        serializer = TaskSerializer(instance=self.task, data=data, partial=True)

        with self.assertRaises(VE):
            serializer.is_valid(raise_exception=True)
            serializer.save()
