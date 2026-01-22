from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings


from polls.utils.moderation import is_content_allowed

from .models import Poll, Vote, Report, BlockedDevice


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
            "creator_device_id": poll.device_id,
        })


class PollListView(APIView):

    def get(self, request):
        polls = Poll.objects.filter(is_active=True)

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
                "creator_device_id": poll.device_id,
                "total_votes": poll.votes.count(),
            }
            for poll in polls
        ]
        return Response(data)

    def post(self, request):
        question = request.data.get("question", "").strip()
        description = request.data.get("description", "").strip()
        device_id = request.data.get("device_id")

        if not question or not device_id:
            return Response(
                {"error": "question and device_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if BlockedDevice.objects.filter(device_id=device_id).exists():
            return Response(
                {"error": "This device is blocked"},
                status=status.HTTP_403_FORBIDDEN
            )
        combined_text = f"{question}\n{description}"
        if not is_content_allowed(combined_text):
            return Response(
                {"error": "This content violates community guidelines"},
                status=status.HTTP_400_BAD_REQUEST
            )
        poll = Poll.objects.create(
            question=question,
            description=description,
            device_id=device_id,
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
        reporter_device_id = request.data.get("device_id")
        reason = request.data.get("reason", "")

        if not reporter_device_id:
            return Response(
                {"error": "device_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if Report.objects.filter(
            poll=poll,
            reporter_device_id=reporter_device_id
        ).exists():
            return Response(
                {"error": "Already reported"},
                status=status.HTTP_409_CONFLICT
            )

        report = Report.objects.create(
            poll=poll,
            reporter_device_id=reporter_device_id,
            reason=reason
        )
        total_reports = poll.reports.count()

        if total_reports >= 3:
            poll.is_active = False
            poll.save()

        creator_reports = Report.objects.filter(
            poll__device_id=poll.device_id
        ).count()

        if creator_reports >= 5:
            BlockedDevice.objects.get_or_create(
                device_id=poll.device_id,
                defaults={"reason": "Repeated community violations"}
            )

        return Response(
            {"message": "Poll reported successfully"},
            status=status.HTTP_201_CREATED
        )

