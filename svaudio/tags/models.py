from django.contrib.contenttypes.models import ContentType
from django.db import models as m
from django.db import router
from django.db.models import signals
from taggit.managers import _TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase
from taggit.utils import require_instance_manager
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

    @classmethod
    def items_for_object(cls, obj):
        content_type_id = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(content_type_id=content_type_id, object_id=obj.id)

    def __str__(self):
        return f"{self.content_object} tagged with {self.tag} by {self.added_by}"


class _UserAddedTaggableManager(_TaggableManager):
    @require_instance_manager
    def add_by_user(self, user: User, *tags, **kwargs):
        """Similar to .add(*tags, **kwargs), but records added_by attribution."""
        tag_kwargs = kwargs.pop("tag_kwargs", {})

        db = router.db_for_write(self.through, instance=self.instance)

        tag_objs = self._to_tag_model_instances(tags, tag_kwargs)
        new_ids = {t.pk for t in tag_objs}

        # NOTE: can we hardcode 'tag_id' here or should the column name be got
        # dynamically from somewhere?
        vals = (
            self.through._default_manager.using(db)
            .values_list("tag_id", flat=True)
            .filter(**self._lookup_kwargs())
        )

        new_ids = new_ids - set(vals)

        signals.m2m_changed.send(
            sender=self.through,
            action="pre_add",
            instance=self.instance,
            reverse=False,
            model=self.through.tag_model(),
            pk_set=new_ids,
            using=db,
        )

        for tag in tag_objs:
            self.through._default_manager.using(db).get_or_create(
                tag=tag,
                **self._lookup_kwargs(),
                defaults=dict(added_by=user),
            )

        signals.m2m_changed.send(
            sender=self.through,
            action="post_add",
            instance=self.instance,
            reverse=False,
            model=self.through.tag_model(),
            pk_set=new_ids,
            using=db,
        )
