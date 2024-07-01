from django.db.models import query
from rest_framework import views, viewsets
from stations import models, serializers


class OwnerMixin(views.APIView):
    def filter_queryset(self, queryset) -> query.QuerySet:
        return queryset.filter(user=self.request.user)


class StationViewSet(OwnerMixin, viewsets.ModelViewSet):
    queryset = models.Station.objects.all()  # noqa
    serializer_class = serializers.StationSerializer


class StationConnectionViewSet(OwnerMixin, viewsets.ModelViewSet):
    queryset = models.StationConnection.objects.all()  # noqa
    serializer_class = serializers.StationConnectionSerializer
