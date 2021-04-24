from django.contrib.auth.mixins import AccessMixin


class ModeratorRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        u = request.user
        if u.is_authenticated and (u.is_superuser or u.is_moderator):
            return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()
