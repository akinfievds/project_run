from django.urls import path, include
from app_run.views import company_details_view

urlpatterns = [
    path('company_details/', company_details_view)
]