from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Lower
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


@dataclass
class Redirection(Exception):
    url: str


class UserDetailView(DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Redirection as r:
            return redirect(r.url)

    def get_object(self, queryset=None):
        queryset = queryset or self.model
        username = self.kwargs["username"]
        obj = queryset.objects.filter(username=username).first()
        if obj:
            return obj
        user = (
            queryset.objects.annotate(username_lower=Lower("username"))
            .filter(username_lower=username.lower())
            .first()
        )
        if not user:
            raise Http404()
        url = reverse("users:detail", kwargs={"username": user.username})
        raise Redirection(url=url)


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["name", "feature_as_artist", "auto_publish_uploads", "bio"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return self.request.user.get_absolute_url()  # type: ignore [union-attr]

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
