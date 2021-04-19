from django.db import models as m
from taggit.models import GenericTaggedItemBase, TagBase

from svaudio.users.models import User


class Tag(TagBase):
    pass


class TaggedItem(GenericTaggedItemBase):
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
