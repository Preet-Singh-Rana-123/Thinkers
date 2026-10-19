from django.contrib import admin
from .models import UserProfile, UserProject, CoffeeChatRequest

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'role', 'college', 'role_badge', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'college', 'skills_text')
    list_filter = ('role_badge',)

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'stars', 'created_at')
    search_fields = ('title', 'user__username')

@admin.register(CoffeeChatRequest)
class CoffeeChatRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'focus', 'status', 'created_at')
    list_filter = ('status', 'focus')
