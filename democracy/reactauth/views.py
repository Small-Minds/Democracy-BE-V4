from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from democracy.reactauth.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
)


class CustomTokenObtain(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefresh(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


swagger_view = get_schema_view(
    openapi.Info(
        title="Democracy System Swagger Autodocs",
        default_version="v1",
    ),
    public=True,
    authentication_classes=(
        TokenAuthentication,
        SessionAuthentication,
    ),
    permission_classes=(IsAuthenticatedOrReadOnly,),
)
