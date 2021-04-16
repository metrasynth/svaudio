from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView

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


locations_submit_view = LocationsSubmitView.as_view()


class ModulesListView(ListView):

    model = m.Module


modules_list_view = ModulesListView.as_view()


class GetByHashMixin:
    model: Model
    kwargs: Dict[str, Any]

    def get_object(self, queryset=None):
        return self.model.objects.get(file__hash=self.kwargs.get("hash"))


class ModulesDetailView(GetByHashMixin, DetailView):

    model = m.Module


modules_detail_view = ModulesDetailView.as_view()


class ProjectsListView(ListView):

    model = m.Project


projects_list_view = ProjectsListView.as_view()


class ProjectsDetailView(GetByHashMixin, DetailView):

    model = m.Project


projects_detail_view = ProjectsDetailView.as_view()
