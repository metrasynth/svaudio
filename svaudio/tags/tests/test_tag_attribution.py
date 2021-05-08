import pytest

from svaudio.repo.models import File, Project
from svaudio.tags.models import Tag, TaggedItem
from svaudio.users.models import User
from svaudio.utils.timestamp import now_utc


@pytest.mark.django_db
def test_track_who_added_tag():
    file = File.objects.create(
        hash="abcdef",
        file_type="P",
        size=12345,
        cached_at=now_utc(),
    )
    project = Project.objects.create(name="a project", file=file)
    user1: User = User.objects.create_user(
        username="myusername1",
        email="my1@user.name",
        password="mypassword1",
    )
    user2: User = User.objects.create_user(
        username="myusername2",
        email="my2@user.name",
        password="mypassword2",
    )

    project.tags.add_by_user(user1, "foo")
    project.tags.add_by_user(user2, "foo", "bar")

    assert Tag.objects.count() == 2

    bar_item, foo_item = TaggedItem.items_for_object(project).order_by("tag__slug")

    assert bar_item.tag.name == "bar"
    assert bar_item.added_by == user2

    assert foo_item.tag.name == "foo"
    assert foo_item.added_by == user1
