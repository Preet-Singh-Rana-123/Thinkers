from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Club(models.Model):
    CATEGORY_CHOICES = [
        ('all', 'All Clubs'),
        ('ai', 'AI & DeepTech'),
        ('d2c', 'D2C & Consumer'),
        ('saas', 'B2B SaaS'),
        ('clean', 'CleanTech & Hardware'),
        ('fintech', 'FinTech & Web3'),
        ('hustle', 'Campus Hustle & Agency'),
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='ai')
    category_label = models.CharField(max_length=100, default='AI & DeepTech')
    badge_color = models.CharField(max_length=30, default='purple')
    bg_color = models.CharField(max_length=50, default='comic-box-purple')
    tagline = models.CharField(max_length=255)
    description = models.TextField()
    lead = models.CharField(max_length=200, help_text="e.g. Aarav Sharma & Priya Sen")
    founder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='founded_clubs')
    university = models.CharField(max_length=200, default='Cross-Campus (Pan-India)')
    frequency = models.CharField(max_length=150, default='Every Thursday @ 8:00 PM IST')
    tags_text = models.CharField(max_length=255, blank=True, default='', help_text="Comma-separated tags")
    members_count_cache = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def tags(self):
        if not self.tags_text:
            return []
        return [t.strip() for t in self.tags_text.split(',') if t.strip()]

    @property
    def members_count(self):
        real_count = self.memberships.count()
        return real_count if real_count > 0 else self.members_count_cache

    @property
    def announcements(self):
        return self.club_announcements.all().order_by('-created_at')

    @property
    def upcoming_events(self):
        return self.events.all().order_by('order', 'created_at')

    @property
    def pitches(self):
        return self.club_pitches.all().order_by('-upvotes')

    @property
    def members(self):
        member_list = []
        for m in self.memberships.select_related('user', 'user__profile').all():
            profile = getattr(m.user, 'profile', None)
            color = profile.role_badge if profile else 'yellow'
            avatar = profile.avatar if profile and profile.avatar else (m.user.username[:2].upper() if m.user.username else 'TH')
            member_list.append({
                'name': m.user.get_full_name() or m.user.username,
                'role': m.role,
                'avatar': avatar,
                'color': color,
                'username': m.user.username,
            })
        return member_list


class ClubMembership(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=100, default='Active Member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('club', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.club.name} ({self.role})"


class ClubAnnouncement(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club_announcements')
    author_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_announcements')
    author_name = models.CharField(max_length=150, blank=True)
    content = models.TextField()
    badge = models.CharField(max_length=50, default='ANNOUNCEMENT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Announcement in {self.club.name}: {self.badge}"

    @property
    def author(self):
        if self.author_name:
            return self.author_name
        if self.author_user:
            return self.author_user.get_full_name() or self.author_user.username
        return "Club Lead"

    @property
    def date(self):
        return self.created_at.strftime("%b %d, %Y")


class ClubEvent(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    date = models.CharField(max_length=100, default='Tomorrow, 8:00 PM')
    type = models.CharField(max_length=50, default='Workshop')
    description = models.TextField(blank=True, default='')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.club.name})"
