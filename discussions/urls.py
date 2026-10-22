from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_list, name='forum_list'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('thread/<int:thread_id>/upvote/', views.upvote_thread, name='upvote_thread'),
    # Live Discussion Meeting Rooms & Club Activities
    path('meetings/', views.meeting_directory, name='meeting_directory'),
    path('meeting/<slug:room_slug>/', views.join_meeting_room, name='join_meeting_room'),
    path('meeting/<slug:room_slug>/api/heartbeat/', views.meeting_heartbeat_api, name='meeting_heartbeat_api'),
    path('meeting/<slug:room_slug>/api/signal/send/', views.meeting_signal_send_api, name='meeting_signal_send_api'),
    path('meeting/<slug:room_slug>/api/signal/poll/', views.meeting_signal_poll_api, name='meeting_signal_poll_api'),
    path('meeting/<slug:room_slug>/api/chat/', views.meeting_chat_api, name='meeting_chat_api'),
    path('meeting/<slug:room_slug>/api/activity/', views.meeting_activity_api, name='meeting_activity_api'),
    path('meeting/<slug:room_slug>/api/demo-peers/', views.meeting_demo_peers_api, name='meeting_demo_peers_api'),
    path('meeting/<slug:room_slug>/api/leave/', views.meeting_leave_api, name='meeting_leave_api'),
]

