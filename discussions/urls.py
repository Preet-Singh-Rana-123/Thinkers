from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_list, name='forum_list'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
]
