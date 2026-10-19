from django.contrib import admin
from .models import Testimonial, PlatformStat

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role', 'club', 'order')

@admin.register(PlatformStat)
class PlatformStatAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'color', 'order')
