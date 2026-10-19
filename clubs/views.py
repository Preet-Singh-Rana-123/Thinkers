from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from .models import Club, ClubMembership, ClubAnnouncement, ClubEvent

CATEGORY_LABELS = {
    'ai': 'AI & DeepTech',
    'saas': 'B2B SaaS',
    'd2c': 'D2C & Consumer',
    'clean': 'CleanTech & Hardware',
    'greentech': 'CleanTech & Hardware',
    'fintech': 'FinTech & Web3',
    'hustle': 'Campus Hustle & Agency',
    'student': 'Campus Hustle & Agency',
    'edtech': 'EdTech & Learning',
}

def club_list(request):
    """Explore all entrepreneur clubs with filtering by category and search query from DB."""
    category = request.GET.get('cat', 'all')
    search_query = request.GET.get('q', '').strip()

    clubs = Club.objects.all().order_by('-id')

    if category != 'all':
        clubs = clubs.filter(category=category)

    if search_query:
        clubs = clubs.filter(
            Q(name__icontains=search_query) |
            Q(tagline__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags_text__icontains=search_query)
        )

    context = {
        "clubs": clubs,
        "current_category": category,
        "search_query": search_query,
        "total_clubs_count": Club.objects.count(),
    }
    return render(request, "clubs/club_list.html", context)


def club_detail(request, club_slug):
    """Single Club Interactive Clubhouse with tabs for feed, pitches, events, and members."""
    club = get_object_or_404(Club, slug=club_slug)

    # Handle post to feed
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            author_user = request.user if request.user.is_authenticated else None
            author_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else "Founder"
            ClubAnnouncement.objects.create(
                club=club,
                author_user=author_user,
                author_name=author_name,
                content=content,
                badge="MEMBER UPDATE"
            )
            messages.success(request, f"Update posted to {club.name}!")
            return redirect('club_detail', club_slug=club.slug)

    context = {
        "club": club,
    }
    return render(request, "clubs/club_detail.html", context)


def club_create(request):
    """Create a new Entrepreneur Club page with comic styled wizard and save to DB."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "ai")
        university = request.POST.get("university", "Cross-Campus (Pan-India)").strip()
        tagline = request.POST.get("tagline", "").strip()
        description = request.POST.get("description", "").strip()
        frequency = request.POST.get("frequency", "Every Thursday @ 8:00 PM IST")
        color_theme = request.POST.get("color_theme", "yellow")
        tags = request.POST.get("tags", "").strip()

        if name:
            category_label = CATEGORY_LABELS.get(category, category.title())
            badge_color = color_theme
            bg_color = f"comic-box-{color_theme}"
            lead_name = (request.user.get_full_name() or request.user.username) if request.user.is_authenticated else "Student Founder"
            founder_user = request.user if request.user.is_authenticated else None

            club = Club.objects.create(
                name=name,
                category=category,
                category_label=category_label,
                university=university or "Cross-Campus",
                tagline=tagline,
                description=description,
                frequency=frequency,
                badge_color=badge_color,
                bg_color=bg_color,
                lead=lead_name,
                founder=founder_user,
                tags_text=tags,
                members_count_cache=1
            )

            # Auto-join creator
            if founder_user:
                ClubMembership.objects.create(club=club, user=founder_user, role="Club Founder & Lead")

            # Add welcome announcement
            ClubAnnouncement.objects.create(
                club=club,
                author_user=founder_user,
                author_name=lead_name,
                content=f"Welcome to the official clubhouse of {club.name}! Introduce yourself below.",
                badge="WELCOME"
            )

            # Add initial event
            ClubEvent.objects.create(
                club=club,
                title="Kickoff Mastermind & Introductions",
                date=frequency,
                type="Kickoff",
                order=1
            )

            messages.success(request, f"BOOM! '{name}' was created successfully! Your club room is now live.")
            return redirect('club_detail', club_slug=club.slug)

    return render(request, "clubs/club_create.html")


def club_join(request, club_slug):
    """Join a club."""
    club = get_object_or_404(Club, slug=club_slug)
    if request.user.is_authenticated:
        membership, created = ClubMembership.objects.get_or_create(
            club=club,
            user=request.user,
            defaults={"role": "Active Member"}
        )
        if created:
            messages.success(request, f"You joined {club.name}!")
        else:
            messages.info(request, f"You are already a member of {club.name}!")
    else:
        messages.success(request, f"Joined {club.name} in demo mode!")
    return redirect('club_detail', club_slug=club.slug)
