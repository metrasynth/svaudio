from django.apps import AppConfig


class RepoConfig(AppConfig):
    name = "svaudio.repo"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Module"))
        registry.register(self.get_model("Project"))
