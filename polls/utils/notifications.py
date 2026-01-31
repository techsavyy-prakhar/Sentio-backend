import requests
from ..models import DeviceNotification

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def send_poll_notification(poll):
    tokens = list(
        DeviceNotification.objects.filter(
            is_enabled=True,
        ).exclude(
            device_id=poll.device_id
        ).values_list("push_token", flat=True)
    )


    if not tokens:
        return {"success": False, "message": "No devices registered"}

    messages = []

    for token in tokens:
        messages.append({
            "to": token,
            "sound": "default",
            "title": "🗳️ New Poll is Live!",
            "body": poll.question[:120],  
            "data": {
                "pollId": poll.id,
                "screen": "poll",
            }
        })

    response = requests.post(
        EXPO_PUSH_URL,
        json=messages,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=100
    )

    return response.json()
