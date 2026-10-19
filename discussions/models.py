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
