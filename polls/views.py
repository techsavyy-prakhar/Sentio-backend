from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

from polls.utils.moderation import is_content_allowed

from .models import Poll, Vote, Report
from .serializers import ReportSerializer

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
        question = request.data.get("question", "").strip()
        description = request.data.get("description", "").strip()

        if not question:
            return Response(
                {"error": "Question is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ MODERATE ONCE (combine text)
        combined_text = f"{question}\n{description}"

        if not is_content_allowed(combined_text):
            return Response(
                {"error": "This content violates our community guidelines"},
                status=status.HTTP_400_BAD_REQUEST
            )

        poll = Poll.objects.create(
            question=question,
            description=description,
            is_active=True
        )

        return Response(
            {
                "id": poll.id,
                "question": poll.question,
                "description": poll.description,
            },
            status=status.HTTP_201_CREATED
        )


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

        # 🟡 Vote check only
        if vote_value is None:
            return Response({"has_voted": False}, status=status.HTTP_200_OK)

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


class ReportPollView(APIView):
    def post(self, request, poll_id):
        device_id = request.data.get("device_id")
        print("Reporting poll:", poll_id, "from device:", device_id)

        if not device_id:
            return Response(
                {"error": "device_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔍 Explicit check
        if Report.objects.filter(poll=poll, device_id=device_id).exists():
            return Response(
                {"error": "This device has already reported this poll"},
                status=status.HTTP_409_CONFLICT
            )

        try:
            report = Report.objects.create(
                poll=poll,
                device_id=device_id,
                reason=request.data.get("reason", "")
            )
        except IntegrityError:
            # safety net (race condition)
            return Response(
                {"error": "This device has already reported this poll"},
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )
