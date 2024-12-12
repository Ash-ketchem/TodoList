# from django.forms import ValidationError
from unittest.mock import MagicMock
from django.test import TestCase
from django.contrib.admin.sites import site
from django.urls import reverse
from App.models import Tag, Task
from rest_framework.request import HttpRequest
from django.contrib.auth.models import User, Permission


class TaskAdminTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_superuser(username="admin", password="admin")
        self.user.user_permissions.add(Permission.objects.get(codename="delete_task"))
        self.user.save()

        # Create a task
        self.task = Task.objects.create(title="Task 1", description="Test task")
        self.tag1 = Tag.objects.create(name="Tag1")
        self.task.tags.add(self.tag1)

    def test_valid_task_data(self):
        # Attempt to update data
        change_data = {"title": "Task 2", "description": "Test changed"}

        # Use the admin interface to simulate the update
        admin_site = site
        model_admin = admin_site._registry[Task]
        request = HttpRequest()
        request.user = self.user

        form = model_admin.get_form(request, self.task)(data=change_data)
        form.is_valid()
        model_admin.save_model(request, self.task, form, change=True)

        # Check that the task is updated correctly
        self.assertEqual(Task.objects.get(id=self.task.id).title, "Task 2")
        self.assertEqual(Task.objects.get(id=self.task.id).description, "Test changed")

    def test_invalid_task_status_change(self):
        # Attempt to update task status to OVERDUE via admin interface
        change_data = {
            "status": Task.StatusChoices.OVERDUE,
        }

        # Use the admin interface to simulate the update
        admin_site = site
        model_admin = admin_site._registry[Task]
        request = HttpRequest()
        request.user = self.user

        form = model_admin.get_form(request, self.task)(data=change_data)
        form.is_valid()

        # Mock the message_user method to avoid the actual message handling
        model_admin.message_user = MagicMock()

        # Check if the form is valid
        model_admin.save_model(request, self.task, form, change=True)
        self.assertNotEqual(self.task.status, Task.StatusChoices.OVERDUE)

    def test_delete_queryset(self):
        admin_site = site
        model_admin = admin_site._registry[Task]
        request = HttpRequest()
        request.user = self.user

        # Delete the first task
        queryset = Task.objects.all()
        model_admin.delete_queryset(request, queryset)

        # Verify that task1 and tag1 are deleted
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
        self.assertFalse(Tag.objects.filter(id=self.tag1.id).exists())

    def test_delete_view(self):
        model_admin = site._registry[Task]
        request = HttpRequest()
        request.user = self.user

        # Get the delete view for the task
        url = reverse(
            "admin:%s_%s_delete" % (Task._meta.app_label, Task._meta.model_name),
            args=[self.task.id],
        )
        response = self.client.post(url, {"post": "yes"})

        model_admin.delete_view(request, self.task.pk)

        # Check if the task was deleted
        self.assertEqual(response.status_code, 302)
