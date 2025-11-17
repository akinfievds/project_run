from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import (AthleteInfo, Challenge, CoachRating,
                            CollectibleItem, Position, Run)


class UserContractedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "last_name", "first_name", )


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserContractedSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = "__all__"


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
    date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")

    class Meta:
        model = Position
        fields = ("id", "run", "latitude", "longitude", "date_time", "distance", "speed")
        read_only_fields = ("id", "distance", "speed")

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


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = "__all__"

    def validate_latitude(self, latitude):
        if not -90.0 <= latitude <= 90.0:
            raise serializers.ValidationError("Latitude has to be between -90.0 and 90.0.")
        return latitude

    def validate_longitude(self, latitude):
        if not -180.0 <= latitude <= 180.0:
            raise serializers.ValidationError("Longitude has to be between -180.0 and 180.0.")
        return latitude


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "date_joined", "username", "last_name",
                  "first_name", "type", "runs_finished", "rating", )

    def get_type(self, obj):
        return "coach" if obj.is_staff else "athlete"

    def get_runs_finished(self, obj):
        return obj.runs_finished

    def get_rating(self, obj):
        return obj.rating


class AthleteDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(many=True)
    coach = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ("items", "coach", )

    def get_coach(self, obj):
        return obj.subscribers.values_list("coach", flat=True).first()


class CoachDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(many=True)
    athletes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ("items", "athletes", )

    def get_athletes(self, obj):
        return obj.subscribes.values_list("athlete", flat=True)


class CoachRatingSerilizer(serializers.ModelSerializer):
    class Meta:
        model = CoachRating
        fields = ("athlete", "coach", "rating", )