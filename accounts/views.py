from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    """Classy comic-styled login page with demo autofill."""
    if request.method == 'POST':
        messages.success(request, "Welcome back, Boss! You are logged in.")
        return redirect('profile')
    return render(request, "accounts/login.html")


def register_view(request):
    """Role-based registration for founders, mentors, investors, and students."""
    if request.method == 'POST':
        messages.success(request, "Account created! Welcome to the Thinkers Entrepreneur Network.")
        return redirect('profile')
    return render(request, "accounts/register.html")


def profile_view(request):
    """User Dashboard & Profile Hub showing joined clubs, pitches, and matches."""
    user_data = {
        "name": "Preet Rana",
        "username": "preet_builder",
        "role": "Full-Stack Founder",
        "college": "College of Engineering (Sem 7)",
        "avatar": "PR",
        "bio": "Building scalable web platforms, distributed architectures, and student entrepreneur networks.",
        "clubs_joined": [
            {"name": "GenAI Disruptors Club", "slug": "genai-disruptors", "role": "Active Hacker", "badge_color": "purple"},
            {"name": "SaaS Growth Syndicate", "slug": "saas-growth-syndicate", "role": "Product Lead", "badge_color": "cyan"},
        ],
        "my_pitches": [
            {"title": "Thinkers Network", "stage": "Alpha MVP", "upvotes": 420, "seeking": "Beta Testers"},
        ],
        "match_requests": [
            {"from_user": "Aarav Sharma", "topic": "Co-Founding Tech Stack Synergy", "time": "2 hours ago"},
            {"from_user": "Priya Sen", "topic": "Design System Audit for App", "time": "Yesterday"},
        ]
    }
    return render(request, "accounts/profile.html", {"user_data": user_data})


def logout_view(request):
    """Log out view."""
    messages.info(request, "You have been logged out. See you at the next pitch night!")
    return redirect('home')
