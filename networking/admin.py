from django.contrib import admin
from .models import SpeedNetworkingSession, SpeedNetworkingQueue

@admin.register(SpeedNetworkingSession)
class SpeedNetworkingSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'scheduled_time', 'active_queue_count', 'is_active', 'created_at')

@admin.register(SpeedNetworkingQueue)
class SpeedNetworkingQueueAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'joined_at')
