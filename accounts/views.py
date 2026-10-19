from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, UserProject, CoffeeChatRequest
from clubs.models import ClubMembership
from collaboration.models import Pitch

def login_view(request):
    """Classy comic-styled login page with real authentication."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Try username directly or by email
        user = authenticate(request, username=username, password=password)
        if not user:
            user_by_email = User.objects.filter(email=username).first()
            if user_by_email:
                user = authenticate(request, username=user_by_email.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! You are logged in.")
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password. Try 'preet_builder' with 'password123' for demo!")

    return render(request, "accounts/login.html")


def register_view(request):
    """Role-based registration for founders, mentors, investors, and students."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        role = request.POST.get('role', 'Founder')
        college = request.POST.get('college', '').strip()

        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, "accounts/register.html")

        first_name = full_name.split()[0] if full_name else username
        last_name = " ".join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else ""

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        role_badge_map = {
            "Technical Founder": "yellow",
            "Growth & Marketing": "cyan",
            "Product Designer": "pink",
            "Hardware & IoT": "purple",
            "Student Hustler": "green",
        }
        role_badge = role_badge_map.get(role, "yellow")

        initials = (first_name[:1] + (last_name[:1] if last_name else username[1:2])).upper()

        UserProfile.objects.create(
            user=user,
            role=role,
            role_badge=role_badge,
            college=college or "Campus Network",
            avatar=initials,
            headline=f"{role} building high-impact ventures",
            bio="Just joined the Thinkers Entrepreneur Clubhouse. Excited to collaborate, pitch, and build!",
            skills_text="Python, Prototyping, Strategy",
            seeking="Looking for co-founders and early beta testers"
        )

        login(request, user)
        messages.success(request, f"Account created! Welcome to the Thinkers Entrepreneur Network, {first_name}!")
        return redirect('profile')

    return render(request, "accounts/register.html")


def profile_view(request):
    """User Dashboard & Profile Hub showing joined clubs, pitches, and matches."""
    user = request.user if request.user.is_authenticated else User.objects.filter(username="preet_builder").first()
    if not user:
        user = User.objects.first()

    profile = getattr(user, 'profile', None) if user else None

    # Load real clubs joined
    memberships = ClubMembership.objects.filter(user=user).select_related('club') if user else []
    clubs_joined = []
    for m in memberships:
        clubs_joined.append({
            "name": m.club.name,
            "slug": m.club.slug,
            "role": m.role,
            "badge_color": m.club.badge_color,
        })

    # Load real pitches submitted by user
    pitches = Pitch.objects.filter(founder_user=user) if user else []
    my_pitches = []
    for p in pitches:
        my_pitches.append({
            "title": p.title,
            "stage": p.stage,
            "upvotes": p.upvotes,
            "seeking": p.seeking,
        })

    # Load real coffee chat requests received
    chat_requests = CoffeeChatRequest.objects.filter(to_user=user).order_by('-created_at') if user else []
    match_requests = []
    for req in chat_requests:
        match_requests.append({
            "from_user": req.from_user.get_full_name() or req.from_user.username,
            "topic": req.topic,
            "time": req.created_at.strftime("%b %d, %H:%M"),
        })

    user_data = {
        "name": user.get_full_name() or user.username if user else "Preet Rana",
        "username": user.username if user else "preet_builder",
        "role": profile.role if profile else "Full-Stack Founder",
        "college": profile.college if profile else "College of Engineering",
        "avatar": profile.avatar if profile else "PR",
        "bio": profile.bio if profile else "Building scalable web platforms and student networks.",
        "clubs_joined": clubs_joined,
        "my_pitches": my_pitches,
        "match_requests": match_requests,
    }

    return render(request, "accounts/profile.html", {"user_data": user_data})


def logout_view(request):
    """Log out view."""
    logout(request)
    messages.info(request, "You have been logged out. See you at the next pitch night!")
    return redirect('home')
