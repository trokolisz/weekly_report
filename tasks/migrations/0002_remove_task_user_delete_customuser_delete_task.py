# Generated by Django 5.1.1 on 2024-09-21 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='user',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
