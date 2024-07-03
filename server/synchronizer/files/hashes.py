import hashlib

from django.db import models


def calculate_sha512(file_field: models.FileField) -> str:
    calculator = hashlib.new("sha512")
    file_pointer = file_field.open()
    for chunk in file_pointer.chunks():
        calculator.update(chunk)
    hex_digest = calculator.hexdigest()
    return hex_digest
