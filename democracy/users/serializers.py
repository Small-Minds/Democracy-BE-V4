from django.conf import settings
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer as RestAuthLoginSerializer
from rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    name = serializers.CharField(min_length=1, max_length=255, required=True)

    def validate_name(self, name):
        if not name:
            raise ValidationError("Please provide a name.")
        return name

    def custom_signup(self, request, user):
        user.name = self.cleaned_data.get("name", "")
        user.save()

    def get_cleaned_data(self):
        data = {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "name": self.validated_data.get("name", ""),
        }
        return data


class LoginSerializer(RestAuthLoginSerializer):
    username = None


class CustomPasswordResetSerializer(PasswordResetSerializer):
    """Serializer for requesting a password reset e-mail."""

    def get_email_options(self):
        """Override this method to change default e-mail options."""
        frontend_url = getattr(settings, "FRONTEND_URL", None)
        return {"domain_override": frontend_url}
