from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

user = get_user_model()


class Run(models.Model):
    STATUSES = [
        ('init', 'INIT'),
        ('in_progress', 'IN_PROGRESS'),
        ('finished', 'FINISHED')
    ]

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время забега')
    athlete = models.ForeignKey(user, on_delete=models.CASCADE, related_name='runs', verbose_name='Атлет')
    comment = models.CharField(max_length=255, verbose_name='Комментарий')
    status = models.CharField(max_length=12, choices=STATUSES, default='init', verbose_name='Статус')
    distance = models.FloatField(blank=True, null=True, verbose_name='Расстояние')
    run_time_seconds = models.PositiveSmallIntegerField(default=0, verbose_name='Время забега')
    speed = models.FloatField(default=0, verbose_name='Средняя скорость забега')

    class Meta:
        verbose_name = 'Забег'
        verbose_name_plural = 'Забеги'


class AthleteInfo(models.Model):
    goals = models.CharField(max_length=255, blank=True, null=True, verbose_name='Цели')
    weight = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Вес')
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name='athlete', verbose_name='Атлет')

    class Meta:
        verbose_name = 'Атлет'
        verbose_name_plural = 'Атлеты'


class Challenge(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='Название')
    athlete = models.ForeignKey(user, on_delete=models.CASCADE, related_name='challenges', verbose_name='Атлет')

    class Meta:
        verbose_name = 'Челлендж'
        verbose_name_plural = 'Челленджи'


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='positions', verbose_name='Забег')
    latitude = models.DecimalField(max_digits=6, decimal_places=4, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=7, decimal_places=4, verbose_name='Долгота')
    date_time = models.DateTimeField(default='0000-01-01T00:00:00.000', verbose_name='Дата и время')
    speed = models.FloatField(default=0, verbose_name='Скорость')
    distance = models.FloatField(default=0, verbose_name='Расстояние')

    class Meta:
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'


class CollectibleItem(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    uid = models.CharField(max_length=10, verbose_name='Идентификатор')
    latitude = models.FloatField(verbose_name='Широта')
    longitude = models.FloatField(verbose_name='Долгота')
    picture = models.URLField(verbose_name='Изображение')
    value = models.PositiveSmallIntegerField(verbose_name='Значение/бонус')
    athletes = models.ManyToManyField(user, related_name='items', blank=True, verbose_name='Атлет')

    class Meta:
        verbose_name = 'Коллекционный предмет'
        verbose_name_plural = 'Коллекционные предметы'


class Subscribe(models.Model):
    athlete = models.ForeignKey(user, on_delete=models.CASCADE, related_name='subscribers', verbose_name='Атлет')
    coach = models.ForeignKey(user, on_delete=models.CASCADE, related_name='subscribes', verbose_name='Тренер')

    class Meta:
        unique_together = ['athlete', 'coach']
        verbose_name = 'Подписка на тренера'
        verbose_name_plural = 'Подписки на тренера'


class CoachRating(models.Model):
    athlete = models.ForeignKey(user, on_delete=models.CASCADE, related_name='ratings_by_athlete', verbose_name='Атлет')
    coach = models.ForeignKey(user, on_delete=models.CASCADE, related_name='ratings_to_coach', verbose_name='Тренер')
    rating = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)],
                                              verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Оценка тренера'
        verbose_name_plural = 'Оценки тренера'