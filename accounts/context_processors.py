from django.contrib.auth.models import User
from .models import Notification

def notifications_context(request):
    """Context processor providing live notifications for the logged in user or demo notifications for preview."""
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(recipient=request.user)
        unread_count = user_notifications.filter(is_read=False).count()
        recent = list(user_notifications[:8])
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent,
        }

    # Guest / Demo founder preview notifications
    demo_user = User.objects.filter(username="preet_builder").first()
    if demo_user and Notification.objects.filter(recipient=demo_user).exists():
        demo_notifications = Notification.objects.filter(recipient=demo_user)
        unread_count = demo_notifications.filter(is_read=False).count()
        recent = list(demo_notifications[:6])
    else:
        unread_count = 2
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
    }
