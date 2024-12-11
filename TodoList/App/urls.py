from django.urls import path, include
# from .views import TaskCreateAPIView, TaskDetailAPIView, TaskListAPIView
from .views import TaskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
urlpatterns = [

    path('', include(router.urls))
    # # REST API routes
    # path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    # path('tasks/create/', TaskCreateAPIView.as_view(), name='task-create'), 
    # path('tasks/<int:id>/', TaskDetailAPIView.as_view(), name='task-details'),
]