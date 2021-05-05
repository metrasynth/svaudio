from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
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

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj:
            return obj
        if not queryset:
            raise Http404()
        username = self.kwargs["username"].lower()
        user = self.model.objects.filter(username__lower=username).first()
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
