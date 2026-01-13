from django.contrib import admin
from .models import Poll, Vote, Report


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "is_active", "created_at")
    search_fields = ("question",)
    list_filter = ("is_active",)
    ordering = ("-created_at",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "poll", "device_id", "vote_value", "created_at")
    search_fields = ("device_id",)
    list_filter = ("vote_value", "poll")
    ordering = ("-created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "poll", "reported_at", "device_id")
    search_fields = ("poll__question",)
    list_filter = ("reported_at",)
    ordering = ("-reported_at",)