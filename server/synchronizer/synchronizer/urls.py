from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views
from stations import views

router = routers.DefaultRouter()
router.register(r"stations", views.StationViewSet, basename="station")
router.register(
    r"station-connections",
    views.StationConnectionViewSet,
    basename="station_connection",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", authtoken_views.obtain_auth_token),
    path("api/", include(router.urls)),
] + static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
