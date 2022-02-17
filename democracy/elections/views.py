from enum import Enum, auto
from typing import Any, Dict

from django.core.cache import cache
from rest_framework import mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from democracy import get_version
from democracy.elections.models import Ballot, Candidate, Election, Position
from democracy.elections.serializers import (
    BallotSerializer,
    CandidateParticipantSerializer,
    CandidateSerializer,
    ElectionResultsSerializer,
    ElectionSerializer,
    ElectionShortSerializer,
    EmptyBallotSerializer,
    PositionLongSerializer,
    PositionSerializer,
)


# Common errors returned by views:
# 417 == Not on whitelist.
# 406 == Already applied (position or election)
class Keys(Enum):
    PUBLIC_ELECTION_SHORT = auto()
    PUBLIC_ELECTION_LIST = auto()
    PUBLIC_ELECTION = auto()
    POSITION = auto()
    BALLOT = auto()
    RESULT = auto()


def cacheKey(key: Keys, id: str) -> str:
    """Derives a cache key from input enum and given id."""
    version: str = get_version()
    result: str = f"{version}-{key.name}-{id}"
    return result


def getCache(key: Keys, id: str) -> Dict:
    """Gets an item from the cache of the given type/id."""
    useKey = cacheKey(key, id)
    print(f"GET key from cache: {useKey}")
    result: Dict = cache.get(useKey)
    if not result:
        print(f"No key in cache: {useKey}")
    return result


def setCache(key: Keys, id: str, obj: Dict):
    """Stores an item in the django cache based on type and id."""
    useKey = cacheKey(key, id)
    print(f"PUT key into cache: {useKey}")
    return cache.set(useKey, obj)


def deleteCache(key: Keys, id: str):
    """Removes an item from the Django cache."""
    useKey = cacheKey(key, id)
    print(f"DELETE key from cache: {useKey}")
    return cache.delete(useKey)


class ElectionManagementViewSet(ModelViewSet):
    serializer_class = ElectionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Election.objects.none()
        return Election.objects.filter(manager=self.request.user)

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def create(self, request, *args, **kwargs):
        # Ensure user has a maximum of 5 elections:
        user_elections_count = Election.objects.filter(
            manager=self.request.user
        ).count()
        if user_elections_count > 2:
            return Response(
                {"reason": "Too many elections."},
                status=status.HTTP_424_FAILED_DEPENDENCY,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        deleteCache(Keys.PUBLIC_ELECTION_LIST, "1")
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        pk: str = kwargs.get("pk", "")
        if pk:
            deleteCache(Keys.PUBLIC_ELECTION, pk)
            deleteCache(Keys.PUBLIC_ELECTION_LIST, "1")
        return super(ElectionManagementViewSet, self).update(request, args, kwargs)


class PositionManagementViewSet(ModelViewSet):
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Position.objects.none()
        return Position.objects.filter(election__manager=self.request.user)


class CandidateManagementViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Candidate.objects.none()
        return Candidate.objects.filter(position__election__manager=self.request.user)


# Participation ViewSets


class PublicElectionParticipantViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, JSONParser)
    queryset = Election.objects.all()

    def retrieve(self, request: Any, pk=None):
        cacheData = getCache(Keys.PUBLIC_ELECTION_SHORT, pk)
        if cacheData:
            return Response(cacheData)

        election = get_object_or_404(self.get_queryset(), id=pk)
        data = {
            "title": election.title,
            "subtitle": election.subtitle,
        }
        setCache(Keys.PUBLIC_ELECTION_SHORT, election.id, data)
        return Response(data)


class ElectionParticipantViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = ElectionShortSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)
    queryset = Election.objects.all()

    def list(self, request: Any):
        # Uses shorter serializer for the list object.
        cacheData = getCache(Keys.PUBLIC_ELECTION_LIST, "1")
        if cacheData:
            return Response(cacheData)
        serializer = ElectionShortSerializer(
            self.get_queryset().order_by("created").reverse(), many=True
        )
        setCache(Keys.PUBLIC_ELECTION_LIST, "1", serializer.data)
        return Response(serializer.data)

    def retrieve(self, request: Any, pk=None):
        election = get_object_or_404(self.get_queryset(), id=pk)
        serializer = ElectionSerializer(election, context={"request": request})
        data = serializer.data
        data["voting_open"] = election.voting_time
        data["applications_open"] = election.application_time
        data["domain_match"] = election.eligible_to_vote(self.request.user)
        data["candidate_count"] = Candidate.objects.filter(
            position__election=election
        ).count()
        return Response(data)


class PositionParticipationViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
):
    serializer_class = PositionLongSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)
    queryset = Position.objects.all()

    def retrieve(self, request, pk=None):
        cachedData = getCache(Keys.POSITION, pk)
        if cachedData:
            return Response(cachedData)
        position = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(position, context={"request": request})
        setCache(Keys.POSITION, position.id, serializer.data)
        return Response(serializer.data)


class CandidateParticipationViewSet(ModelViewSet):
    serializer_class = CandidateParticipantSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Candidate.objects.none()
        return Candidate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Ensure all input is valid.
        serializer: CandidateParticipantSerializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # Gather some objects for determining if the user can proceed.
        position = serializer.validated_data["position"]
        election = position.election

        # Ensure the user is only making a single submission.
        if not election.enable_multiple_submissions:
            if Candidate.objects.filter(
                position__election=position.election, user=self.request.user
            ).exists():
                return Response(
                    {"reason": "Election only allows a single submission."},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

        # UOTTAWA REGEX STEP
        # if not election.apply_uottawa_regex(self.request.user):
        #     return Response(
        #         {"error": "You are not on the whitelist."},
        #         status=status.HTTP_417_EXPECTATION_FAILED,
        #     )

        user_email: str = self.request.user.email
        if election.whitelist:
            if user_email.lower() not in election.whitelist:
                print(
                    f"User {self.request.user.email} attempted to submit a platform but was not on the whitelist."
                )
                return Response(
                    {"error": "You are not on the whitelist."},
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        # Ensure the domain matches.
        if not election.eligible_to_vote(self.request.user):
            return Response(
                {"reason": "Domain mismatch."},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        deleteCache(Keys.POSITION, position.id)
        deleteCache(Keys.BALLOT, position.election.id)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


# Voting


class EmptyBallotViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = EmptyBallotSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)
    queryset = Election.objects.all()

    def retrieve(self, request: Any, pk=None):
        cachedData = getCache(Keys.BALLOT, pk)
        if cachedData:
            return Response(cachedData)
        election = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(election, context={"request": request})
        setCache(Keys.BALLOT, election.id, serializer.data)
        return Response(serializer.data)


class VotingViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = BallotSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Ballot.objects.none()
        return Ballot.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        print(f"User {self.request.user.email} attempted to submit a ballot.")
        election_id = str(request.data["election"])
        if not election_id:
            return Response(
                {"error": "Provide an election ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure the user is on the whitelist if it exists.
        election: Election = Election.objects.get(id=election_id)

        # UOTTAWA REGEX STEP
        # if not election.apply_uottawa_regex(self.request.user):
        #     return Response(
        #         {"error": "You are not on the whitelist."},
        #         status=status.HTTP_417_EXPECTATION_FAILED,
        #     )

        user_email: str = self.request.user.email
        if election.whitelist:
            if user_email.lower() not in election.whitelist:
                print(
                    f"User {self.request.user.email} attempted to submit a platform but was not on the whitelist."
                )
                return Response(
                    {"error": "You are not on the whitelist."},
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        if Ballot.objects.filter(user=request.user, election=election_id).exists():
            print("User has already voted..")
            return Response(
                {"error": "You cannot submit more than one ballot for an election."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer: BallotSerializer):
        ballot: Ballot = serializer.save()
        ballot.user = self.request.user
        ballot.save()


# Election Results


class ResultViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
):
    serializer_class = ElectionResultsSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, JSONParser)
    queryset = Election.objects.all()

    def retrieve(self, request: Any, pk=None):
        cachedData = getCache(Keys.RESULT, pk)
        if cachedData:
            return Response(cachedData)
        election = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(election, context={"request": request})
        setCache(Keys.RESULT, election.id, serializer.data)
        return Response(serializer.data)
