from django.contrib import admin
from .models import Poll, Vote, Report, BlockedDevice, DeviceNotification


# -----------------------
# Poll Admin
# -----------------------
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_question",
        "device_id",
        "is_active",
        "created_at",
        "updated_at",
        "report_count",
    )

    search_fields = ("question", "description", "device_id")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)
    list_per_page = 25

    actions = ["disable_polls", "enable_polls"]

    def short_question(self, obj):
        return obj.question[:60] + "..." if len(obj.question) > 60 else obj.question
    short_question.short_description = "Question"

    def report_count(self, obj):
        return obj.reports.count()
    report_count.short_description = "Reports"

    @admin.action(description="❌ Disable selected polls")
    def disable_polls(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="✅ Enable selected polls")
    def enable_polls(self, request, queryset):
        queryset.update(is_active=True)


# -----------------------
# Vote Admin
# -----------------------
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "poll",
        "device_id",
        "vote_value",
        "created_at",
    )

    search_fields = ("device_id", "poll__question")
    list_filter = ("vote_value", "created_at")
    ordering = ("-created_at",)
    list_per_page = 50


# -----------------------
# Report Admin
# -----------------------
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "poll",
        "device_id",           # offender
        "reporter_device_id",  # reporter
        "reported_at",
    )

    search_fields = (
        "poll__question",
        "device_id",
        "reporter_device_id",
    )

    list_filter = ("reported_at",)
    ordering = ("-reported_at",)
    list_per_page = 50


# -----------------------
# Blocked Device Admin
# -----------------------
@admin.register(BlockedDevice)
class BlockedDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "reason",
        "blocked_at",
    )

    search_fields = ("device_id",)
    ordering = ("-blocked_at",)
    list_per_page = 50


@admin.register(DeviceNotification)
class DeviceNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "push_token",
        "is_enabled",
        "created_at",
    )
    search_fields = ("device_id", "push_token")
    list_filter = ("is_enabled", "created_at")
    ordering = ("-created_at",)
    list_per_page = 25