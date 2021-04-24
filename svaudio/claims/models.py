from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models as m
from django.utils.translation import gettext_lazy as _

from svaudio.users.models import User


class Claim(m.Model):
    user = m.ForeignKey(
        User,
        on_delete=m.CASCADE,
        related_name="claims_made",
    )
    content_type = m.ForeignKey(
        ContentType,
        on_delete=m.CASCADE,
        verbose_name=_("content type"),
        related_name="%(app_label)s_%(class)s_claims",
    )
    object_id = m.IntegerField(
        verbose_name=_("object ID"),
        db_index=True,
    )
    content_object = GenericForeignKey()
    approved = m.BooleanField(
        null=True,
        blank=True,
    )
    reviewed_at = m.DateTimeField(
        null=True,
        blank=True,
    )
    reviewed_by = m.ForeignKey(
        User,
        on_delete=m.SET_NULL,
        null=True,
        blank=True,
        related_name="claims_reviewed",
    )

    @classmethod
    def claims_for(cls, instance):
        model = type(instance)._meta.concrete_model
        return cls.objects.filter(
            content_type__app_label=model._meta.app_label,
            content_type__model=model._meta.model_name,
            object_id=instance.pk,
        )
