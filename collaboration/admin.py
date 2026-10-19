from django.contrib import admin
from .models import Pitch, PitchUpvote, CoFounderPost, CoFounderApplication, StartupChallenge

@admin.register(Pitch)
class PitchAdmin(admin.ModelAdmin):
    list_display = ('title', 'founder_display', 'club_display', 'stage', 'category', 'upvotes', 'created_at')
    list_filter = ('stage', 'category', 'stage_color')
    search_fields = ('title', 'one_liner', 'problem', 'solution', 'founder_name', 'founder_user__username')

    def founder_display(self, obj):
        return obj.founder
    founder_display.short_description = 'Founder'

    def club_display(self, obj):
        return obj.club.name if obj.club else obj.club_name_fallback
    club_display.short_description = 'Club'

@admin.register(PitchUpvote)
class PitchUpvoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'pitch', 'created_at')

@admin.register(CoFounderPost)
class CoFounderPostAdmin(admin.ModelAdmin):
    list_display = ('startup_name', 'role_needed', 'founder_display', 'equity', 'commitment', 'location')
    search_fields = ('startup_name', 'role_needed', 'description', 'skills_text')

    def founder_display(self, obj):
        return obj.founder
    founder_display.short_description = 'Founder'

@admin.register(CoFounderApplication)
class CoFounderApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'post', 'created_at')

@admin.register(StartupChallenge)
class StartupChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'prize_pool', 'deadline', 'hosted_by', 'participants')
