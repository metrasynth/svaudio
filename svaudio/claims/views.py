from datetime import datetime, timezone
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

from ..mixins import ModeratorRequiredMixin
from ..repo.models import Module, Project
from .models import Claim

# [TODO] factor this out into settings
CLAIMS_ALLOWED_MODELS = [
    Module,
    Project,
]


def _get_target_object(content_type_id, object_id):
    content_type = ContentType.objects.get(id=content_type_id)
    cls = content_type.model_class()
    if cls not in CLAIMS_ALLOWED_MODELS:
        raise Http404()
    obj = cls.objects.get(id=object_id)
    if not obj:
        raise Http404()
    return obj


class ModerateView(ModeratorRequiredMixin, ListView):

    template_name = "claims/moderate.html"
    model = Claim

    def get_queryset(self):
        return Claim.objects.filter(reviewed_at=None)


moderate_view = ModerateView.as_view()


def moderate_action_view(request):
    u = request.user
    if not (u.is_authenticated and (u.is_superuser or u.is_moderator)):
        raise Http404()
    claim = get_object_or_404(Claim, pk=request.POST["claim_id"])
    if claim.reviewed_by:
        raise Http404()
    action_type = request.POST["action_type"]
    if action_type == "approve":
        claim.approved = True
    elif action_type == "reject":
        claim.approved = False
    else:
        raise Http404()
    claim.reviewed_by = u
    claim.reviewed_at = datetime.now(tz=timezone.utc)
    claim.save()
    messages.add_message(
        request,
        messages.SUCCESS,
        f'Thank you for moderating "{claim}"',
    )
    return redirect("claims:moderate")


class ObjectClaimListView(LoginRequiredMixin, ListView):

    template_name = "claims/object_claim_list.html"
    model = Claim

    def get_queryset(self):
        content_type_id = self.kwargs["content_type_id"]
        object_id = self.kwargs["object_id"]
        return Claim.objects.filter(
            content_type_id=content_type_id,
            object_id=object_id,
            approved=True,
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        # Find target object.
        data["content_type_id"] = self.kwargs["content_type_id"]
        data["object_id"] = self.kwargs["object_id"]
        target = _get_target_object(data["content_type_id"], data["object_id"])
        data["target"] = target
        # Find any user claim, even if pending.
        user_claim = Claim.claims_for(target).filter(user=self.request.user).first()
        data["user_claim"] = user_claim
        return data


object_claim_list_view = ObjectClaimListView.as_view()


def object_claim_create_view(request, content_type_id, object_id):
    if not request.user.is_authenticated:
        raise Http404()
    target = _get_target_object(content_type_id, object_id)
    redirect_to_claim_list = redirect(
        "claims:object-claim-list",
        content_type_id=content_type_id,
        object_id=object_id,
    )
    user_claim = Claim.claims_for(target).filter(user=request.user).first()
    if user_claim:  # already exists?
        return redirect_to_claim_list
    p = request.POST.get
    if ("yes", "yes", "yes") != (p("ownerAck"), p("reviewAck"), p("abuseAck")):
        messages.add_message(
            request,
            messages.WARNING,
            "Please acknowledge all three items to claim ownership.",
        )
        return redirect_to_claim_list
    Claim.objects.create(user=request.user, content_object=target)
    messages.add_message(
        request,
        messages.SUCCESS,
        "Thank you! Your ownership claim was submitted and will now be reviewed.",
    )
    return redirect_to_claim_list
