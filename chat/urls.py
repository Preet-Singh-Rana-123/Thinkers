from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<int:conversation_id>/', views.inbox_view, name='conversation_detail'),
    path('start/<str:username>/', views.start_or_get_conversation, name='start_chat'),
    path('api/<int:conversation_id>/send/', views.send_message_api, name='send_message_api'),
    path('api/<int:conversation_id>/poll/', views.get_messages_api, name='get_messages_api'),
    path('api/unread-count/', views.chat_unread_count_api, name='chat_unread_count_api'),
]
