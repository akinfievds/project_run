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
    athlete = models.ForeignKey(user, on_delete=models.CASCADE, related_name='runs')
    comment = models.CharField(max_length=255)
    status = models.CharField(max_length=12, choices=STATUSES, default='init')
    distance = models.FloatField(blank=True, null=True)


class AthleteInfo(models.Model):
    goals = models.CharField(max_length=255, blank=True, null=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name='athlete')


class Challenge(models.Model):
    full_name = models.CharField(max_length=255)
    athlete = models.ForeignKey(user, on_delete=models.CASCADE, related_name='challenges')


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='positions')
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)


class CollectibleItem(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)
    picture = models.URLField()
    value = models.PositiveSmallIntegerField()