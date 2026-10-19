from django.db import models
from django.contrib.auth.models import User

class SpeedNetworkingSession(models.Model):
    title = models.CharField(max_length=200, default="Thursday Founder Speed Networking")
    scheduled_time = models.CharField(max_length=100, default="Thursday, 7:00 PM IST")
    active_queue_count = models.IntegerField(default=42)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.scheduled_time})"


class SpeedNetworkingQueue(models.Model):
    session = models.ForeignKey(SpeedNetworkingSession, on_delete=models.CASCADE, related_name='queue_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speed_networking_entries')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.session.title}"
