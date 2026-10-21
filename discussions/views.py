from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import DiscussionChannel, Thread, ThreadReply, ThreadUpvote
from clubs.models import Club

def forum_list(request):
    """Explore discussion boards, AMAs, and club mastermind threads from DB."""
    channels = DiscussionChannel.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        channel_slug = request.POST.get("channel", "roasts")
        content = request.POST.get("content", "").strip()
        club_name = request.POST.get("club", "General Community").strip()

        if title and content:
            channel = DiscussionChannel.objects.filter(slug=channel_slug).first() or channels.first()
            author_user = request.user if request.user.is_authenticated else None
            author_name = (request.user.get_full_name() or request.user.username) if request.user.is_authenticated else "Founder"
            author_role = "Founder"
            author_avatar = "TH"
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                author_role = request.user.profile.role
                author_avatar = request.user.profile.avatar or request.user.username[:2].upper()

            club_obj = Club.objects.filter(name__icontains=club_name).first()

            thread = Thread.objects.create(
                channel=channel,
                title=title,
                content=content,
                author_user=author_user,
                author_name=author_name,
                author_role=author_role,
                author_avatar=author_avatar,
                club=club_obj,
                club_name_fallback=club_name,
                upvotes=1
            )
            messages.success(request, f"Your mastermind thread has been started!")
            return redirect('thread_detail', thread_id=thread.id)

    channel_filter = request.GET.get('channel', 'all')
    threads = Thread.objects.select_related('channel', 'club', 'author_user').all()

    if channel_filter != 'all':
        threads = threads.filter(channel__slug__icontains=channel_filter)

    context = {
        "channels": channels,
        "threads": threads,
        "current_channel": channel_filter,
    }
    return render(request, "discussions/forum_list.html", context)


def thread_detail(request, thread_id):
    """Single discussion thread with comic speech dialogue between founders."""
    thread = get_object_or_404(Thread, id=thread_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            author_user = request.user if request.user.is_authenticated else None
            author_name = (request.user.get_full_name() or request.user.username) if request.user.is_authenticated else "Peer Founder"
            author_role = "Active Member"
            author_avatar = "TH"
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                author_role = request.user.profile.role
                author_avatar = request.user.profile.avatar or request.user.username[:2].upper()

            ThreadReply.objects.create(
                thread=thread,
                author_user=author_user,
                author_name=author_name,
                author_role=author_role,
                author_avatar=author_avatar,
                content=content,
                upvotes=0
            )
            if thread.author_user and thread.author_user != request.user:
                from accounts.models import create_notification
                create_notification(
                    recipient=thread.author_user,
                    actor=request.user if request.user.is_authenticated else None,
                    actor_name_fallback=author_name,
                    verb=f"replied to your mastermind thread: '{thread.title[:40]}...'",
                    notification_type='thread_reply',
                    target_url=f"/community/thread/{thread.id}/"
                )
            messages.success(request, "Your reply has been posted to the discussion!")
            return redirect('thread_detail', thread_id=thread.id)

    context = {
        "thread": thread,
    }
    return render(request, "discussions/thread_detail.html", context)


def upvote_thread(request, thread_id):
    """AJAX or redirect endpoint to upvote a discussion thread."""
    thread = get_object_or_404(Thread, id=thread_id)
    thread.upvotes += 1
    thread.save(update_fields=['upvotes'])

    if request.user.is_authenticated:
        ThreadUpvote.objects.get_or_create(thread=thread, user=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({"success": True, "upvotes": thread.upvotes})

    messages.success(request, "Upvoted discussion thread!")
    return redirect('thread_detail', thread_id=thread.id)
