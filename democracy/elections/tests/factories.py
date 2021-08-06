from factory import SubFactory
from factory.django import DjangoModelFactory

from democracy.elections.models import Candidate, Election, Position
from democracy.users.tests.factories import UserFactory


class ElectionFactory(DjangoModelFactory):
    class Meta:
        model = Election


class PositionFactory(DjangoModelFactory):
    election = SubFactory(ElectionFactory)

    class Meta:
        model = Position


class CandidateFactory(DjangoModelFactory):
    position = SubFactory(PositionFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = Candidate
