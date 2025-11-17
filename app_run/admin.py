from django.contrib import admin

from app_run.models import (AthleteInfo, Challenge, CoachRating,
                            CollectibleItem, Position, Run, Subscribe)


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'athlete', 'comment', 'status',
                    'distance', 'run_time_seconds', 'speed', )


@admin.register(AthleteInfo)
class AthleteInfoAdmin(admin.ModelAdmin):
    list_display = ('goals', 'weight', 'user',)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'athlete', )


@admin.register(CoachRating)
class CoachRating(admin.ModelAdmin):
    list_display = ('athlete', 'coach', 'rating', )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('run', 'latitude', 'longitude', 'date_time',
                    'speed', 'distance',)


@admin.register(CollectibleItem)
class CollectableItem(admin.ModelAdmin):
    list_display = ('name', 'uid', 'latitude', 'longitude',
                    'picture', 'value', )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'coach',)
