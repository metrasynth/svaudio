from django.urls import path

from svaudio.apps.artists.views import artists_list_view

app_name = "artists"
urlpatterns = [
    path("artists/", view=artists_list_view, name="artist-list"),
]
