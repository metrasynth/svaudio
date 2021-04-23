from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtistsConfig(AppConfig):
    name = "svaudio.artists"
    verbose_name = _("Artists")
