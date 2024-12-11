from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import Task, Tag
from .serializers import TaskSerializer
from rest_framework.exceptions import ValidationError

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp', 'status', 'due_date')
    list_filter = ('status', 'due_date')
    search_fields = ('title', 'description')
    readonly_fields = ('timestamp', )
    fieldsets = (
        ("Task Details", {
            "fields": ('title', 'description', 'due_date', 'status', 'tags')
        }),
        ("Metadata", {
            "fields": ('timestamp',),
        }),
    )
    filter_horizontal = ('tags',) 

   
    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]):
        for task in queryset.all():
            # Custom logic before deleting the Task
            tags = task.tags.all()
            for tag in tags:
                if tag.task_set.count() == 1:  # If tag is only associated with this task
                    tag.delete()

        return super().delete_queryset(request, queryset)
    
    def delete_view(self, request: HttpRequest, object_id: str, *args, **kwargs):
        for tag in Task.objects.get(pk=object_id).tags.all():
            # Custom logic before deleting the Task
            if tag.task_set.count() == 1:
                tag.delete()
        return super().delete_view(request, object_id, *args, **kwargs)
    
    def save_model(self, request: Any, obj: Any, form: Any, change: Any):
        if change:
            validated_data =form.cleaned_data

            # Custom update logic: use your existing update method to handle the task update
            try:
                serializer = TaskSerializer()
                obj = serializer.update(obj, validated_data)
            except ValidationError as e:
                # If validation error occurs, show it in the admin panel
                self.message_user(request, (f'Error updating task: {e}'), level='error')
                return None
        
        return super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',) 
    # readonly_fields = ('taskCount',)
    fieldsets = (
        ("Tag Details", {
            "fields": ('name',),
        }),
        #  ("Metadata", {
        #     "fields": ('taskCount',),
        # }),
    )
