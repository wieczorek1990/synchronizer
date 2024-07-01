from rest_framework import serializers
from stations import models


class WithUserModelSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())


class StationSerializer(WithUserModelSerializer):
    class Meta:
        model = models.Station
        fields = ("pk", "name", "path", "user")


class StationConnectionSerializer(WithUserModelSerializer):
    class Meta:
        model = models.StationConnection
        fields = ("pk", "station_a", "station_b", "user")
