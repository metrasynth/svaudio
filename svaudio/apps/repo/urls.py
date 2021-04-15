from django.urls import path

from svaudio.apps.repo.views import (
    locations_submit_view,
    modules_detail_view,
    modules_list_view,
    projects_detail_view,
    projects_list_view,
)

app_name = "repo"
urlpatterns = [
    path("locations/submit/", view=locations_submit_view, name="location-submit"),
    path("modules/", view=modules_list_view, name="module-list"),
    path("modules/<str:hash>/", view=modules_detail_view, name="module-detail"),
    path("projects/", view=projects_list_view, name="project-list"),
    path("projects/<str:hash>/", view=projects_detail_view, name="project-detail"),
]
