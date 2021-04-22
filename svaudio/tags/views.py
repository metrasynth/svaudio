from django.views.generic import DetailView, ListView

from . import models as m


class TagListView(ListView):

    model = m.Tag
    template_name = "tags/tag_list.html"


tag_list_view = TagListView.as_view()


class TagDetailView(DetailView):

    model = m.Tag
    template_name = "tags/tag_detail.html"


tag_detail_view = TagDetailView.as_view()
