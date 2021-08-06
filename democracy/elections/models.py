import re
import uuid

from django.conf import settings
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    TextChoices,
    TextField,
    UUIDField,
)
from django.utils import timezone

from democracy.users.models import User

# Temporary uOttawa Regex
uOttawa_regx = re.compile(r"([a-zA-Z]+[0-9][0-9][0-9]@uottawa\.ca)", re.IGNORECASE)


class Election(Model):
    """Stores information about an election."""

    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True, editable=False)

    # Election Information
    title = CharField(max_length=200, blank=True, default="")
    subtitle = CharField(max_length=200, blank=True, default="")
    description = TextField(blank=True, default="", max_length=20000)

    # Election Management
    manager = ForeignKey(
        to="users.User", null=True, related_name="elections", on_delete=CASCADE
    )
    enable_multiple_submissions = BooleanField(default=False)
    election_email_domain = CharField(max_length=100, blank=True, default="")
    # If not blank, this can be scanned while submitting applications
    whitelist = TextField(blank=True, default="")
    public = BooleanField(default=False)

    # Voting Time Parameters
    # CANDIDATE PLATFORM SUBMISSIONS
    submission_start_time = DateTimeField(blank=True, null=True)
    submission_end_time = DateTimeField(blank=True, null=True)
    submission_release_time = DateTimeField(blank=True, null=True)
    # VOTING
    voting_start_time = DateTimeField(blank=True, null=True)
    voting_end_time = DateTimeField(blank=True, null=True)
    voting_release_time = DateTimeField(blank=True, null=True)

    # Can access positions via .positions

    @property
    def application_time(self) -> bool:
        """Returns true if NOW is within the application period."""
        if getattr(settings, "DEBUG", False):
            return True

        # If the times don't exist, return false
        if not self.submission_start_time or not self.submission_end_time:
            return False

        now = timezone.now()
        return self.submission_start_time < now < self.submission_end_time

    @property
    def voting_time(self) -> bool:
        """Returns true if NOW is within the voting period."""
        if getattr(settings, "DEBUG", False):
            return True

        # If the times don't exist, return false
        if not self.voting_start_time or not self.voting_end_time:
            return False

        now = timezone.now()
        return self.voting_start_time < now < self.voting_end_time

    def eligible_to_vote(self, user: User) -> bool:
        return str(user.email_domain).lower() == str(self.election_email_domain).lower()

    def apply_uottawa_regex(self, user: User) -> bool:
        return bool(uOttawa_regx.match(str(user.email).lower()))

    def __str__(self):
        return f"Election: '{self.title}' by {self.manager.name}"


class Position(Model):
    """Stores information about an open and electable position."""

    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True, editable=False)

    election = ForeignKey(
        to=Election, null=True, related_name="positions", on_delete=CASCADE
    )
    title = CharField(max_length=200, blank=True, default="")
    description = TextField(blank=True, default="", max_length=20000)

    # Can access candidates via .candidates

    def __str__(self):
        return f"Position: '{self.title}'"


class Candidate(Model):
    """Stores the platform of a candidate."""

    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True, editable=False)

    user = ForeignKey(
        to="users.User", null=True, related_name="candidacies", on_delete=CASCADE
    )
    position = ForeignKey(
        to=Position, null=True, related_name="candidates", on_delete=CASCADE
    )
    platform = TextField(blank=True, default="", max_length=10000)

    def __str__(self):
        return f"Candidate: '{self.user.name} for {self.position.title}'"


class Ballot(Model):
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True, editable=False)

    # The user submitting the ballot will be recorded as the 'user'
    user = ForeignKey(
        to="users.User", null=True, related_name="ballots", on_delete=CASCADE
    )

    # The election the ballot is tied to will be the 'election'
    election = ForeignKey(
        to=Election, null=True, related_name="ballots", on_delete=CASCADE
    )

    # Votes can be accessed via '.votes'
    def __str__(self):
        return f"Ballot for {self.user.name} in election {self.election.title}"


class Vote(Model):
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True, editable=False)

    class VoteTypes(TextChoices):
        NORMAL = "NORMAL"
        ABSTAIN = "ABSTAIN"
        NO_CONFIDENCE = "NO_CONFIDENCE"

    ballot = ForeignKey(to=Ballot, related_name="votes", on_delete=CASCADE)
    position = ForeignKey(to=Position, related_name="votes", on_delete=CASCADE)
    candidate = ForeignKey(
        to=Candidate, null=True, related_name="votes", on_delete=CASCADE
    )
    vote_type = CharField(
        max_length=20, choices=VoteTypes.choices, default=VoteTypes.NORMAL
    )

    def __str__(self):
        return f"Vote by {self.ballot.user.name} in election ({self.ballot.election.id}) of type {self.vote_type}"


# class SpecialVote(Model):
#     """Special vote for special people: no-confidence or other special status."""
#     id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
#     created = DateTimeField(auto_now_add=True, editable=False)
#
#     ballot = ForeignKey(to=Ballot, related_name="votes", on_delete=CASCADE)
#     position = ForeignKey(to=Position, related_name="votes", on_delete=CASCADE)
