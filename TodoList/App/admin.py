from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import Task, Tag

# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "timestamp", "status", "due_date")
    list_filter = ("status", "due_date")
    search_fields = ("title", "description")
    readonly_fields = ("timestamp",)
    fieldsets = (
        (
            "Task Details",
            {"fields": ("title", "description", "due_date", "status", "tags")},
        ),
        (
            "Metadata",
            {
                "fields": ("timestamp",),
            },
        ),
    )
    filter_horizontal = ("tags",)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]):
        for task in queryset.all():
            # Custom logic before deleting the Task
            tags = task.tags.all()
            for tag in tags:
                if (
                    tag.task_set.count() == 1
                ):  # If tag is only associated with this task
                    tag.delete()

        return super().delete_queryset(request, queryset)

    def delete_view(self, request: HttpRequest, object_id: str, *args, **kwargs):
        for tag in Task.objects.get(pk=object_id).tags.all():
            # Custom logic before deleting the Task
            if tag.task_set.count() == 1:
                tag.delete()
        return super().delete_view(request, object_id, *args, **kwargs)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    fieldsets = (
        (
            "Tag Details",
            {
                "fields": ("name",),
            },
        ),
    )
