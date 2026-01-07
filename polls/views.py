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

        if not device_id:
            return Response(
                {"error": "device_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already voted
        existing_vote = Vote.objects.filter(
            poll=poll,
            device_id=device_id
        ).first()

        if existing_vote:
            return Response({
                "has_voted": True,
                "vote_value": existing_vote.vote_value,
                "yes_votes": poll.votes.filter(vote_value=True).count(),
                "no_votes": poll.votes.filter(vote_value=False).count(),
                "total_votes": poll.votes.count(),
            }, status=status.HTTP_200_OK)

        # 🔍 If vote_value NOT provided → just a CHECK call
        if vote_value is None:
            return Response({
                "has_voted": False
            }, status=status.HTTP_200_OK)

        # Convert string → boolean safely
        if isinstance(vote_value, str):
            vote_value = vote_value.lower()
            if vote_value == "true":
                vote_value = True
            elif vote_value == "false":
                vote_value = False
            else:
                return Response(
                    {"error": "vote_value must be true or false"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 🗳 Create vote
        Vote.objects.create(
            poll=poll,
            device_id=device_id,
            vote_value=vote_value
        )

        return Response({
            "has_voted": True,
            "message": "Vote recorded",
            "yes_votes": poll.votes.filter(vote_value=True).count(),
            "no_votes": poll.votes.filter(vote_value=False).count(),
            "total_votes": poll.votes.count(),
        }, status=status.HTTP_201_CREATED)

