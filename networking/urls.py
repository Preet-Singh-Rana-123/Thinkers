from django.urls import path
from . import views

urlpatterns = [
    path('', views.members_list, name='members_list'),
    path('member/<str:username>/', views.member_profile, name='member_profile'),
    path('speed-networking/', views.speed_networking, name='speed_networking'),
]
