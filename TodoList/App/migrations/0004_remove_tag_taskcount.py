# Generated by Django 5.1.4 on 2024-12-11 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("App", "0003_tag_taskcount_alter_task_tags"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tag",
            name="taskCount",
        ),
    ]