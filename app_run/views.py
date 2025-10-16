from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from app_run.models import Run
from app_run.serializers import RunSerializer
from django.conf import settings


@api_view(['GET'])
def company_details_view(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer