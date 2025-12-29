from rest_framework import serializers
from .models import Poll, Vote


class PollSerializer(serializers.ModelSerializer):
    yes_votes = serializers.SerializerMethodField()
    no_votes = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            "id",
            "question",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "yes_votes",
            "no_votes",
            "total_votes",
        ]

    def get_yes_votes(self, obj):
        return obj.vote_set.filter(vote_value=True).count()

    def get_no_votes(self, obj):
        return obj.vote_set.filter(vote_value=False).count()

    def get_total_votes(self, obj):
        return obj.vote_set.count()


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "poll", "device_id", "vote_value", "created_at"]
