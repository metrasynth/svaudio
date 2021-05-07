import pytest
from allauth.socialaccount.models import SocialAccount

from svaudio.claims.models import Claim
from svaudio.repo.models import Fetch, File, Location, Project
from svaudio.users.models import User
from svaudio.utils.timestamp import now_utc

DISCORD_UID = "qrstuvwxyz"


@pytest.mark.django_db
def test_retroactively_assign_ownership_to_new_discord_users():
    # Create a resource that has discord metadata.
    metadata = {"discord": {"uid": DISCORD_UID}}
    file = File.objects.create(
        hash="abcdef",
        file_type="P",
        size=12345,
        cached_at=now_utc(),
        metadata=metadata,
    )
    location = Location.objects.create(
        url="test://file.sunvox?noFetch=1",
        metadata=metadata,
        most_recent_file=file,
    )
    fetch = Fetch.objects.create(
        location=location,
        file=file,
        queued_at=now_utc(),
        started_at=now_utc(),
        finished_at=now_utc(),
        success=True,
    )
    location.last_good_fetch = fetch
    location.save()
    project = Project.objects.create(name="a project", file=file)

    # Starts out with no claims.
    claims = Claim.claims_for(project)
    assert claims.count() == 0

    # Creating a social account should trigger setting initial ownership.
    user: User = User.objects.create_user(
        username="myusername",
        email="my@user.name",
        password="mypassword",
    )
    SocialAccount.objects.create(
        user=user,
        provider="discord",
        uid=DISCORD_UID,
    )
    (claim,) = Claim.claims_for(project)
    assert claim.user == user
    assert claim.content_object == project
    assert claim.approved
