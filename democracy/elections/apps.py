from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ElectionsConfig(AppConfig):
    name = "democracy.elections"
    verbose_name = _("Elections")
