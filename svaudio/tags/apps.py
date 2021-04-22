from django.apps import AppConfig


class TagsConfig(AppConfig):
    name = "svaudio.tags"
    label = "Tags"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Tag"))
