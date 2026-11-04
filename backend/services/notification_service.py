from datetime import datetime, timezone, timedelta

def generate_notifications(activities, user_id):
    now = datetime.now(timezone.utc)
    notifications = []

    for activity in activities:
        if activity.get("user_id") != user_id:
            continue

        if activity.get("status") == "Completed":
            continue

        try:
            due = datetime.fromisoformat(
                activity["due_date"].replace("Z", "+00:00")
            )

            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)

            remaining = due - now

            if remaining.total_seconds() < 0:
                notifications.append({
                    "type": "overdue",
                    "title": "Overdue activity",
                    "message": activity.get("title", "Activity") + " is overdue.",
                    "activity_id": activity.get("activity_id"),
                    "due_date": activity.get("due_date")
                })

            elif remaining <= timedelta(hours=24):
                notifications.append({
                    "type": "urgent",
                    "title": "Deadline approaching",
                    "message": activity.get("title", "Activity") + " is due within 24 hours.",
                    "activity_id": activity.get("activity_id"),
                    "due_date": activity.get("due_date")
                })

            elif remaining <= timedelta(days=3):
                notifications.append({
                    "type": "reminder",
                    "title": "Upcoming deadline",
                    "message": activity.get("title", "Activity") + " is due within 3 days.",
                    "activity_id": activity.get("activity_id"),
                    "due_date": activity.get("due_date")
                })

        except (ValueError, TypeError, KeyError):
            continue

    return notifications
