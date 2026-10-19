from django.contrib import admin
from .models import DiscussionChannel, Thread, ThreadReply, ThreadUpvote

class ThreadReplyInline(admin.StackedInline):
    model = ThreadReply
    extra = 1

@admin.register(DiscussionChannel)
class DiscussionChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'badge', 'badge_color', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'author_display', 'upvotes', 'replies_count', 'created_at')
    list_filter = ('channel',)
    search_fields = ('title', 'content', 'author_name', 'author_user__username')
    inlines = [ThreadReplyInline]

    def author_display(self, obj):
        return obj.author
    author_display.short_description = 'Author'

@admin.register(ThreadReply)
class ThreadReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author_display', 'upvotes', 'is_top_answer', 'created_at')
    list_filter = ('is_top_answer',)
    search_fields = ('content', 'author_name', 'author_user__username')

    def author_display(self, obj):
        return obj.author
    author_display.short_description = 'Author'

@admin.register(ThreadUpvote)
class ThreadUpvoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'thread', 'created_at')
