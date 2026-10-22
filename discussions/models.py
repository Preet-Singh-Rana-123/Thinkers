from django.db import models
from django.contrib.auth.models import User
from clubs.models import Club

class DiscussionChannel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    badge = models.CharField(max_length=50, default='POPULAR')
    badge_color = models.CharField(max_length=20, default='yellow')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Thread(models.Model):
    channel = models.ForeignKey(DiscussionChannel, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=300)
    author_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_threads')
    author_name = models.CharField(max_length=150, blank=True)
    author_role = models.CharField(max_length=100, default='Founder')
    author_avatar = models.CharField(max_length=10, default='TH')
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='club_threads')
    club_name_fallback = models.CharField(max_length=150, blank=True, default='')
    content = models.TextField()
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def author(self):
        if self.author_name:
            return self.author_name
        if self.author_user:
            return self.author_user.get_full_name() or self.author_user.username
        return "Founder"

    @property
    def club_display(self):
        if self.club:
            return self.club.name
        return self.club_name_fallback or "Thinkers Community"

    @property
    def replies_count(self):
        return self.replies.count()


class ThreadReply(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    author_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_replies')
    author_name = models.CharField(max_length=150, blank=True)
    author_role = models.CharField(max_length=100, default='Founder')
    author_avatar = models.CharField(max_length=10, default='TH')
    content = models.TextField()
    upvotes = models.IntegerField(default=0)
    is_top_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_top_answer', '-upvotes', 'created_at']

    def __str__(self):
        return f"Reply by {self.author} on #{self.thread.id}"

    @property
    def author(self):
        if self.author_name:
            return self.author_name
        if self.author_user:
            return self.author_user.get_full_name() or self.author_user.username
        return "Founder"


class ThreadUpvote(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='thread_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_thread_upvotes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('thread', 'user')

    def __str__(self):
        return f"{self.user.username} upvoted #{self.thread.id}"


class MeetingRoom(models.Model):
    MEETING_TYPES = [
        ('club_mastermind', 'Club Live Mastermind'),
        ('pitch_roast', 'Pitch Roast & Elevator Pitches'),
        ('open_discussion', 'Open Founder Discussion'),
        ('brainstorm', 'Whiteboard & Ideation'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, default='')
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings')
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings')
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hosted_meetings')
    host_name = models.CharField(max_length=150, blank=True, default='Club Lead')
    meeting_type = models.CharField(max_length=50, choices=MEETING_TYPES, default='club_mastermind')
    badge_color = models.CharField(max_length=30, default='purple')
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=16)
    current_activity = models.CharField(max_length=50, default='discussion')  # 'discussion', 'pitch_timer', 'icebreaker', 'notes'
    activity_state = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.slug})"

    @property
    def active_participants_count(self):
        from django.utils import timezone
        import datetime
        cutoff = timezone.now() - datetime.timedelta(seconds=25)
        count = self.participants.filter(is_active=True, last_seen__gte=cutoff).count()
        # If in demo mode and 0, provide baseline visual count
        return count if count > 0 else 1

    @property
    def club_display(self):
        if self.club:
            return self.club.name
        return "Thinkers Global Hub"


class MeetingParticipant(models.Model):
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='meeting_participations')
    session_id = models.CharField(max_length=64, db_index=True)
    display_name = models.CharField(max_length=150)
    role = models.CharField(max_length=60, default='Active Member')
    avatar = models.CharField(max_length=10, default='TH')
    color = models.CharField(max_length=30, default='yellow')
    has_video = models.BooleanField(default=True)
    has_audio = models.BooleanField(default=True)
    is_screen_sharing = models.BooleanField(default=False)
    hand_raised = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'session_id')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.display_name} in {self.room.slug} ({self.session_id[:8]})"


class MeetingSignal(models.Model):
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='signals')
    from_session = models.CharField(max_length=64)
    to_session = models.CharField(max_length=64, db_index=True)  # target peer or 'broadcast'
    signal_type = models.CharField(max_length=50)  # 'offer', 'answer', 'ice_candidate', 'reaction', 'peer_joined', 'peer_left'
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Signal {self.signal_type} from {self.from_session[:6]} to {self.to_session[:6]}"


class MeetingChatMessage(models.Model):
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='messages')
    sender_session = models.CharField(max_length=64)
    sender_name = models.CharField(max_length=150)
    sender_avatar = models.CharField(max_length=10, default='TH')
    sender_color = models.CharField(max_length=30, default='yellow')
    sender_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    message_type = models.CharField(max_length=30, default='chat')  # 'chat', 'system', 'pitch_vote', 'activity'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender_name} in {self.room.slug}"

