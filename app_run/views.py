from django.http import JsonResponse
from rest_framework import viewsets

from app_run.models import Run
from app_run.serializers import RunSerializer


def company_details_view(request):
    return JsonResponse({
        'company_name': 'Runners for the values',
        'slogan':'Anywhere, anytime, anywhat...',
        'contacts':'city-district-country'
    })


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer