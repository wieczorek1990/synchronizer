from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=256)
    path = models.TextField()
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="stations"
    )

    def __str__(self) -> str:
        return f"{self.name}"


class StationConnection(models.Model):
    station_a = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="station_connections_a",
    )
    station_b = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="station_connections_b",
    )
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="station_connections",
    )

    def __str__(self) -> str:
        return f"{self.station_a} - {self.station_b}"
