from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run.views import company_details_view, RunViewSet, RunStartView, RunStopView, UsersViewSet, AthleteInfoViewSet

router = DefaultRouter()
router.register('runs', RunViewSet, basename='runs')
router.register('users', UsersViewSet, basename='users')
router.register('athlete_info', AthleteInfoViewSet, basename='athletes')

urlpatterns = [
    path('company_details/', company_details_view),
    path('runs/<int:run_id>/start/', RunStartView.as_view()),
    path('runs/<int:run_id>/stop/', RunStopView.as_view()),
    path('', include(router.urls))
]