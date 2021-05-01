from contextlib import contextmanager

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.management import BaseCommand, CommandError, CommandParser

from svaudio.claims.models import Claim
from svaudio.repo.models import Fetch, File, Location, Module, Project
from svaudio.tags.models import Tag, TaggedItem
from svaudio.users.models import User


class Command(BaseCommand):
    help = "Destructively populate dev database with sample data and sample users"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-f",
            "--force",
            default=False,
            action="store_true",
            help="Required to perform the database population.",
        )

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError("Must be running in DEBUG mode.")
        if not options.get("force"):
            raise CommandError("Use --force to destructively populate dev database.")
        self.perform_sample_data_populate()

    def perform_sample_data_populate(self):
        self._delete_all()
        self._create_users()
        self._fetch_urls()
        self._create_flatpages()

    def _delete_all(self):
        for model in [
            FlatPage,
            Claim,
            Fetch,
            File,
            Location,
            Module,
            Project,
            Tag,
            TaggedItem,
            User,
        ]:
            model.objects.all().delete()
            print(f"Deleted {model.__name__}.")

    def _create_users(self):
        @contextmanager
        def create_user(name: str, validate_email=True):
            """Creates a user, lets it be configured, then saves."""
            user: User = User.objects.create_user(
                username=name,
                email=f"{name}@{name}.name",
                password=name,
            )
            yield user
            user.save()
            if validate_email:
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    verified=True,
                    primary=True,
                )
            print(f"Created {user}.")

        with create_user("su") as su:
            su.is_superuser = True
            self.su = su

        with create_user("mod") as mod:
            mod.is_moderator = True
            self.mod = mod

        with create_user("arTisT") as artist:
            artist.feature_as_artist = True
            artist.display_name = "The arTisT"
            artist.bio = "hi. i only capiTalize The leTTer T."
            self.artist = artist

        with create_user("visitor", validate_email=False) as visitor:
            visitor.bio = "Just a visitor."
            self.visitor = visitor

    def _fetch_urls(self):
        for url in [
            (
                "https://github.com/warmplace/sunvox/raw/master/"
                "examples/NightRadio%20-%20Tiny%20Tune.sunvox"
            ),
            (
                "https://github.com/warmplace/sunvox/raw/master/"
                "instruments/guitar/electric_guitar.sunsynth"
            ),
        ]:
            Location.objects.create(url=url, added_by=self.visitor)

    def _create_flatpages(self):
        site = Site.objects.get(pk=1)
        page = FlatPage.objects.create(
            url="/",
            title="Index",
            content="Welcome, **developer**.",
        )
        page.sites.add(site)
        page = FlatPage.objects.create(
            url="/about/",
            title="About",
            content="This is a development version of [sunvox.audio](https://sunvox.audio/).",
        )
        page.sites.add(site)
