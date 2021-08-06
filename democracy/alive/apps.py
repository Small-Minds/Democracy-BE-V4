from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AliveConfig(AppConfig):
    name = "democracy.alive"
    verbose_name = _("Alive")
