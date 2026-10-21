from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at', 'updated_at')
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ", ".join([u.username for u in obj.participants.all()])
    get_participants.short_description = "Participants"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content_snippet', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username')

    def content_snippet(self, obj):
        return obj.content[:50]
    content_snippet.short_description = "Content"
