from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


user = get_user_model()


class ProgressRunItemPagination(PageNumberPagination):
    page_size_query_param = 'size'


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
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    pagination_class = ProgressRunItemPagination


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = user.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = ProgressRunItemPagination

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
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status != 'init':
            return Response({'message': 'Incorrect Status'}, status=400)
        run.status = 'in_progress'
        run.save()
        return Response(RunSerializer(run).data)


class RunStopView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status != 'in_progress':
            return Response({'message': 'Incorrect Status'}, status=400)
        run.status = 'finished'
        run.save()
        return Response(RunSerializer(run).data)