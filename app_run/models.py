from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()


class Run(models.Model):
    STATUSES = [
        ('init', 'INIT'),
        ('in_progress', 'IN_PROGRESS'),
        ('finished', 'FINISHED')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(user, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    status = models.CharField(max_length=12, choices=STATUSES)
