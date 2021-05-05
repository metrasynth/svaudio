from django.contrib.auth.models import AbstractUser
from django.db import models as m
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for sunvox.audio."""

    #: First and last name do not cover name patterns around the globe
    name = m.CharField(
        _("Display Name"),
        blank=True,
        max_length=255,
        help_text=_("Optional, to show a different name than your username."),
    )
    is_moderator = m.BooleanField(default=False)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    feature_as_artist = m.BooleanField(
        default=False,
        help_text=_("Select this to be included in list of artists."),
    )
    auto_publish_uploads = m.BooleanField(
        default=False,
        help_text=_("Select this to make new uploads publicly listed."),
    )
    bio = m.TextField(
        blank=True,
        help_text=_("Limited Markdown supported"),
    )

    def display_name(self):
        return self.name or self.username

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
