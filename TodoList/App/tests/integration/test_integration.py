import base64
from django.core.exceptions import ValidationError
from django.urls import reverse
from App.models import Task, Tag
from App.serializers import TaskSerializer
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from rest_framework.test import APITestCase


class IntegrationTest(APITestCase):
    def setUp(self):
        # Create test data
        self.tag1 = Tag.objects.create(name="python")
        self.tag2 = Tag.objects.create(name="react")
        self.task1 = Task.objects.create(
            title="Task 1",
            description="Sample Description",
        )
        self.task2 = Task.objects.create(
            title="Task 2",
            description="Sample Description",
        )
        self.task1.tags.add(self.tag1, self.tag2)
        self.user = User.objects.create_user(username="test", password="test")
        self.user.save()

        # Basic Authentication
        self.basic_auth = "Basic " + base64.b64encode(b"test:test").decode("utf-8")

    def test_view_returns_correct_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, 200)
        # Validate the response data
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(response.json()["results"], serializer.data)

    def test_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Data for the new task
        new_task_data = {
            "title": "Task 3",
            "description": "New Task Description",
            "tags": [self.tag1.name, self.tag2.name],
        }

        # Send POST request to create a new task
        url = reverse("task-list")
        response = self.client.post(url, new_task_data, format="json")

        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 3)

        new_task = Task.objects.get(title="Task 3")
        self.assertEqual(new_task.description, "New Task Description")
        self.assertEqual(list(new_task.tags.all()), [self.tag1, self.tag2])

    def test_create_task_default_open_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Data for the new task
        new_task_data = {
            "title": "Task 3",
            "description": "New Task Description",
            "status": Task.StatusChoices.COMPLETED,
        }

        # Send POST request to create a new task
        url = reverse("task-list")
        response = self.client.post(url, new_task_data, format="json")
        self.assertEqual(response.status_code, 201)

        new_task = Task.objects.get(title="Task 3")
        self.assertEqual(new_task.status, Task.StatusChoices.OPEN)

    def test_create_task_fail_true(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Data for the new task
        new_task_data = {
            "title": "Task 3",
            "description": "New Task Description",
            "due_date": now().date() - timedelta(days=2),
        }

        # Send POST request to create a new task
        url = reverse("task-list")
        response = self.client.post(url, new_task_data, format="json")

        # Assertions
        self.assertEqual(response.status_code, 400)

        # Manual validation to confirm
        # the backend rejects saving a task with past due_date
        with self.assertRaises(ValidationError):
            self.task1.due_date = now().date() - timedelta(days=2)
            self.task1.save()

    def test_update_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Data to update
        update_data = {
            "title": "Updated Task 1",
            "description": "Updated Description",
            "tags": [],
        }

        # Send PUT request to update the task
        url = reverse("task-detail", kwargs={"pk": self.task1.id})
        response = self.client.put(url, update_data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task 1")
        self.assertEqual(self.task1.description, "Updated Description")
        self.assertTrue(self.task1.tags.count() == 0)

    def test_update_task_validations(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Data to update
        update_data = {"status": Task.StatusChoices.OVERDUE}

        with self.assertRaises(ValidationError):
            # Send PATCH request to update the task
            url = reverse("task-detail", kwargs={"pk": self.task1.id})
            self.client.patch(url, update_data)

    def test_delete_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Send DELETE request to delete the task
        url = reverse("task-detail", kwargs={"pk": self.task1.id})
        response = self.client.delete(url)

        # Assertions
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())
        self.assertFalse(Tag.objects.filter(id=self.tag1.id).exists())
