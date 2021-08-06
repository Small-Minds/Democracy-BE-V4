from django.urls import include, path
from rest_framework.routers import DefaultRouter

from democracy.elections.views import (
    CandidateManagementViewSet,
    CandidateParticipationViewSet,
    ElectionManagementViewSet,
    ElectionParticipantViewSet,
    EmptyBallotViewSet,
    PositionManagementViewSet,
    PositionParticipationViewSet,
    PublicElectionParticipantViewSet,
    ResultViewSet,
    VotingViewSet,
)

app_name = "elections"

# Management Router
router = DefaultRouter()
router.register(r"election", ElectionManagementViewSet, basename="election")
router.register(r"position", PositionManagementViewSet, basename="position")
router.register(r"candidate", CandidateManagementViewSet, basename="candidate")

# Participation Router
participation_router = DefaultRouter()
participation_router.register(
    r"public-details", PublicElectionParticipantViewSet, basename="public-details"
)
participation_router.register(
    r"election", ElectionParticipantViewSet, basename="election"
)
participation_router.register(
    r"position", PositionParticipationViewSet, basename="position"
)
participation_router.register(
    r"candidate", CandidateParticipationViewSet, basename="candidate"
)

voting_router = DefaultRouter()
voting_router.register(r"vote", VotingViewSet, basename="vote")
voting_router.register(r"emptyballot", EmptyBallotViewSet, basename="emptyballot")
voting_router.register(r"results", ResultViewSet, basename="results")

urlpatterns = [
    path("manage/", include(router.urls)),
    path("participate/", include(participation_router.urls)),
    path("", include(voting_router.urls)),
]
