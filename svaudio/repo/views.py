from typing import Any, Dict

from actstream import action
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models import Model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView

from ..tags.models import Tag
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


class ModulesListView(ListView):

    model = m.Module


module_list_view = ModulesListView.as_view()


class GetByHashMixin:
    model: Model
    kwargs: Dict[str, Any]

    def get_object(self, queryset=None):
        return self.model.objects.get(file__hash=self.kwargs.get("hash"))


class ModulesDetailView(GetByHashMixin, DetailView):

    model = m.Module


module_detail_view = ModulesDetailView.as_view()


class ProjectsListView(ListView):

    model = m.Project


project_list_view = ProjectsListView.as_view()


class ProjectsDetailView(GetByHashMixin, DetailView):

    model = m.Project


project_detail_view = ProjectsDetailView.as_view()


def module_add_tag_view(request, hash):
    return _add_tag_view("module", request, hash)


def project_add_tag_view(request, hash):
    return _add_tag_view("project", request, hash)


def _add_tag_view(modelname, request, hash):
    if not request.user.is_authenticated:
        return redirect(f"repo:{modelname}-detail", hash=hash)
    model = {"module": m.Module, "project": m.Project}[modelname]
    obj = get_object_or_404(model, file__hash=hash)
    tags = request.POST["tags"]
    tags = tags.split(",")
    tags = [t.strip().lower() for t in tags]
    tags = [t[1:] if t[0:1] == "#" else t for t in tags]
    tags = {t for t in tags if t}
    existing_tags = {t.name for t in obj.tags.all()}
    new_tags = tags - existing_tags
    for new_tag in new_tags:
        obj.tags.add(new_tag)
        action.send(
            request.user,
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
    cache.delete(make_template_fragment_key("object-tag-list", [modelname, obj.pk]))
    cache.delete(make_template_fragment_key(f"{modelname}-table-row", [obj.pk]))
    return redirect(f"repo:{modelname}-detail", hash=hash)
