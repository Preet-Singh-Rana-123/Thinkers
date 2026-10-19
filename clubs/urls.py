from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('create/', views.club_create, name='club_create'),
    path('<slug:club_slug>/', views.club_detail, name='club_detail'),
    path('<slug:club_slug>/join/', views.club_join, name='club_join'),
]
