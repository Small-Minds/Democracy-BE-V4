import pytest

from democracy.elections.models import Candidate, Election, Position

pytestmark = pytest.mark.django_db


class TestElection:
    def test_save(self, election: Election):
        election.save()

    def test_delete(self, election: Election):
        election.save()
        election.delete()


class TestPosition:
    def test_save(self, position: Position):
        position.save()

    def test_delete(self, position: Position):
        position.save()
        position.delete()


class TestCandidate:
    def test_save(self, candidate: Candidate):
        candidate.save()

    def test_delete(self, candidate: Candidate):
        candidate.save()
        candidate.delete()
