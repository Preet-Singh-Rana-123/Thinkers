from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from accounts.models import UserProfile, CoffeeChatRequest
from .models import SpeedNetworkingSession, SpeedNetworkingQueue

def members_list(request):
    """Explore all entrepreneurs in the network with role filtering from DB."""
    role = request.GET.get('role', 'all')
    search_q = request.GET.get('q', '').strip()

    members = UserProfile.objects.select_related('user').all().order_by('-id')

    if role != 'all':
        members = members.filter(role__icontains=role)

    if search_q:
        members = members.filter(
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q) |
            Q(user__username__icontains=search_q) |
            Q(college__icontains=search_q) |
            Q(skills_text__icontains=search_q) |
            Q(headline__icontains=search_q)
        )

    context = {
        "members": members,
        "current_role": role,
        "search_q": search_q,
    }
    return render(request, "networking/members_list.html", context)


def member_profile(request, username):
    """Detailed Entrepreneur Trading Card & Bio from DB."""
    member = get_object_or_404(UserProfile, user__username=username)

    if request.method == "POST":
        focus = request.POST.get("focus", "Discuss Co-Founding Opportunity")
        note = request.POST.get("note", "").strip()
        if request.user.is_authenticated:
            CoffeeChatRequest.objects.create(
                from_user=request.user,
                to_user=member.user,
                focus=focus,
                topic=note or f"Coffee chat requested by {request.user.get_full_name() or request.user.username}",
                status="pending"
            )
            messages.success(request, f"Coffee chat invite dispatched to {member.name}!")
        else:
            messages.success(request, f"Coffee chat invite dispatched to {member.name} (demo mode)!")
        return redirect('member_profile', username=username)

    context = {
        "member": member,
    }
    return render(request, "networking/member_profile.html", context)


def speed_networking(request):
    """Virtual Speed Networking Lounge with live countdown, queue, and instant match simulator."""
    session = SpeedNetworkingSession.objects.filter(is_active=True).first()
    active_queue = session.active_queue_count if session else 42
    next_session = session.scheduled_time if session else "Thursday, 7:00 PM IST"
    sample_attendees = UserProfile.objects.select_related('user').all()[:4]

    context = {
        "active_queue_count": active_queue,
        "next_session": next_session,
        "sample_attendees": sample_attendees,
    }
    return render(request, "networking/speed_networking.html", context)
