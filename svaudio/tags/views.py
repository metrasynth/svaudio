from django.views.generic import DetailView, ListView

from . import models as m


class TagListView(ListView):

    model = m.Tag


tag_list_view = TagListView.as_view()


class TagDetailView(DetailView):

    model = m.Tag


tag_detail_view = TagDetailView.as_view()
