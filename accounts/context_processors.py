from django.contrib.auth.models import User
from .models import Notification

def notifications_context(request):
    """Context processor providing live notifications and unread message counts for the logged in user or demo user."""
    from chat.models import Message

    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(recipient=request.user)
        unread_count = user_notifications.filter(is_read=False).count()
        recent = list(user_notifications[:8])
        unread_messages = Message.objects.filter(
            conversation__participants=request.user, 
            is_read=False
        ).exclude(sender=request.user).count()

        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent,
            'unread_messages_count': unread_messages,
        }

    # Guest / Demo founder preview notifications
    demo_user = User.objects.filter(username="preet_builder").first()
    if demo_user:
        demo_notifications = Notification.objects.filter(recipient=demo_user)
        unread_count = demo_notifications.filter(is_read=False).count() if demo_notifications.exists() else 2
        recent = list(demo_notifications[:6]) if demo_notifications.exists() else []
        unread_messages = Message.objects.filter(
            conversation__participants=demo_user, 
            is_read=False
        ).exclude(sender=demo_user).count()
    else:
        unread_count = 2
        recent = []
        unread_messages = 0

    if not recent:
        recent = [
            {
                "actor_name": "Aarav Sharma",
                "actor_avatar": "AS",
                "verb": "sent you a 1-on-1 coffee chat invite for 'Co-Founding Tech Stack Synergy'",
                "target_url": "/accounts/profile/",
                "is_read": False,
                "timesince_display": "2 hours ago",
            },
            {
                "actor_name": "Priya Sen",
                "actor_avatar": "PS",
                "verb": "sent you a coffee chat invite for 'Design System Audit'",
                "target_url": "/accounts/profile/",
                "is_read": False,
                "timesince_display": "5 hours ago",
            },
            {
                "actor_name": "Tanvi Chawla",
                "actor_avatar": "TC",
                "verb": "replied to your mastermind thread on micro-SaaS pricing!",
                "target_url": "/community/",
                "is_read": True,
                "timesince_display": "Yesterday",
            },
        ]

    return {
        'unread_notifications_count': unread_count,
        'recent_notifications': recent,
        'unread_messages_count': unread_messages,
    }
