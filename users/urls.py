from django.urls import include, path

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter

from users.views import UserCustomViewSet

router = SimpleRouter()
router.register(r"users", UserCustomViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
]
