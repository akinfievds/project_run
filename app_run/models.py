from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()


class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(user, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
