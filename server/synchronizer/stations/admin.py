from django.contrib import admin
from stations import models

models_with_admin_models = [
    (models.Station, admin.ModelAdmin),
    (models.StationConnection, admin.ModelAdmin),
]
for model, admin_model in models_with_admin_models:
    admin.site.register(model, admin_model)
