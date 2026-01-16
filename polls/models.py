from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    device_id = models.CharField(max_length=255, default="UNKNOWN_DEVICE")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class Vote(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    device_id = models.CharField(max_length=255, default="UNKNOWN_DEVICE")
    vote_value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("poll", "device_id")

    def __str__(self):
        return f"{self.device_id} → {self.poll_id}"


class Report(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    reporter_device_id = models.CharField(max_length=255, null=True, blank=True, default="ANONYMOUS")
    device_id = models.CharField(max_length=255, null=True, blank=True, default="ANONYMOUS")
    reason = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("poll", "reporter_device_id")

    def __str__(self):
        return f"Report for Poll {self.poll.id} by {self.reporter_device_id}"


class BlockedDevice(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    reason = models.TextField(blank=True)
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blocked: {self.device_id}"
