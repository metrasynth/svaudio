from django.db import models as m
from django.utils.translation import gettext_lazy as _

from svaudio.users.models import User


class File(m.Model):
    """A file that has been retrieved and minimally processed."""

    class FileType(m.TextChoices):
        MODULE = "M", _("Module")
        PROJECT = "P", _("Project")

    hash = m.CharField(
        max_length=64,
        unique=True,
        help_text="SHA-256 hash of file",
    )
    file_type = m.CharField(
        max_length=1,
        choices=FileType.choices,
        null=True,
        help_text="Type of file, if known.",
    )
    size = m.IntegerField(
        help_text="Size of file in bytes.",
    )
    cached_at = m.DateTimeField(
        help_text="When the file was cached.",
    )
    last_accessed_at = m.DateTimeField(
        help_text="When the file was last accessed.",
    )


class Location(m.Model):
    """A location where a SunVox resource might be found"""

    url = m.URLField(
        max_length=2048,
        help_text="URL where resource can be publicly accessed.",
    )
    added_by = m.ForeignKey(
        User,
        on_delete=m.SET_NULL,
        related_name="locations_added",
        null=True,
        help_text="User who added the resource.",
    )
    added_at = m.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of when the location was added.",
    )
    last_good_fetch = m.ForeignKey(
        "Fetch",
        on_delete=m.SET_NULL,
        related_name="locations",
        null=True,
        help_text="Most recent fetch that succeeded.",
    )
    most_recent_file = m.ForeignKey(
        "File",
        on_delete=m.SET_NULL,
        related_name="locations",
        null=True,
        help_text="File ",
    )


class Fetch(m.Model):
    """An attempt to fetch a location to get a file."""

    location = m.ForeignKey(
        "Location",
        on_delete=m.CASCADE,
        related_name="fetches",
        help_text="Location that we are fetching.",
    )
    file = m.ForeignKey(
        "File",
        on_delete=m.RESTRICT,
        related_name="fetches",
        null=True,
        help_text="File that was fetched, when finished, if successful.",
    )
    queued_at = m.DateTimeField(
        auto_now_add=True,
        help_text="When the fetch was queued.",
    )
    started_at = m.DateTimeField(
        null=True,
        help_text="When the fetch started.",
    )
    finished_at = m.DateTimeField(
        null=True,
        help_text="When the fetch finished.",
    )
    success = m.BooleanField(
        null=True,
        help_text="Whether the fetch succeeded.",
    )


class Module(m.Model):
    """A SunVox module found within a File."""

    file = m.OneToOneField(
        "File",
        on_delete=m.CASCADE,
        related_name="module",
        help_text="File containing the content of this module.",
    )
    name = m.CharField(
        max_length=500,
        blank=True,
        help_text="Name of this module.",
    )


class Project(m.Model):
    """A SunVox project found within a File."""

    file = m.OneToOneField(
        "File",
        on_delete=m.CASCADE,
        related_name="project",
        help_text="File containing the content of this project.",
    )
    name = m.CharField(
        max_length=500,
        blank=True,
        help_text="Name of this project.",
    )
