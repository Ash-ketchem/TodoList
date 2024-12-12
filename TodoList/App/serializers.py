from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Task, Tag
from django.utils.timezone import now


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=30), write_only=True, default=[]
    )

    class Meta:
        model = Task
        fields = "__all__"

    def validate(self, attrs):
        due_date = attrs.get("due_date", None)
        status = attrs.get("status", None)

        # If a due_date is present and has passed, mark the task as overdue
        if (
            due_date
            and due_date < now().date()
            and status != Task.StatusChoices.COMPLETED
        ):
            attrs["status"] = Task.StatusChoices.OVERDUE

        return super().validate(attrs)

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        validated_data["status"] = Task.StatusChoices.OPEN

        if (
            validated_data.get("due_date", None)
            and validated_data.get("due_date") < now().date()
        ):
            raise ValidationError({"status": "Cannot complete a task before creation"})
        task = Task.objects.create(**validated_data)

        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            task.tags.add(tag)

        return task

    def update(self, instance, validated_data):

        if validated_data.get("status", "") == Task.StatusChoices.OVERDUE:
            raise ValidationError({"status": "Cannot update task to OVERDUE status."})

        tags_data = validated_data.pop("tags", None)

        # Update the task fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags_data is not None:
            for tag in instance.tags.all():
                if tag.name not in tags_data and tag.task_set.count() == 1:
                    tag.delete()

            # Convert tags to Tag objects and set them
            tags = [
                Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tags_data
            ]
            instance.tags.set(tags)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Transform tags to only return their names (instead of full Tag objects)
        representation["tags"] = [tag.name for tag in instance.tags.all()]

        return representation
