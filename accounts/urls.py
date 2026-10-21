from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('coffee-chat/<int:request_id>/respond/', views.respond_coffee_chat, name='respond_coffee_chat'),
    path('notifications/<int:notification_id>/open/', views.open_notification, name='open_notification'),
    path('notifications/read-all/', views.mark_notifications_read, name='mark_notifications_read'),
    path('logout/', views.logout_view, name='logout'),
]
