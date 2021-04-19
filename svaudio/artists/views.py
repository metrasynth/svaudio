from django.views.generic import ListView

from svaudio.users.models import User


class ArtistListView(ListView):

    model = User
    template_name = "artists/artist_list.html"

    def get_queryset(self):
        return super(ArtistListView, self).get_queryset().filter(feature_as_artist=True)


artists_list_view = ArtistListView.as_view()
