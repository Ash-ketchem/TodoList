from typing import Any, Iterable
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = "OPEN", "Open"
        WORKING = "WORKING", "Working"
        PENDING_REVIEW = "PENDING_REVIEW", "Pending Review"
        COMPLETED = "COMPLETED", "Completed"
        OVERDUE = "OVERDUE", "Overdue"
        CANCELLED = "CANCELLED", "Cancelled"

    title = models.CharField(max_length=100, null=False, blank=False)  # required
    description = models.TextField(max_length=1000, null=False, blank=False)  # required
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN,
        null=False,
        blank=False,
    )
    tags = models.ManyToManyField("Tag", blank=True, default=[])

    class Meta:
        ordering = ["id"]  # Order by the ID field by default

    def clean(self):
        super().clean()

        # Ensure due_date is after the timestamp
        if (
            self.due_date
            and self.due_date < now().date()
            and self.status == Task.StatusChoices.OPEN
        ):
            raise ValidationError(
                "The due date must be greater than or equal to the current date."
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate the model instance
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} : {self.status}"


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
