from django.urls import path

from .views import object_claim_create_view, object_claim_list_view

app_name = "claims"
urlpatterns = [
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
