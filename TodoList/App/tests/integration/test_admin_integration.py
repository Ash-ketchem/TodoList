from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.test import Client
from App.models import Task, Tag
import base64


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

    def test_add_task_via_admin(self):
        data = {
            "title": "task 1",
            "description": "task",
            "due_date": "",
            "status": Task.StatusChoices.OPEN,
            "_save": "Save",
        }

        response = self.admin_client.get("/admin/App/task/add/")
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.post("/admin/App/task/add/", data=data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Task.objects.count(), 3)

    def test_add_invalid_task_via_admin(self):
        data = {
            "title": "task 1",
            "description": "task",
            "due_date": "",
            "status": Task.StatusChoices.OVERDUE,
            "_save": "Save",
        }

        response = self.admin_client.get("/admin/App/task/add/")
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.post("/admin/App/task/add/", data=data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Task.objects.count(), 2)

    def test_delete_task_via_admin(self):
        response = self.admin_client.get(f"/admin/App/task/{self.task1.id}/change/")
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.post(
            f"/admin/App/task/{self.task1.id}/delete/", {"post": "yes"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_delete_all_tasks_via_admin(self):
        # testing delete_queryset
        data = {
            "action": "delete_selected",
            "select_across": "0",
            "index": "0",
            "_selected_action": [task.id for task in Task.objects.all()],
        }

        response = self.admin_client.post("/admin/App/task/?o=2", data=data)
        self.assertEqual(response.status_code, 200)

        data.update({"action": "delete_selected", "post": "yes"})
        # deleting all tasks
        response = self.admin_client.post("/admin/App/task/?o=2", data=data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.count(), 0)

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
