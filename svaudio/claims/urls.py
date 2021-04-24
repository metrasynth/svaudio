from django.urls import path

from .views import (
    moderate_action_view,
    moderate_view,
    object_claim_create_view,
    object_claim_list_view,
)

app_name = "claims"
urlpatterns = [
    path(
        "moderate/",
        view=moderate_view,
        name="moderate",
    ),
    path(
        "moderate/~action/",
        view=moderate_action_view,
        name="moderate-action",
    ),
    path(
        "<int:content_type_id>/<int:object_id>/",
        view=object_claim_list_view,
        name="object-claim-list",
    ),
    path(
        "<int:content_type_id>/<int:object_id>/~create/",
        view=object_claim_create_view,
        name="object-claim-create",
    ),
]
