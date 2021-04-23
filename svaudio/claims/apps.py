from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClaimsConfig(AppConfig):
    name = "svaudio.claims"
    verbose_name = _("Claims")
