from django.urls import path

from svaudio.repo.views import (
    location_submit_api_view,
    location_submit_view,
    module_add_tag_view,
    module_detail_view,
    module_list_view,
    module_update_view,
    project_add_tag_view,
    project_detail_view,
    project_list_view,
    project_update_view,
)

app_name = "repo"
urlpatterns = [
    path(
        "locations/submit/",
        view=location_submit_view,
        name="location-submit",
    ),
    path(
        "locations/submit/api/",
        view=location_submit_api_view,
        name="location-submit-api",
    ),
    path(
        "modules/",
        view=module_list_view,
        name="module-list",
    ),
    path(
        "modules/<str:hash>/",
        view=module_detail_view,
        name="module-detail",
    ),
    path(
        "modules/<str:hash>/~add-tag/",
        view=module_add_tag_view,
        name="module-add-tag",
    ),
    path(
        "modules/<str:hash>/~update/",
        view=module_update_view,
        name="module-update",
    ),
    path(
        "projects/",
        view=project_list_view,
        name="project-list",
    ),
    path(
        "projects/<str:hash>/",
        view=project_detail_view,
        name="project-detail",
    ),
    path(
        "projects/<str:hash>/~add-tag/",
        view=project_add_tag_view,
        name="project-add-tag",
    ),
    path(
        "projects/<str:hash>/~update/",
        view=project_update_view,
        name="project-update",
    ),
]
