from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Poll, Vote


class PollDetailView(APIView):
    def get(self, request, poll_id):
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            return Response({"error": "Poll not found"}, status=404)

        return Response({
            "id": poll.id,
            "question": poll.question,
            "description": poll.description,
            "is_active": poll.is_active,
            "created_at": poll.created_at.isoformat(),
            "yes_votes": poll.votes.filter(vote_value=True).count(),
            "no_votes": poll.votes.filter(vote_value=False).count(),
            "total_votes": poll.votes.count(),
        })


class PollListView(APIView):
    def get(self, request):
        polls = Poll.objects.all()

        data = [
            {
                "id": poll.id,
                "question": poll.question,
                "description": poll.description,
                "is_active": poll.is_active,
                "created_at": poll.created_at.isoformat(),
                "updated_at": poll.updated_at.isoformat(),
                "yes_votes": poll.votes.filter(vote_value=True).count(),
                "no_votes": poll.votes.filter(vote_value=False).count(),
                "total_votes": poll.votes.count(),
            }
            for poll in polls
        ]

        return Response(data)

    def post(self, request):
        question = request.data.get("question")
        description = request.data.get("description", "")

        if not question:
            return Response({"error": "question is required"}, status=400)

        poll = Poll.objects.create(
            question=question,
            description=description
        )

        return Response({
            "id": poll.id,
            "question": poll.question,
            "description": poll.description,
            "is_active": poll.is_active,
            "created_at": poll.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class VoteView(APIView):
    def post(self, request, poll_id):
        device_id = request.data.get("device_id")
        vote_value = request.data.get("vote_value")

        if device_id is None:
            return Response({"error": "device_id required"}, status=400)

        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            return Response({"error": "Poll not found"}, status=404)

        if Vote.objects.filter(poll=poll, device_id=device_id).exists():
            return Response(
                {"has_voted": True, "message": "You already voted"},
                status=409
            )

        Vote.objects.create(
            poll=poll,
            device_id=device_id,
            vote_value=vote_value
        )

        return Response({
            "success": True,
            "yes_votes": poll.votes.filter(vote_value=True).count(),
            "no_votes": poll.votes.filter(vote_value=False).count(),
            "total_votes": poll.votes.count(),
        }, status=status.HTTP_201_CREATED)
