from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReactAuthConfig(AppConfig):
    name = "democracy.reactauth"
    verbose_name = _("React App Authentication")
