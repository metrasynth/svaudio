from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RepoConfig(AppConfig):
    name = "svaudio.repo"
    verbose_name = _("Repo")

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Module"))
        registry.register(self.get_model("Project"))
