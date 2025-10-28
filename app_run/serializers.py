from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import AthleteInfo, Challenge, Run, Position


class UserContractedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "last_name", "first_name", )


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserContractedSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "date_joined", "username", "last_name",
                  "first_name", "type", "runs_finished", )

    def get_type(self, obj):
        return "coach" if obj.is_staff else "athlete"

    def get_runs_finished(self, obj):
        return obj.runs.filter(status="finished").count()


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = AthleteInfo
        exclude = ("id", "user",)

    def get_user_id(self, obj):
        return obj.user.id

    def validate_weight(self, value):
        if value <= 0 or value >= 900:
            raise serializers.ValidationError("Weight has to be between 1 and 10.")
        return value


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

    def validate_run(self, run):
        if not run.status == 'in_progress':
            raise serializers.ValidationError("Run status has to be 'in_progress'.")
        return run

    def validate_latitude(self, latitude):
        if not -90.0 <= latitude <= 90.0:
            raise serializers.ValidationError("Latitude has to be between -90.0 and 90.0.")
        return latitude

    def validate_longitude(self, latitude):
        if not -180.0 <= latitude <= 180.0:
            raise serializers.ValidationError("Longitude has to be between -180.0 and 180.0.")
        return latitude