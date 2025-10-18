from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


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
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = user.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', '')
        qs = qs.filter(is_superuser=False)
        if type == 'coach':
            return qs.filter(is_staff=True)
        elif type == 'athlete':
            return qs.filter(is_staff=False)
        return qs


class RunStartView(APIView):
    def get(self, request, run_id):
        if not run_id:
            raise Http404
        run = get_object_or_404(Run, id=run_id)
        run.status = 'in_progress'
        run.save()
        return Response(RunSerializer(run).data)
