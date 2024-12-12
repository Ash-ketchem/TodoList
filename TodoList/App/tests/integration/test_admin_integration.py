from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.test import Client
from App.models import Task, Tag
from App.serializers import TaskSerializer, TagSerializer
import base64
from django.utils.timezone import now, timedelta


class AdminIntegrationTest(APITestCase):
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

        # Create admin user
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="admin", email="admin@example.com"
        )

        # Create basic user
        self.user = get_user_model().objects.create_user(
            username="test", password="test"
        )
        self.user.save()

        # Basic Authentication for the API tests
        self.basic_auth = "Basic " + base64.b64encode(b"test:test").decode("utf-8")

        # Create a client for admin login
        self.admin_client = Client()
        self.admin_client.login(username="admin", password="admin")

    def test_admin_login(self):
        # Test if the admin user can access the Django admin site
        response = self.admin_client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_delete_task_via_admin(self):
        task_to_delete = Task.objects.create(
            title="Task 4",
            description="To be deleted",
        )

        response = self.admin_client.get(f"/admin/App/task/{task_to_delete.id}/change/")
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.post(
            f"/admin/App/task/{task_to_delete.id}/delete/", {"post": "yes"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task_to_delete.id).exists())

    def test_admin_permissions_for_non_admin_user(self):
        # A non-admin user should not be able to access the admin site
        non_admin_client = Client()
        non_admin_client.login(username="test", password="test")

        # Attempt to access the admin page
        response = non_admin_client.get("/admin/")
        self.assertNotEqual(response.status_code, 200)  # Should be forbidden

    def test_task_list_admin_access(self):
        response = self.admin_client.get("/admin/App/task/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")
