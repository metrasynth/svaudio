from typing import Iterable, Optional, Union

from django import template
from django.contrib.contenttypes.models import ContentType

from svaudio.claims.models import Claim
from svaudio.repo.models import Module, Project
from svaudio.users.models import User

register = template.Library()

Claimable = Union[Module, Project]


@register.simple_tag
def approved_claims_for_object(obj: Claimable) -> Iterable[Claim]:
    return Claim.claims_for(obj).filter(approved=True)


@register.simple_tag
def claim_for_object_by_user(obj: Claimable, user: User) -> Optional[Claim]:
    if not user.is_anonymous:
        return Claim.claims_for(obj).filter(user=user)


@register.filter
def content_type(obj):
    if obj:
        return ContentType.objects.get_for_model(obj)
