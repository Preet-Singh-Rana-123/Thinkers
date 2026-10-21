from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Pitch, PitchUpvote, CoFounderPost, CoFounderApplication, StartupChallenge
from clubs.models import Club

def pitch_wall(request):
    """Pitch Wall showcase page with upvotes, category filters, and pitch deck submission."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        one_liner = request.POST.get("one_liner", "").strip()
        category = request.POST.get("category", "Developer Tools")
        stage = request.POST.get("stage", "Idea / Prototype")
        seeking = request.POST.get("seeking", "").strip()
        problem = request.POST.get("problem", "").strip()
        solution = request.POST.get("solution", "").strip()
        traction = request.POST.get("traction", "").strip()

        stage_color_map = {
            "Idea / Prototype": "yellow",
            "Prototype / Alpha": "yellow",
            "Alpha / Waitlist": "pink",
            "Live Beta": "cyan",
            "Revenue Generating": "green",
            "Pilot Stage": "green",
            "MVP Hardware": "pink",
        }

        if title and one_liner:
            founder_user = request.user if request.user.is_authenticated else None
            founder_name = (request.user.get_full_name() or request.user.username) if request.user.is_authenticated else "Student Founder"
            college = "College of Engineering"
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                college = request.user.profile.college or college

            pitch = Pitch.objects.create(
                title=title,
                one_liner=one_liner,
                category=category,
                stage=stage,
                stage_color=stage_color_map.get(stage, "yellow"),
                seeking=seeking,
                problem=problem or one_liner,
                solution=solution or one_liner,
                traction=traction or "Early prototype with active peer testing.",
                founder_user=founder_user,
                founder_name=founder_name,
                college=college,
                upvotes=1
            )
            messages.success(request, f"Your pitch for '{pitch.title}' has been dropped onto the Pitch Wall!")
            return redirect('pitch_wall')

    category = request.GET.get('cat', 'all')
    pitches = Pitch.objects.all().order_by('-upvotes')
    if category != 'all':
        pitches = pitches.filter(category__icontains=category)

    context = {
        "pitches": pitches,
        "current_category": category,
    }
    return render(request, "collaboration/pitch_wall.html", context)


def upvote_pitch(request, pitch_id):
    """AJAX or redirect endpoint to upvote a pitch."""
    pitch = get_object_or_404(Pitch, id=pitch_id)
    pitch.upvotes += 1
    pitch.save(update_fields=['upvotes'])

    if request.user.is_authenticated:
        PitchUpvote.objects.get_or_create(pitch=pitch, user=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({"success": True, "upvotes": pitch.upvotes})
    
    messages.success(request, f"Upvoted {pitch.title}!")
    return redirect('pitch_wall')


def co_founders(request):
    """Find a Co-Founder Matching Board and post creation."""
    if request.method == "POST":
        action = request.POST.get("action", "create_post")

        if action == "apply":
            post_id = request.POST.get("post_id")
            pitch_note = request.POST.get("pitch_note", "").strip()
            if post_id and request.user.is_authenticated:
                post = get_object_or_404(CoFounderPost, id=post_id)
                app = CoFounderApplication.objects.create(
                    post=post,
                    applicant=request.user,
                    pitch_note=pitch_note or "Interested in connecting!"
                )
                if post.founder_user:
                    from accounts.models import create_notification
                    create_notification(
                        recipient=post.founder_user,
                        actor=request.user,
                        verb=f"applied for {post.role_needed} at {post.startup_name}",
                        notification_type='cofounder_applied',
                        target_url='/collaboration/co-founders/'
                    )
                messages.success(request, f"Application sent to {post.founder} for {post.startup_name}!")
            else:
                messages.success(request, "Application sent! Founder will review your profile.")
            return redirect('co_founders')

        else:
            startup_name = request.POST.get("startup_name", "").strip()
            role_needed = request.POST.get("role_needed", "").strip()
            equity = request.POST.get("equity", "20% - 30% Equity")
            commitment = request.POST.get("commitment", "15-20 hrs/week")
            location = request.POST.get("location", "Remote / Hybrid")
            description = request.POST.get("description", "").strip()
            skills_required = request.POST.get("skills_required", "").strip()

            if startup_name and role_needed:
                founder_user = request.user if request.user.is_authenticated else None
                founder_name = (request.user.get_full_name() or request.user.username) if request.user.is_authenticated else "Founder"

                CoFounderPost.objects.create(
                    startup_name=startup_name,
                    role_needed=role_needed,
                    equity=equity,
                    commitment=commitment,
                    location=location,
                    description=description,
                    skills_text=skills_required,
                    founder_user=founder_user,
                    founder_name=founder_name,
                    badge="NEW POST"
                )
                messages.success(request, f"Co-founder call for {startup_name} is now live!")
                return redirect('co_founders')

    posts = CoFounderPost.objects.all().order_by('-created_at')
    context = {
        "posts": posts,
    }
    return render(request, "collaboration/co_founders.html", context)


def challenges(request):
    """Startup Sprints, Grants, and Hackathons."""
    challenge_list = StartupChallenge.objects.all().order_by('order', 'created_at')
    context = {
        "challenges": challenge_list,
    }
    return render(request, "collaboration/challenges.html", context)


def respond_cofounder_application(request, application_id):
    """Founder accepts or declines a co-founder application."""
    app = get_object_or_404(CoFounderApplication, id=application_id)
    action = request.POST.get('action') or request.GET.get('action', 'accept')

    from accounts.models import create_notification
    if action == 'accept':
        app.status = 'accepted'
        app.save(update_fields=['status'])
        create_notification(
            recipient=app.applicant,
            actor=request.user if request.user.is_authenticated else app.post.founder_user,
            verb=f"accepted your co-founder application for {app.post.startup_name}! Let's team up.",
            notification_type='cofounder_accepted',
            target_url='/collaboration/co-founders/'
        )
        messages.success(request, f"Accepted {app.applicant.get_full_name() or app.applicant.username}'s application!")
    elif action == 'decline':
        app.status = 'declined'
        app.save(update_fields=['status'])
        create_notification(
            recipient=app.applicant,
            actor=request.user if request.user.is_authenticated else app.post.founder_user,
            verb=f"has reviewed your application for {app.post.startup_name}.",
            notification_type='cofounder_declined',
            target_url='/collaboration/co-founders/'
        )
        messages.info(request, "Application declined.")

    return redirect('co_founders')
