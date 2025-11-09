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

from django.db.models import Sum, Min, Max, Count, Q, Avg

from geopy import distance
from openpyxl import load_workbook

from app_run.models import AthleteInfo, Challenge, Run, Position, CollectibleItem
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, PositionSerializer, CollectibleItemSerializer, UserDetailSerializer


class ProgressRunItemPagination(PageNumberPagination):
    page_size_query_param = 'size'


@api_view(['POST'])
def upload_file(request):
    uploaded_file = request.FILES.get('file')
    if uploaded_file:
        wb = load_workbook(uploaded_file)
        ws = wb.active
        errors = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            name, uid, value, latitude, longitude, url = row
            serializer = CollectibleItemSerializer(data={
                'name': name,
                'uid': uid,
                'value': value,
                'latitude': latitude,
                'longitude': longitude,
                'picture': url
            })
            if serializer.is_valid():
                CollectibleItem.objects.create(**serializer.validated_data)
            else:
                print(serializer.errors)
                errors.append(row)
        return Response(errors)
    return Response("File is not available!", status=400)


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
    queryset = User.objects.annotate(runs_finished=Count('runs', filter=Q(runs__status='finished')))
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = ProgressRunItemPagination

    def get_queryset(self):
        type = self.request.query_params.get('type', '')
        qs = self.queryset.filter(is_superuser=False)
        if type == 'coach':
            return qs.filter(is_staff=True)
        elif type == 'athlete':
            return qs.filter(is_staff=False)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return super().get_serializer_class()


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

    def perform_create(self, serializer):
        run = serializer.validated_data.get('run')
        athlete_latitude = serializer.validated_data.get('latitude')
        athlete_longitude = serializer.validated_data.get('longitude')
        items = CollectibleItem.objects.all()
        for item in items:
            distance_to_item = round(
                distance.distance((item.latitude, item.longitude), (athlete_latitude, athlete_longitude)).m,
                3
            )
            if distance_to_item <= 100 and not item in run.athlete.items.all():
                run.athlete.items.add(item)
        previous_positions = run.positions.all()
        if previous_positions.exists():
            serializer.validated_data['distance'] = round(
                distance.distance(
                    *[(position.latitude, position.longitude)
                    for position in previous_positions.order_by('date_time')]
                ).km, 2
            )
            last_position = previous_positions.order_by('-date_time').first()
            distance_to_previous_position = distance.distance((last_position.latitude, last_position.longitude),
                                                            (athlete_latitude, athlete_longitude)).m
            time_from_previous_position = (
                serializer.validated_data.get('date_time') - last_position.date_time
            ).total_seconds()
            serializer.validated_data['speed'] = round(
                distance_to_previous_position / time_from_previous_position,
                2
            )
        serializer.save()


class CollectibleItemViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


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
        positions = run.positions.all()
        run.distance = round(distance.distance(*[(position.latitude, position.longitude)
                                                 for position in positions])
                                                 .km, 3)
        timestampts = run.positions.aggregate(start=Min('date_time'), stop=Max('date_time'))
        start, stop = timestampts.get('start'), timestampts.get('stop')
        run.run_time_seconds = (stop - start).total_seconds() if start and stop else 0
        run.speed = run.positions.aggregate(Avg('speed')).get('speed__avg')
        run.status = 'finished'
        run.save()
        athlete = run.athlete
        finished_runs = athlete.runs.filter(status='finished')
        if (finished_runs.count() >= 10
            and not Challenge.objects.filter(athlete=athlete, full_name='Сделай 10 Забегов!').exists()):
            Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=athlete)
        total_distance = finished_runs.aggregate(Sum('distance'))
        if (total_distance.get('distance__sum') >= 50
            and not Challenge.objects.filter(athlete=athlete, full_name='Пробеги 50 километров!').exists()):
            Challenge.objects.create(full_name='Пробеги 50 километров!', athlete=athlete)
        return Response(RunSerializer(run).data)