from django.urls import path
from . import views

urlpatterns = [
    path('pitch-wall/', views.pitch_wall, name='pitch_wall'),
    path('pitch/<int:pitch_id>/upvote/', views.upvote_pitch, name='upvote_pitch'),
    path('co-founders/', views.co_founders, name='co_founders'),
    path('co-founders/application/<int:application_id>/respond/', views.respond_cofounder_application, name='respond_cofounder_application'),
    path('challenges/', views.challenges, name='challenges'),
]
