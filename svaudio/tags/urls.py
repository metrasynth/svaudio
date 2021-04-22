from django.urls import path

from svaudio.tags.views import tag_detail_view, tag_list_view

app_name = "tags"
urlpatterns = [
    path(
        "tags/",
        view=tag_list_view,
        name="tag-list",
    ),
    path(
        "tags/<str:slug>/",
        view=tag_detail_view,
        name="tag-detail",
    ),
]
