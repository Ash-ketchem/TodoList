from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Task, Tag
from .serializers import TagSerializer, TaskSerializer
from rest_framework import routers, serializers, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination


# Create your views here.


class TaskListPagination(PageNumberPagination):
    page_size = 10  # Tasks per page


class TaskViewSet(viewsets.ModelViewSet):
    """Handle all CRUD operations for tasks."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "tags__name"]
    pagination_class = TaskListPagination

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        tags = task.tags.all()
        for tag in tags:
            if tag.task_set.count() == 1:
                tag.delete()
        return super().destroy(request, *args, **kwargs)
