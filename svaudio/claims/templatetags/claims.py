from typing import Iterable, Optional, Union

from django import template

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
    if user.is_anonymous:
        return
    return Claim.claims_for(obj).filter(user=user)
