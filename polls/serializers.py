from rest_framework import serializers
from .models import Poll, Vote, Report


class PollSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    question = serializers.CharField()
    description = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class VoteSerializer(serializers.Serializer):
    poll = serializers.CharField()
    device_id = serializers.CharField()
    vote_value = serializers.BooleanField()

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "poll", "reason", "reported_at", "device_id"]