from django.urls import path, include

# from .views import TaskCreateAPIView, TaskDetailAPIView, TaskListAPIView
from .views import TaskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
urlpatterns = [path("", include(router.urls))]
