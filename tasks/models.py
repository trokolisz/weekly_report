from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subordinates'
    )

    def get_all_subordinates(self):
        subordinates = set()

        def _get_subordinates(user):
            for subordinate in user.subordinates.all():
                if subordinate not in subordinates:
                    subordinates.add(subordinate)
                    _get_subordinates(subordinate)

        _get_subordinates(self)
        return subordinates

    def __str__(self):
        return self.username
    

class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    description = models.TextField()
    time_spent = models.PositiveIntegerField(help_text='Time spent in minutes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.description[:50]}"

