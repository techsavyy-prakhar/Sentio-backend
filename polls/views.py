from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Poll, Vote
from .serializers import PollSerializer, VoteSerializer


class PollViewSet(ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        poll = self.get_object()

        device_id = request.data.get("device_id")
        vote_value = request.data.get("vote_value")

        if not device_id:
            return Response({"error": "device_id required"}, status=400)

        if Vote.objects.filter(poll=poll, device_id=device_id).exists():
            return Response({"error": "Already voted"}, status=400)

        Vote.objects.create(
            poll=poll,
            device_id=device_id,
            vote_value=vote_value,
        )

        return Response({
            "success": True,
            "yes_votes": poll.vote_set.filter(vote_value=True).count(),
            "no_votes": poll.vote_set.filter(vote_value=False).count(),
            "total_votes": poll.vote_set.count()
        })
    
    @action(detail=True, methods=["post"])
    def check_vote(self, request, pk=None):
        device_id = request.data.get("device_id")

        if not device_id:
            return Response({"error": "device_id required"}, status=400)

        has_voted = Vote.objects.filter(
            poll_id=pk,
            device_id=device_id
        ).exists()

        return Response({
            "has_voted": has_voted
        })
