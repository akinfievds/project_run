from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, viewsets

from django_filters.rest_framework import DjangoFilterBackend

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from geopy import distance

from app_run.models import AthleteInfo, Challenge, Run, Position
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, PositionSerializer


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
    queryset = User.objects.all()
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


class AthleteInfoViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = AthleteInfoSerializer

    def get_object(self):
        user = get_object_or_404(User, id=self.kwargs.get('pk'))
        athlete, created = AthleteInfo.objects.get_or_create(user=user)
        return athlete

    def perform_update(self, serializer):
        user = get_object_or_404(User, id=self.kwargs.get('pk'))
        goals = serializer.validated_data.get('goals')
        weight = serializer.validated_data.get('weight')
        athlete, created = AthleteInfo.objects.update_or_create(
            user=user,
            defaults={
            'goals': goals,
            'weight': weight
        })
        return athlete

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=201)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['athlete']


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['run']


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
        run.distance = round(distance.distance(*[(position.latitude, position.longitude)
                                                 for position in run.positions.all()])
                                                 .km, 3)
        run.save()
        athlete = run.athlete
        if (athlete.runs.filter(status='finished').count() >= 10
            and not Challenge.objects.filter(athlete=athlete, full_name='Сделай 10 Забегов!').exists()):
            Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=athlete)
        return Response(RunSerializer(run).data)