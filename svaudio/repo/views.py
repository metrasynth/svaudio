import json
from typing import Any, Dict

from actstream import action
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import DatabaseError
from django.db.models import Model
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from ..claims.models import Claim
from ..tags.models import Tag, TaggedItem
from ..verbs import Verb
from . import models as m


class LocationsSubmitView(LoginRequiredMixin, SuccessMessageMixin, CreateView):

    model = m.Location
    fields = ["url"]
    success_message = _("URL successfully submitted")
    template_name = "repo/location_submit.html"

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super(LocationsSubmitView, self).form_valid(form)

    def get_success_url(self) -> str:
        return reverse("repo:location-submit")


location_submit_view = LocationsSubmitView.as_view()


@csrf_exempt
def location_submit_api_view(request):
    if request.method != "POST":
        raise Http404()
    if request.content_type != "application/json":
        raise Http404()
    body = json.loads(request.body) or {}
    private_key = body.get("key")
    if private_key != settings.SVAUDIO_REPO_API_SECRET_KEY:
        raise Http404()
    url = body.get("url")
    metadata = body.get("metadata")
    if not url:
        raise Http404()
    try:
        m.Location.objects.create(url=url, metadata=metadata)
        response = {"submitted": True}
    except DatabaseError:
        response = {"submitted": False}
    return HttpResponse(content=json.dumps(response), content_type="application/json")


class ModulesListView(ListView):

    model = m.Module
    queryset = m.Module.objects.filter(listed=True).order_by("-file__cached_at")


module_list_view = ModulesListView.as_view()


class GetByHashMixin:
    model: Model
    kwargs: Dict[str, Any]

    def get_object(self, queryset=None):
        return self.model.objects.get(file__hash=self.kwargs.get("hash"))


class ModulesDetailView(GetByHashMixin, SuccessMessageMixin, DetailView):

    model = m.Module


module_detail_view = ModulesDetailView.as_view()


class ModuleUpdateView(GetByHashMixin, UpdateView):

    model = m.Module
    template_name = "repo/module_update.html"
    fields = [
        "alt_name",
        "description",
        "listed",
    ]

    def get_object(self, queryset=None):
        obj = super(ModuleUpdateView, self).get_object(queryset)
        if not obj:
            raise Http404()
        user_claim = (
            Claim.claims_for(obj)
            .filter(
                user=self.request.user,
                approved=True,
            )
            .first()
        )
        if not user_claim:
            raise Http404()
        return obj

    def get_success_url(self) -> str:
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Saved changes to {self.object}",
        )
        return self.object.get_absolute_url()


module_update_view = ModuleUpdateView.as_view()


class ProjectsListView(ListView):

    model = m.Project
    queryset = m.Project.objects.filter(listed=True).order_by("-file__cached_at")


project_list_view = ProjectsListView.as_view()


class ProjectsDetailView(GetByHashMixin, DetailView):

    model = m.Project


project_detail_view = ProjectsDetailView.as_view()


class ProjectUpdateView(GetByHashMixin, SuccessMessageMixin, UpdateView):

    model = m.Project
    template_name = "repo/project_update.html"
    fields = [
        "alt_name",
        "description",
        "listed",
    ]

    def get_object(self, queryset=None):
        obj = super(ProjectUpdateView, self).get_object(queryset)
        if not obj:
            raise Http404()
        user_claim = (
            Claim.claims_for(obj)
            .filter(
                user=self.request.user,
                approved=True,
            )
            .first()
        )
        if not user_claim:
            raise Http404()
        return obj

    def get_success_url(self) -> str:
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Saved changes to {self.object}",
        )
        return self.object.get_absolute_url()


project_update_view = ProjectUpdateView.as_view()


def module_add_tag_view(request, hash):
    return _add_tag_view("module", request, hash)


def module_remove_tagged_item_view(request, hash):
    return _remove_tagged_item_view("module", request, hash)


def project_add_tag_view(request, hash):
    return _add_tag_view("project", request, hash)


def project_remove_tagged_item_view(request, hash):
    return _remove_tagged_item_view("project", request, hash)


def _add_tag_view(modelname, request, hash):
    user = request.user
    if not user.is_authenticated:
        return redirect(f"repo:{modelname}-detail", hash=hash)
    model = {"module": m.Module, "project": m.Project}[modelname]
    obj = get_object_or_404(model, file__hash=hash)
    tags = request.POST["tags"]
    tags = tags.split(",")
    tags = [t.strip().lower() for t in tags]
    tags = [t[1:] if t[0:1] == "#" else t for t in tags]
    tags = {t for t in tags if t}
    existing_tags = {t.name for t in obj.tags.all()}
    new_tags = list(sorted(tags - existing_tags))
    obj.tags.add_by_user(user, *new_tags)
    for new_tag in new_tags:
        action.send(
            sender=user,
            verb=Verb.ADDED_TAG,
            action_object=Tag.objects.get(name=new_tag),
            target=obj,
        )
    count = len(new_tags)
    messages.add_message(
        request,
        messages.SUCCESS,
        f"You added {count} new tag{'s' if count != 1 else ''}. Thanks!",
    )
    obj.clear_caches()
    return redirect(f"repo:{modelname}-detail", hash=hash)


def _remove_tagged_item_view(modelname, request, hash):
    user = request.user
    if not user.is_authenticated:
        return redirect(f"repo:{modelname}-detail", hash=hash)
    model = {"module": m.Module, "project": m.Project}[modelname]
    obj = get_object_or_404(model, file__hash=hash)
    tagged_item_id = request.POST["tagged_item_id"]
    tagged_items = obj.tagged_items.filter(id=tagged_item_id)
    tagged_item: TaggedItem
    for tagged_item in tagged_items:
        if request.user.is_moderator or (
            tagged_item.recently_added() and tagged_item.added_by == user
        ):
            tagged_item.delete()
    return redirect(f"repo:{modelname}-detail", hash=hash)
