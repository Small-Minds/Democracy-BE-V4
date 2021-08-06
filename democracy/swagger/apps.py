from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SwaggerConfig(AppConfig):
    name = "democracy.swagger"
    verbose_name = _("Swagger Documentation")
