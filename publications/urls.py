from django.urls import include, path

from rest_framework.routers import SimpleRouter

from publications.views import PublicationModelViewSet

router = SimpleRouter()
router.register(r"posts", PublicationModelViewSet, basename="publications")


urlpatterns = [
    path("", include(router.urls)),
]
