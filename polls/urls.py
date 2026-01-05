from django.urls import path
from .views import PollListView, PollDetailView, VoteView

urlpatterns = [
    path("polls/", PollListView.as_view(), name="polls"),
    path("polls/<int:poll_id>/", PollDetailView.as_view(), name="poll-detail"),
    path("polls/<int:poll_id>/vote/", VoteView.as_view(), name="vote"),
]
