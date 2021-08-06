import pytest

from democracy.elections.models import Candidate, Election, Position
from democracy.elections.tests.factories import (
    CandidateFactory,
    ElectionFactory,
    PositionFactory,
)
from democracy.users.models import User
from democracy.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def election() -> Election:
    return ElectionFactory()


@pytest.fixture
def position() -> Position:
    return PositionFactory()


@pytest.fixture
def candidate() -> Candidate:
    return CandidateFactory()
