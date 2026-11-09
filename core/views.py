import time
from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render
from core.models import PlatformStat, Testimonial
from clubs.models import Club
from collaboration.models import Pitch

def home(request):
    """Home / Landing page with high-energy comic style hero, club previews, featured pitch cards, live stats, and founder testimonials."""
    stats = PlatformStat.objects.all()
    if not stats.exists():
        stats = [
            {"number": "180+", "label": "Active Entrepreneur Clubs", "color": "yellow"},
            {"number": "5,400+", "label": "Innovators & Hustlers", "color": "pink"},
            {"number": "$2.8M+", "label": "College Startup Grants", "color": "green"},
            {"number": "340+", "label": "Co-Founders Paired", "color": "cyan"},
        ]

    featured_clubs = Club.objects.all().order_by('-id')[:4]
    trending_pitches = Pitch.objects.all().order_by('-upvotes')[:3]
    testimonials = Testimonial.objects.all()

    context = {
        "stats": stats,
        "featured_clubs": featured_clubs,
        "trending_pitches": trending_pitches,
        "testimonials": testimonials,
    }
    return render(request, "core/index.html", context)


def about(request):
    """About the Thinkers platform: Mission, origin story, comic principles, and why interactive clubs outperform traditional networking."""
    return render(request, "core/about.html")


def how_it_works(request):
    """Interactive comic guide: 4 step roadmap to entrepreneur club success."""
    return render(request, "core/how_it_works.html")


def health_check(request):
    """Health check endpoint for ALB, Docker container, and Prometheus uptime monitoring."""
    db_status = "healthy"
    try:
        connection.ensure_connection()
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    is_healthy = db_status == "healthy"
    status_code = 200 if is_healthy else 503

    return JsonResponse({
        "status": "healthy" if is_healthy else "degraded",
        "service": "thinkers-platform",
        "database": db_status,
        "timestamp": int(time.time()),
    }, status=status_code)

