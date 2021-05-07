from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models as m
from django.utils.translation import gettext_lazy as _

from svaudio.users.models import User


class Claim(m.Model):
    created_at = m.DateTimeField(auto_now_add=True)
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
    def claims_for(cls, obj):
        model = type(obj)._meta.concrete_model
        return cls.objects.filter(
            content_type__app_label=model._meta.app_label,
            content_type__model=model._meta.model_name,
            object_id=obj.pk,
        )

    def __str__(self):
        if not self.reviewed_at:
            status = "pending review"
        else:
            status = "approved" if self.approved else "rejected"
        return (
            f"Claim by {self.user.display_name()} for {self.content_object} ({status})"
        )
