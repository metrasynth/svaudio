from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TagsConfig(AppConfig):
    name = "svaudio.tags"
    verbose_name = _("Tags")
    label = "Tags"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Tag"))
