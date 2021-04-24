from django.db import models as m
from taggit.models import GenericTaggedItemBase, TagBase
from vote.models import VoteModel

from svaudio.users.models import User


class Tag(TagBase):
    class Meta:
        ordering = ["name"]

    def module_items(self):
        return self.tags_taggeditem_items.filter(content_type__model="module")

    def project_items(self):
        return self.tags_taggeditem_items.filter(content_type__model="project")


class TaggedItem(VoteModel, GenericTaggedItemBase):
    tag = m.ForeignKey(
        Tag,
        on_delete=m.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )
    added_by = m.ForeignKey(
        User,
        on_delete=m.SET_NULL,
        blank=True,
        null=True,
        related_name="tags_added",
    )
