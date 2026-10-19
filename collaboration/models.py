from django.db import models
from django.contrib.auth.models import User
from clubs.models import Club

class Pitch(models.Model):
    title = models.CharField(max_length=200)
    founder_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_pitches')
    founder_name = models.CharField(max_length=150, blank=True)
    college = models.CharField(max_length=200, default='College Campus')
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='club_pitches')
    club_name_fallback = models.CharField(max_length=150, blank=True, default='')
    stage = models.CharField(max_length=50, default='Prototype / Alpha')
    stage_color = models.CharField(max_length=20, default='yellow')
    category = models.CharField(max_length=100, default='Developer Tools')
    badge = models.CharField(max_length=50, default='HOT PITCH')
    one_liner = models.CharField(max_length=300)
    problem = models.TextField(blank=True, default='')
    solution = models.TextField(blank=True, default='')
    traction = models.TextField(blank=True, default='')
    seeking = models.CharField(max_length=255)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.founder}"

    @property
    def founder(self):
        if self.founder_name:
            return self.founder_name
        if self.founder_user:
            return self.founder_user.get_full_name() or self.founder_user.username
        return "Anonymous Founder"

    @property
    def club_display(self):
        if self.club:
            return self.club.name
        return self.club_name_fallback or "Thinkers Club"


class PitchUpvote(models.Model):
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name='pitch_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_pitch_upvotes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pitch', 'user')

    def __str__(self):
        return f"{self.user.username} upvoted {self.pitch.title}"


class CoFounderPost(models.Model):
    startup_name = models.CharField(max_length=200)
    founder_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='founder_posts')
    founder_name = models.CharField(max_length=150, blank=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='cofounder_posts')
    club_name_fallback = models.CharField(max_length=150, blank=True, default='')
    role_needed = models.CharField(max_length=200)
    equity = models.CharField(max_length=50, default='20% - 30% Equity')
    commitment = models.CharField(max_length=100, default='Part-Time (15 hrs/wk) to Full-Time')
    location = models.CharField(max_length=100, default='Remote / Hybrid')
    description = models.TextField()
    skills_text = models.CharField(max_length=255, help_text="Comma-separated skills")
    badge = models.CharField(max_length=50, default='TOP MATCH')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role_needed} for {self.startup_name}"

    @property
    def founder(self):
        if self.founder_name:
            return self.founder_name
        if self.founder_user:
            return self.founder_user.get_full_name() or self.founder_user.username
        return "Solo Founder"

    @property
    def club_name(self):
        if self.club:
            return self.club.name
        return self.club_name_fallback or "Entrepreneur Club"

    @property
    def skills_required(self):
        if not self.skills_text:
            return []
        return [s.strip() for s in self.skills_text.split(',') if s.strip()]


class CoFounderApplication(models.Model):
    post = models.ForeignKey(CoFounderPost, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cofounder_applications')
    pitch_note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.applicant.username} for {self.post.startup_name}"


class StartupChallenge(models.Model):
    title = models.CharField(max_length=255)
    prize_pool = models.CharField(max_length=100, default='₹1,00,000')
    deadline = models.CharField(max_length=100, default='14 Days Left')
    hosted_by = models.CharField(max_length=200)
    description = models.TextField()
    participants = models.IntegerField(default=0)
    badge = models.CharField(max_length=50, default='PRIZE SPRINT')
    badge_color = models.CharField(max_length=20, default='yellow')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
