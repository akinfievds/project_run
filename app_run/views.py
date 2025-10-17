from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer
from django.conf import settings
from django.contrib.auth import get_user_model

user = get_user_model()


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


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = user.objects.select_related('athlete').all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', '')
        qs = qs.filter(is_superuser=False)
        if type == 'coach':
            return qs.filter(is_staff=True)
        elif type == 'athlete':
            return qs.filter(is_staff=False)
        return qs
