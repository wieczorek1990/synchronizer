from django.core import exceptions
from django.db import models
from files import hashes

FILES_DIRECTORY = "files"


class File(models.Model):
    station = models.ForeignKey("stations.Station", on_delete=models.CASCADE)
    hidden = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.station}"


def file_path(file_version: models.Model, filename: str) -> str:
    return f"{FILES_DIRECTORY}/{file_version.file.station.name}/{filename}"


class FileVersion(models.Model):
    file = models.ForeignKey(
        "files.File", on_delete=models.CASCADE, related_name="files"
    )
    name = models.TextField()
    file_holder = models.FileField(upload_to=file_path)
    checksum = models.CharField(max_length=128)
    next_version = models.ForeignKey(
        "files.FileVersion",
        on_delete=models.CASCADE,
        related_name="file_versions",
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"

    def calculate_checksum(self) -> str:
        return hashes.calculate_sha512(self.file_holder)

    def clean(self) -> None:
        if self.next_version is None:
            return
        if self.pk == self.next_version.pk:
            raise exceptions.ValidationError("Invalid next version.")

    def save(self, **kwargs) -> None:
        self.checksum = self.calculate_checksum()
        super().save(**kwargs)
