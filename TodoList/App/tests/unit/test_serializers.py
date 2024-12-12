from django.test import TestCase
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from App.models import Task, Tag
from App.serializers import TaskSerializer


class TaskSerializerTestCase(TestCase):
    def setUp(self):
        # Common setup for all test cases
        self.tag1 = Tag.objects.create(name="python")
        self.tag2 = Tag.objects.create(name="react")
        self.task = Task.objects.create(
            title="Sample Task",
            description="Sample Description",
            due_date=now().date() + timedelta(days=5),
            status=Task.StatusChoices.OPEN,
        )
        self.task.tags.add(self.tag1, self.tag2)

    def test_create_task_with_tags(self):
        """Test creating a task with new tags."""
        data = {
            "title": "New Task",
            "description": "Sample Description",
            "due_date": now().date() + timedelta(2000),
            "tags": ["python", "react"],
            "timestamp": now().date(),
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        task = serializer.save()
        self.assertEqual(task.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name="python").exists())
        self.assertTrue(Tag.objects.filter(name="react").exists())

    def test_update_status_after_due_date(self):
        """Test that a task is marked as overdue if the due_date is in the past."""

        data = {"due_date": now().date() - timedelta(days=2)}
        serializer = TaskSerializer(instance=self.task, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        # Validate() will change the status to OVERDUE due to the past due_date
        validated_data = serializer.validated_data

        self.assertEqual(validated_data["status"], Task.StatusChoices.OVERDUE)

    def test_update_task_tags(self):
        """Test updating a task's tags"""
        data = {"tags": ["django"], "title": "changed"}
        serializer = TaskSerializer(instance=self.task, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Ensure only the new tag exists
        self.assertEqual(self.task.tags.count(), 1)
        self.assertEqual(self.task.tags.first().name, "django")
        self.assertFalse(Tag.objects.filter(name="python").exists())

    def test_task_update_to_overdue_status_raises_error(self):
        with self.assertRaises(ValidationError):
            data = {
                "title": "New Task",
                "description": "Sample Description",
                "due_date": now().date() - timedelta(2000),
                "tags": ["python", "react"],
                "timestamp": now().date(),
            }
            serializer = TaskSerializer(data=data)
            serializer.create(validated_data=data)

    def test_representation(self):
        """Test serialized output tag representation"""
        serializer = TaskSerializer(instance=self.task)
        self.assertEqual(serializer.data["tags"], ["python", "react"])

    def test_default_status_is_open(self):
        """Test that the default status for a task is OPEN"""
        data = {
            "title": "Task Without Status",
            "description": "Testing Task Without Status",
            "tags": [],
            "timestamp": now().date(),
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.status, Task.StatusChoices.OPEN)
