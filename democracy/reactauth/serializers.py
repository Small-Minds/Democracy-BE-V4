from django.contrib.auth.models import update_last_login
from rest_auth import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Fail if email has not been verified.
        email_address = self.user.emailaddress_set.get(email=self.user.email)
        if not email_address.verified:
            raise serializers.ValidationError("E-mail is not verified.")

        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        update_last_login(None, self.user)
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        data = {"access": str(refresh.access_token)}

        # Fail if email has not been verified.
        # email_address = self.user.emailaddress_set.get(email=self.user.email)
        # if not email_address.verified:
        #     raise serializers.ValidationError("E-mail is not verified.")

        # Rotate refresh tokens.
        refresh.set_jti()
        refresh.set_exp()
        data["refresh"] = str(refresh)

        return data
