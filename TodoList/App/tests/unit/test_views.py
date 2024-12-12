import base64
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from App.models import Task, Tag
from django.contrib.auth.models import User


class TaskViewSetTest(APITestCase):

    def setUp(self):
        # user
        self.user = User.objects.create_user(username="test", password="test")
        # Create tags
        self.tag1 = Tag.objects.create(name="python")
        self.tag2 = Tag.objects.create(name="Nodejs")

        # Create tasks
        self.task1 = Task.objects.create(title="Task 1", description="Description")

        # Add tags to tasks
        self.task1.tags.add(self.tag1)

        # URL to access TaskViewSet
        self.url = reverse("task-list")  # Adjust this based on your URLs

        # Basic Authentication
        self.basic_auth = "Basic " + base64.b64encode(b"test:test").decode("utf-8")

    def test_task_destroy_deletes_task_and_tags(self):
        """
        Test that deleting a task also deletes associated tags
        when they are no longer used
        """

        self.client.credentials(HTTP_AUTHORIZATION=self.basic_auth)

        # Check initial number of tasks and tags
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)

        # Delete task
        task_url = reverse("task-detail", kwargs={"pk": self.task1.pk})
        response = self.client.delete(task_url)

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure task is deleted
        self.assertEqual(Task.objects.count(), 0)

        # Ensure tags used by task1 are deleted
        self.assertEqual(Tag.objects.count(), 1)

        self.assertEqual(Tag.objects.first().name, self.tag2.name)
