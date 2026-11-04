from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

CATEGORY_ALIASES = {
    'greentech': 'clean',
    'student': 'hustle',
}

def club_list(request):
    """Explore all entrepreneur clubs with filtering by category, search query, and 9-per-page pagination."""
    category = request.GET.get('cat', 'all')
    search_query = request.GET.get('q', '').strip()

    clubs = Club.objects.all().order_by('-id')

    # Resolve category aliases
    canonical_cat = CATEGORY_ALIASES.get(category, category)

    if category != 'all':
        clubs = clubs.filter(Q(category=canonical_cat) | Q(category=category))

    if search_query:
        clubs = clubs.filter(
            Q(name__icontains=search_query) |
            Q(tagline__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags_text__icontains=search_query)
        )

    total_filtered_count = clubs.count()

    # Pagination: exactly 9 clubs per page
    paginator = Paginator(clubs, 9)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Determine user's joined clubs
    user = request.user if request.user.is_authenticated else User.objects.filter(username="preet_builder").first()
    joined_club_ids = set()
    my_clubs_count = 0
    if user:
        joined_club_ids = set(ClubMembership.objects.filter(user=user).values_list('club_id', flat=True))
        my_clubs_count = len(joined_club_ids)

    context = {
        "clubs": page_obj,
        "page_obj": page_obj,
        "current_category": category,
        "search_query": search_query,
        "total_clubs_count": Club.objects.count(),
        "total_filtered_count": total_filtered_count,
        "joined_club_ids": joined_club_ids,
        "my_clubs_count": my_clubs_count,
    }
    return render(request, "clubs/club_list.html", context)


def my_clubs(request):
    """User's joined clubs hub where user can see the clubs they have joined."""
    user = request.user if request.user.is_authenticated else User.objects.filter(username="preet_builder").first()
    is_demo_view = not request.user.is_authenticated

    memberships = []
    if user:
        memberships = ClubMembership.objects.filter(user=user).select_related('club').order_by('-joined_at')

    total_clubs_count = Club.objects.count()
    my_clubs_count = len(memberships)

    context = {
        "memberships": memberships,
        "total_clubs_count": total_clubs_count,
        "my_clubs_count": my_clubs_count,
        "is_demo_view": is_demo_view,
        "viewed_user": user,
    }
    return render(request, "clubs/my_clubs.html", context)


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

    # Check user membership
    user = request.user if request.user.is_authenticated else User.objects.filter(username="preet_builder").first()
    membership = None
    is_member = False
    if user:
        membership = ClubMembership.objects.filter(club=club, user=user).first()
        is_member = (membership is not None)

    context = {
        "club": club,
        "is_member": is_member,
        "membership": membership,
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
    user = request.user if request.user.is_authenticated else User.objects.filter(username="preet_builder").first()

    if user:
        membership, created = ClubMembership.objects.get_or_create(
            club=club,
            user=user,
            defaults={"role": "Active Member"}
        )
        if created:
            if club.founder and club.founder != user:
                from accounts.models import create_notification
                create_notification(
                    recipient=club.founder,
                    actor=user,
                    verb=f"joined your club '{club.name}' as an Active Member!",
                    notification_type='club_joined',
                    target_url=f"/clubs/{club.slug}/"
                )
            messages.success(request, f"Boom! You joined {club.name}!")
        else:
            messages.info(request, f"You are already an active member of {club.name}!")
    else:
        messages.warning(request, "Please log in to join clubs!")
        return redirect('login')

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('club_detail', club_slug=club.slug)


def club_leave(request, club_slug):
    """Leave a club."""
    club = get_object_or_404(Club, slug=club_slug)
    user = request.user if request.user.is_authenticated else User.objects.filter(username="preet_builder").first()

    if user:
        deleted_count, _ = ClubMembership.objects.filter(club=club, user=user).delete()
        if deleted_count > 0:
            messages.info(request, f"You have left {club.name}.")
        else:
            messages.info(request, f"You were not a member of {club.name}.")
    else:
        messages.warning(request, "Please log in to manage club memberships.")
        return redirect('login')

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('my_clubs')

