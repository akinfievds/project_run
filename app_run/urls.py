from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run import views

router = DefaultRouter()
router.register('runs', views.RunViewSet, basename='runs')
router.register('users', views.UsersViewSet, basename='users')
router.register('athlete_info', views.AthleteInfoViewSet, basename='athletes')
router.register('challenges', views.ChallengeViewSet, basename='challenges')
router.register('positions', views.PositionViewSet, basename='positions')
router.register('collectible_item', views.CollectibleItemViewSet, basename='collectible_item')

urlpatterns = [
    path('company_details/', views.company_details_view),
    path('upload_file/', views.upload_file),
    path('runs/<int:run_id>/start/', views.RunStartView.as_view()),
    path('runs/<int:run_id>/stop/', views.RunStopView.as_view()),
    path('', include(router.urls))
]