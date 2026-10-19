from django.contrib import admin
from .models import Club, ClubMembership, ClubAnnouncement, ClubEvent

class ClubMembershipInline(admin.TabularInline):
    model = ClubMembership
    extra = 1

class ClubAnnouncementInline(admin.StackedInline):
    model = ClubAnnouncement
    extra = 1

class ClubEventInline(admin.TabularInline):
    model = ClubEvent
    extra = 1

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_label', 'lead', 'university', 'members_count_display', 'created_at')
    list_filter = ('category', 'badge_color')
    search_fields = ('name', 'lead', 'university', 'tagline', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ClubMembershipInline, ClubAnnouncementInline, ClubEventInline]

    def members_count_display(self, obj):
        return obj.members_count
    members_count_display.short_description = 'Members'

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'role', 'joined_at')
    list_filter = ('club', 'role')
    search_fields = ('user__username', 'club__name', 'role')

@admin.register(ClubAnnouncement)
class ClubAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('club', 'badge', 'author_display', 'created_at')
    list_filter = ('club', 'badge')
    search_fields = ('content', 'badge', 'club__name')

    def author_display(self, obj):
        return obj.author
    author_display.short_description = 'Author'

@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'date', 'type')
    list_filter = ('club', 'type')
    search_fields = ('title', 'description')
