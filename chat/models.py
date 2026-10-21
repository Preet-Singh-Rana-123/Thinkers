from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = ", ".join([u.username for u in self.participants.all()])
        return f"Chat ({self.id}): {participant_names}"

    def get_other_participant(self, user):
        """Return the other participant in a 1-on-1 conversation."""
        if not user:
            return self.participants.first()
        other = self.participants.exclude(id=user.id).first()
        return other or self.participants.first()

    @property
    def last_message(self):
        """Return the latest message in this conversation."""
        return self.messages.order_by('-created_at').first()

    def unread_count_for(self, user):
        """Return number of unread messages sent by others to user."""
        if not user or not user.is_authenticated:
            return 0
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def mark_as_read(self, user):
        """Mark all unread incoming messages as read for this user."""
        if not user or not user.is_authenticated:
            return 0
        return self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    @classmethod
    def get_or_create_direct_chat(cls, user1, user2):
        """Get existing 1-on-1 conversation or create one."""
        if user1 == user2:
            return None, False

        # Find existing conversation with both users
        existing_convs = cls.objects.filter(participants=user1).filter(participants=user2)
        for conv in existing_convs:
            if conv.participants.count() == 2:
                return conv, False

        new_conv = cls.objects.create()
        new_conv.participants.add(user1, user2)
        return new_conv, True


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.content[:30]}"

    @property
    def formatted_time(self):
        return self.created_at.strftime('%I:%M %p')

    @property
    def formatted_date(self):
        return self.created_at.strftime('%b %d, %Y')

    @property
    def sender_avatar(self):
        if hasattr(self.sender, 'profile') and self.sender.profile.avatar:
            return self.sender.profile.avatar
        first = self.sender.first_name[:1] if self.sender.first_name else self.sender.username[:1]
        last = self.sender.last_name[:1] if self.sender.last_name else ''
        return (first + last).upper() or "TH"

    @property
    def sender_name(self):
        return self.sender.get_full_name() or self.sender.username
