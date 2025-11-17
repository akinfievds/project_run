from django.contrib import admin

from app_run.models import (AthleteInfo, Challenge, CoachRaiting, CollectibleItem, Position,
                            Run, Subscribe)

admin.site.register(Run)
admin.site.register(AthleteInfo)
admin.site.register(Challenge)
admin.site.register(CoachRaiting)
admin.site.register(Position)
admin.site.register(CollectibleItem)
admin.site.register(Subscribe)
