from collections import OrderedDict
from typing import Dict, List

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from democracy.elections.models import Ballot, Candidate, Election, Position, Vote
from democracy.users.api.serializers import UserSerializer

# Participation Serializers


class CandidateParticipantSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        exclude: List[str] = ["user"]
        read_only_fields = ["id"]


class ElectionShortSerializer(ModelSerializer):
    class Meta:
        model = Election
        exclude: List[str] = ["created", "enable_multiple_submissions", "whitelist"]
        read_only_fields = ["id", "manager"]


# Management Serializers


class CandidateSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Candidate
        exclude: List[str] = ["created"]
        read_only_fields = ["id"]


class PositionSerializer(ModelSerializer):
    candidates = CandidateParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Position
        exclude: List[str] = ["created"]
        read_only_fields = ["id"]


class SimplePositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        exclude: List[str] = ["created", "election"]
        read_only_fields = ["id"]


class ElectionSerializer(ModelSerializer):
    positions = SimplePositionSerializer(many=True, read_only=True)
    manager = UserSerializer(read_only=True)

    class Meta:
        model = Election
        exclude: List[str] = ["created"]
        read_only_fields = ["id", "manager"]


# Participation Serializer
# For Positions Page


class PositionLongSerializer(ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)

    def validate_election(self, election: Election):
        if not election.application_time:
            raise serializers.ValidationError(
                {"time": "Application period not open yet."}
            )

        return election

    class Meta:
        model = Position
        exclude: List[str] = ["created"]
        read_only_fields = ["id"]


# Ballot Serializer


class EmptyBallotSerializer(ModelSerializer):
    positions = PositionLongSerializer(many=True, read_only=True)

    class Meta:
        model = Election
        exclude: List[str] = ["created", "whitelist"]
        read_only_fields = ["id", "manager"]


class VoteSerializer(ModelSerializer):
    """Not to be called directly; serializes the data within
    BallotSerializer."""

    def create(self, validated_data):
        raise Exception("Can't directly create votes.")

    def update(self, instance, validated_data):
        raise Exception("Updating votes is not allowed.")

    def validate(self, data: OrderedDict):
        """Ensure candidates are included with normal votes."""

        candidate = data.get("candidate")
        vote_type = data.get("vote_type")

        # If the vote type is normal, ensure that the candidate is present and return.
        if vote_type == Vote.VoteTypes.NORMAL:
            if not candidate:
                err: str = "Must include a candidate with a normal vote."
                print(err)
                raise serializers.ValidationError(err)
            return data

        # Otherwise, there should be no candidate.
        if candidate:
            err2: str = "You cannot reference a candidate with an ABSTAIN or NO_CONFIDENCE vote."
            print(err2)
            raise serializers.ValidationError(err2)

        return data

    class Meta:
        model = Vote
        exclude: List[str] = ["created", "ballot", "id"]


class BallotSerializer(ModelSerializer):
    votes = VoteSerializer(many=True)
    election = PrimaryKeyRelatedField(queryset=Election.objects.all())

    def validate_election(self, election: Election):
        if not election.voting_time:
            raise serializers.ValidationError({"time": "Voting period not open yet."})
        return election

    def update(self, instance, validated_data):
        raise Exception("Updating ballots is not allowed.")

    def create(self, validated_data):
        print(validated_data)

        # Ensure a set of votes are present.
        votes: List[Dict] = validated_data.pop("votes")
        if len(votes) == 0:
            raise serializers.ValidationError({"votes": "Include at least one vote."})

        ballot: Ballot = Ballot(**validated_data)
        if not ballot.election:
            raise serializers.ValidationError(
                {"election": "Ballot must have election."}
            )
        else:
            print(f"Ballot election is {ballot.election}")

        for vote_data in votes:
            Vote.objects.create(ballot=ballot, **vote_data)

        return ballot

    class Meta:
        model = Ballot
        exclude: List[str] = ["created", "user", "id"]


# Results


class CandidateResultsSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    votes = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Candidate
        exclude: List[str] = ["created", "platform"]
        read_only_fields = ["id"]


class PositionResultsSerializer(ModelSerializer):
    candidates = CandidateResultsSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        """Adds keys for no-confidence and abstain to the json response."""
        ret = super().to_representation(instance)
        ret["abstain"] = instance.votes.filter(vote_type=Vote.VoteTypes.ABSTAIN).count()
        ret["no_confidence"] = instance.votes.filter(
            vote_type=Vote.VoteTypes.NO_CONFIDENCE
        ).count()
        return ret

    class Meta:
        model = Position
        exclude: List[str] = ["created", "election", "description"]
        read_only_fields = ["id"]


class ElectionResultsSerializer(ModelSerializer):
    positions = PositionResultsSerializer(many=True, read_only=True)

    class Meta:
        model = Election
        exclude: List[str] = ["created", "whitelist"]
        read_only_fields = ["id", "manager"]
