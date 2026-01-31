from django.urls import path
from .views import PollListView, PollDetailView, VoteView, ReportPollView, RegisterDeviceView

urlpatterns = [
    path("polls/", PollListView.as_view(), name="polls"),
    path("polls/<int:poll_id>/", PollDetailView.as_view(), name="poll-detail"),
    path("polls/<int:poll_id>/vote/", VoteView.as_view(), name="vote"),
    path("polls/<int:poll_id>/report/", ReportPollView.as_view(), name="vote"),
    path("register-device/", RegisterDeviceView.as_view()),



]
