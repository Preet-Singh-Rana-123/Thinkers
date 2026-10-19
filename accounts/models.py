from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=100, default='Founder')
    role_badge = models.CharField(max_length=20, default='yellow')
    college = models.CharField(max_length=255, blank=True, default='')
    headline = models.CharField(max_length=255, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    avatar = models.CharField(max_length=10, blank=True, default='')
    skills_text = models.CharField(max_length=300, blank=True, default='', help_text="Comma-separated skills")
    seeking = models.CharField(max_length=255, blank=True, default='')
    badges_text = models.CharField(max_length=300, blank=True, default='', help_text="Comma-separated badges")
    primary_club_name = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (@{self.username})"

    @property
    def username(self):
        return self.user.username

    @property
    def name(self):
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username

    @property
    def skills(self):
        if not self.skills_text:
            return []
        return [s.strip() for s in self.skills_text.split(',') if s.strip()]

    @property
    def badges(self):
        if not self.badges_text:
            return []
        return [b.strip() for b in self.badges_text.split(',') if b.strip()]

    @property
    def club(self):
        if self.primary_club_name:
            return self.primary_club_name
        membership = self.user.club_memberships.first() if hasattr(self.user, 'club_memberships') else None
        if membership:
            return membership.club.name
        return "Thinkers Network"


class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    desc = models.TextField()
    stars = models.CharField(max_length=20, default='100')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class CoffeeChatRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_coffee_chats')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_coffee_chats')
    focus = models.CharField(max_length=120, default='Discuss Co-Founding Opportunity')
    topic = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.from_user.username} -> {self.to_user.username} ({self.status})"
