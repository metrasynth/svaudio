from django.db import models as m
from taggit.models import GenericTaggedItemBase, TagBase


class Tag(TagBase):
    pass


class TaggedItem(GenericTaggedItemBase):
    tag = m.ForeignKey(
        Tag, on_delete=m.CASCADE, related_name="%(app_label)s_%(class)s_items"
    )
