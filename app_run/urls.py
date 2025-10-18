from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run.views import company_details_view, RunViewSet, RunStartView, UsersViewSet

router = DefaultRouter()
router.register('runs', RunViewSet)
router.register('users', UsersViewSet)

urlpatterns = [
    path('company_details/', company_details_view),
    path('runs/<int:run_id>/start/', RunStartView.as_view()),
    path('', include(router.urls))
]