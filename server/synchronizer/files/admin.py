from django.contrib import admin
from files import models


class FileVersionModelAdmin(admin.ModelAdmin):
    readonly_fields = ("checksum",)


models_with_admin_models = [
    (models.File, admin.ModelAdmin),
    (models.FileVersion, FileVersionModelAdmin),
]
for model, admin_model in models_with_admin_models:
    admin.site.register(model, admin_model)
