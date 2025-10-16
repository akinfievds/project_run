from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_run.views import company_details_view, RunViewSet, UsersViewSet

router = DefaultRouter()
router.register('runs', RunViewSet)
router.register('users', UsersViewSet)

urlpatterns = [
    path('company_details/', company_details_view),
    path('', include(router.urls))
]