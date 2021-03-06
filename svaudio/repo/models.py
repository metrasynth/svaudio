from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models as m
from django.db import transaction
from django.db.models.fields.json import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from taggit.managers import TaggableManager
from vote.models import VoteModel

from svaudio.claims.models import Claim
from svaudio.repo.tasks import globally_set_initial_ownership, start_fetch
from svaudio.tags.models import TaggedItem, _UserAddedTaggableManager
from svaudio.users.models import User
from svaudio.utils.timestamp import now_utc


class File(m.Model):
    """A file that has been retrieved and minimally processed."""

    class Meta:
        ordering = ["-cached_at"]

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
        blank=True,
        help_text="Type of file, if known.",
    )
    size = m.IntegerField(
        help_text="Size of file in bytes.",
    )
    cached_at = m.DateTimeField(
        help_text="When the file was cached.",
    )
    last_accessed_at = m.DateTimeField(
        null=True,
        blank=True,
        help_text="When the file was last accessed.",
    )
    metadata = JSONField(
        null=True,
        blank=True,
        help_text="Metadata provided by API client",
    )

    def file_ext(self) -> str:
        return {"M": "sunsynth", "P": "sunvox"}[self.file_type]

    def media_path(self) -> Path:
        dest_dir, dest_file = self.hash[:2], f"{self.hash[2:]}.{self.file_ext()}"
        return Path(settings.SVAUDIO_REPO_CACHE_PATH) / dest_dir / dest_file

    def alias_path_fragment(self) -> Optional[str]:
        if self.file_type == "M":
            name = self.module.name
        elif self.file_type == "P":
            name = self.project.name
        else:
            return
        hash = self.hash
        dest_dir_1, dest_dir_2 = hash[:2], hash[2:]
        basename = f"{slugify(name)}-{hash[:8]}" if name else hash
        filename = f"{basename}.{self.file_ext()}"
        return f"{dest_dir_1}/{dest_dir_2}/{filename}"

    def alias_path(self) -> Optional[Path]:
        fragment = self.alias_path_fragment()
        return (Path(settings.SVAUDIO_REPO_CACHE_PATH) / fragment) if fragment else None

    def media_url(self) -> Optional[str]:
        fragment = self.alias_path_fragment()
        return urljoin(settings.SVAUDIO_REPO_CACHE_URL, fragment) if fragment else None

    def ensure_alias_symlink_exists(self):
        alias_path = self.alias_path()
        if not alias_path:
            return
        media_path = self.media_path()
        if not alias_path.is_symlink():
            alias_path.parent.mkdir(parents=True, exist_ok=True)
            alias_path.symlink_to(media_path)


class Location(m.Model):
    """A location where a SunVox resource might be found"""

    def __str__(self):
        return self.url

    url = m.URLField(
        max_length=2048,
        help_text="URL where resource can be publicly accessed.",
        unique=True,
    )
    added_by = m.ForeignKey(
        User,
        on_delete=m.SET_NULL,
        related_name="locations_added",
        null=True,
        blank=True,
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
        blank=True,
        help_text="Most recent fetch that succeeded.",
    )
    most_recent_file = m.ForeignKey(
        "File",
        on_delete=m.SET_NULL,
        related_name="locations",
        null=True,
        blank=True,
        help_text="Most recent file downloaded.",
    )
    metadata = JSONField(
        null=True,
        blank=True,
        help_text="Metadata provided by API client",
    )

    def save(self, *args, **kw) -> None:
        is_new = not self.id
        super().save(*args, **kw)
        if is_new and not (self.url.startswith("test://") and "?noFetch=1" in self.url):
            self.fetches.create()


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
        blank=True,
        help_text="File that was fetched, when finished, if successful.",
    )
    queued_at = m.DateTimeField(
        auto_now_add=True,
        help_text="When the fetch was queued.",
    )
    started_at = m.DateTimeField(
        null=True,
        blank=True,
        help_text="When the fetch started.",
    )
    finished_at = m.DateTimeField(
        null=True,
        blank=True,
        help_text="When the fetch finished.",
    )
    success = m.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the fetch succeeded.",
    )

    def save(self, *args, **kw) -> None:
        should_fetch = not self.id and "?noFetch=1" not in self.location.url
        super().save(*args, **kw)
        if should_fetch:
            assert self.id
            transaction.on_commit(self.start_fetch)

    def start_fetch(self):
        self.refresh_from_db()
        start_fetch.delay(fetch_id=self.id)


class Resource(m.Model):
    name = m.CharField(
        max_length=500,
        blank=True,
        help_text="Name of this resource.",
    )
    alt_name = m.CharField(
        "Alternate name",
        max_length=500,
        blank=True,
        null=True,
        help_text="(Optional) Name to show instead of the one embedded in the file.",
    )
    description = m.TextField(
        blank=True,
        null=True,
        help_text="(Optional) Full description. Limited Markdown supported.",
    )
    listed = m.BooleanField(
        default=True,
        help_text="Uncheck this to remove from search results.",
    )
    file = NotImplemented  # Implemented in subclasses.

    tags = TaggableManager(through=TaggedItem, manager=_UserAddedTaggableManager)

    class Meta:
        abstract = True
        ordering = ["-file__cached_at"]

    @staticmethod
    def clear_all_caches():
        for item in Module.objects.all():
            item.clear_caches()
        for item in Project.objects.all():
            item.clear_caches()

    def __str__(self):
        return self.display_name()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clear_caches()

    def clear_caches(self):
        raise NotImplementedError()

    def display_name(self):
        alt_name = self.alt_name.strip() if self.alt_name else ""
        return alt_name or self.name.strip() or "(untitled)"

    def metadata(self):
        return self.file.metadata

    def set_initial_ownership(self):
        if Claim.claims_for(self).count() > 0:
            return
        metadata = self.metadata() or {}
        discord_uid = metadata.get("discord", {}).get("uid")
        if discord_uid:
            criteria = dict(provider="discord", uid=discord_uid)
            listed = False
            for social_account in SocialAccount.objects.filter(**criteria):
                user = social_account.user
                print(f"Setting initial ownership for {self} to {user}...")
                Claim.objects.create(
                    user=user,
                    content_object=self,
                    approved=True,
                    reviewed_at=now_utc(),
                )
                listed = listed or user.auto_publish_uploads
            if self.listed != listed:
                self.listed = listed
                self.save()


class Module(VoteModel, Resource):
    """A SunVox module found within a File."""

    file = m.OneToOneField(
        "File",
        on_delete=m.CASCADE,
        related_name="module",
        help_text="File containing the content of this module.",
    )

    def clear_caches(self):
        cache.delete(make_template_fragment_key("object-tag-list", ["module", self.pk]))
        cache.delete(make_template_fragment_key("module-table-row", [self.pk]))

    def get_absolute_url(self):
        return reverse("repo:module-detail", kwargs={"hash": self.file.hash})

    def get_update_url(self):
        return reverse("repo:module-update", kwargs={"hash": self.file.hash})


class Project(VoteModel, Resource):
    """A SunVox project found within a File."""

    file = m.OneToOneField(
        "File",
        on_delete=m.CASCADE,
        related_name="project",
        help_text="File containing the content of this project.",
    )

    def clear_caches(self):
        cache.delete(
            make_template_fragment_key("object-tag-list", ["project", self.pk])
        )
        cache.delete(make_template_fragment_key("project-table-row", [self.pk]))

    def get_absolute_url(self):
        return reverse("repo:project-detail", kwargs={"hash": self.file.hash})

    def get_update_url(self):
        return reverse("repo:project-update", kwargs={"hash": self.file.hash})


@receiver(post_save, sender=SocialAccount)
def globally_set_initial_ownership_on_social_account_creation(sender, **kwargs):
    if kwargs.get("created"):
        globally_set_initial_ownership.delay()
