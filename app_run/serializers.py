from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import Run


class UserContractedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name',)


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserContractedSerializer(source='athlete')

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type',)

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'