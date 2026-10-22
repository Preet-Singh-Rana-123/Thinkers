import json
import uuid
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import (
    DiscussionChannel, Thread, ThreadReply, ThreadUpvote,
    MeetingRoom, MeetingParticipant, MeetingSignal, MeetingChatMessage
)
from clubs.models import Club

# Curated discussion mastermind prompts for club meetings
CLUB_MASTERMIND_TOPICS = [
    "What is your single biggest bottleneck to 10x growth this month?",
    "Pitch teardown: How are you positioning against incumbents?",
    "How we acquired our first 100 paying customers without paid ads.",
    "Technical dilemma: Monolith vs Microservices vs Serverless in 2026.",
    "Customer discovery: Share your most brutal customer rejection and the pivot it sparked.",
    "Roast my pricing model: Freemium vs Seat-based vs Usage-based.",
    "Fundraising in 2026: Grants, SAFE notes, or bootstrapping with AI agents?",
    "Founder mental resilience: How do you survive burnout during shipping sprints?",
    "Hiring your first 3 engineers: Equity percentage vs cash splits.",
]

def get_current_founder(request):
    """Return logged in user profile details or realistic fallback."""
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        full_name = request.user.get_full_name() or request.user.username
        role = profile.role if profile and profile.role else "Founder"
        avatar = profile.avatar if profile and profile.avatar else request.user.username[:2].upper()
        color = profile.role_badge if profile and profile.role_badge else "yellow"
        return {
            'user': request.user,
            'name': full_name,
            'username': request.user.username,
            'role': role,
            'avatar': avatar,
            'color': color,
            'is_authenticated': True,
        }
    demo_user = User.objects.filter(username="preet_builder").first() or User.objects.first()
    if demo_user:
        profile = getattr(demo_user, 'profile', None)
        full_name = demo_user.get_full_name() or demo_user.username
        role = profile.role if profile and profile.role else "Founder & Builder"
        avatar = profile.avatar if profile and profile.avatar else demo_user.username[:2].upper()
        color = profile.role_badge if profile and profile.role_badge else "purple"
        return {
            'user': demo_user,
            'name': full_name,
            'username': demo_user.username,
            'role': role,
            'avatar': avatar,
            'color': color,
            'is_authenticated': False,
        }
    return {
        'user': None,
        'name': "Guest Founder",
        'username': "guest_founder",
        'role': "Club Member",
        'avatar': "GF",
        'color': "yellow",
        'is_authenticated': False,
    }


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

    # Active live rooms to highlight at the top of forum
    live_rooms = MeetingRoom.objects.filter(is_active=True).select_related('club', 'host')[:4]

    context = {
        "channels": channels,
        "threads": threads,
        "current_channel": channel_filter,
        "live_rooms": live_rooms,
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

    # Check if there is an active meeting linked to this thread
    thread_meeting = MeetingRoom.objects.filter(thread=thread).first()

    context = {
        "thread": thread,
        "thread_meeting": thread_meeting,
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


# ==============================================================================
# LIVE DISCUSSION MEETINGS & CLUB ACTIVITIES
# ==============================================================================

def meeting_directory(request):
    """Directory of all active and upcoming founder discussion rooms and club meetings."""
    meeting_type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('q', '').strip()

    rooms = MeetingRoom.objects.select_related('club', 'host').filter(is_active=True)

    if meeting_type_filter != 'all':
        rooms = rooms.filter(meeting_type=meeting_type_filter)

    if search_query:
        rooms = rooms.filter(title__icontains=search_query)

    # Handle quick room creation
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        meeting_type = request.POST.get("meeting_type", "open_discussion")
        description = request.POST.get("description", "").strip()
        club_id = request.POST.get("club_id", "").strip()

        if title:
            founder = get_current_founder(request)
            club_obj = Club.objects.filter(id=club_id).first() if club_id else None
            base_slug = slugify(title) or "meeting"
            room_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            color_map = {
                'club_mastermind': 'purple',
                'pitch_roast': 'pink',
                'open_discussion': 'cyan',
                'brainstorm': 'yellow',
            }

            room = MeetingRoom.objects.create(
                title=title,
                slug=room_slug,
                description=description or f"Live meeting hosted by {founder['name']}",
                meeting_type=meeting_type,
                club=club_obj,
                host=founder['user'],
                host_name=founder['name'],
                badge_color=color_map.get(meeting_type, 'yellow'),
                is_active=True,
                current_activity='pitch_timer' if meeting_type == 'pitch_roast' else 'discussion',
                activity_state={
                    'pitch_timer': {'running': False, 'time_left': 60, 'total': 60, 'speaker': founder['name']},
                    'current_topic': CLUB_MASTERMIND_TOPICS[0],
                    'notes': f"Mastermind session for '{title}'. Notes taken live will sync here.",
                    'pitch_votes': []
                }
            )
            messages.success(request, f"Live Room '{room.title}' launched! Opening stage...")
            return redirect('join_meeting_room', room_slug=room.slug)

    clubs = Club.objects.all().order_by('name')

    context = {
        "rooms": rooms,
        "clubs": clubs,
        "current_type": meeting_type_filter,
        "search_query": search_query,
    }
    return render(request, "discussions/meeting_directory.html", context)


def join_meeting_room(request, room_slug):
    """
    Live Audio/Video Meeting Room stage with WebRTC, camera & microphone access,
    in-meeting chat, pitch timers, collaborative notes, and club activities.
    """
    founder = get_current_founder(request)

    # Try finding existing meeting room
    room = MeetingRoom.objects.select_related('club', 'host', 'thread').filter(slug=room_slug).first()

    # If not found by slug, check if room_slug matches a Club slug
    if not room:
        club = Club.objects.filter(slug=room_slug).first()
        if club:
            room = MeetingRoom.objects.filter(club=club, is_active=True).first()
            if not room:
                room = MeetingRoom.objects.create(
                    title=f"{club.name}: Live Mastermind Stage",
                    slug=club.slug,
                    description=club.tagline or f"Official live video stage and mastermind hub for {club.name}.",
                    meeting_type='club_mastermind',
                    club=club,
                    host=club.founder or founder['user'],
                    host_name=club.lead or founder['name'],
                    badge_color=club.badge_color or 'purple',
                    is_active=True,
                    activity_state={
                        'pitch_timer': {'running': False, 'time_left': 60, 'total': 60, 'speaker': 'Club Pitcher'},
                        'current_topic': CLUB_MASTERMIND_TOPICS[0],
                        'notes': f"Welcome to {club.name} weekly mastermind! Drop pitch ideas, questions, and action items here.",
                        'pitch_votes': []
                    }
                )

    # If still not found, check if it's a thread id
    if not room and room_slug.startswith('thread-'):
        try:
            thread_id = int(room_slug.split('-')[1])
            thread = Thread.objects.filter(id=thread_id).first()
            if thread:
                room = MeetingRoom.objects.create(
                    title=f"Live Voice Discussion: {thread.title[:60]}",
                    slug=room_slug,
                    description=f"Live voice and video discussion for mastermind thread #{thread.id}",
                    meeting_type='open_discussion',
                    thread=thread,
                    club=thread.club,
                    host=thread.author_user or founder['user'],
                    host_name=thread.author,
                    badge_color='cyan',
                    is_active=True,
                    activity_state={
                        'pitch_timer': {'running': False, 'time_left': 60, 'total': 60, 'speaker': 'Speaker'},
                        'current_topic': thread.title,
                        'notes': f"Discussion notes on thread: {thread.title}\n\nKey points:",
                        'pitch_votes': []
                    }
                )
        except (ValueError, IndexError):
            pass

    # Fallback: create ad-hoc room
    if not room:
        room = MeetingRoom.objects.create(
            title=f"Founder Mastermind: {room_slug.replace('-', ' ').title()}",
            slug=room_slug,
            description="Live peer discussion room with camera, microphone, screen sharing, and club tools.",
            meeting_type='open_discussion',
            host=founder['user'],
            host_name=founder['name'],
            badge_color='yellow',
            is_active=True,
            activity_state={
                'pitch_timer': {'running': False, 'time_left': 60, 'total': 60, 'speaker': 'Founder'},
                'current_topic': CLUB_MASTERMIND_TOPICS[0],
                'notes': "Welcome to the mastermind! Notes taken here sync across all participants.",
                'pitch_votes': []
            }
        )

    # Initial chat messages
    messages_list = room.messages.select_related('sender_user').order_by('created_at')[:50]

    # STUN configuration for WebRTC
    ice_servers = [
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
    ]

    is_host = bool(
        (room.host and request.user.is_authenticated and room.host == request.user) or
        (request.user.is_authenticated and request.user.is_staff) or
        (room.host_name and founder['name'] == room.host_name)
    )

    context = {
        "room": room,
        "founder": founder,
        "is_host": is_host,
        "messages_list": messages_list,
        "ice_servers_json": json.dumps(ice_servers),
        "activity_state_json": json.dumps(room.activity_state or {}),
        "club_topics_json": json.dumps(CLUB_MASTERMIND_TOPICS),
    }
    return render(request, "discussions/meeting_room.html", context)


# ------------------------------------------------------------------------------
# REAL-TIME MEETING APIS (Heartbeat, WebRTC Signals, In-Room Chat, Activities)
# ------------------------------------------------------------------------------

@csrf_exempt
def meeting_heartbeat_api(request, room_slug):
    """
    Heartbeat endpoint: Registers/updates participant state, cleans up stale
    participants, and returns the current participant list and activity state.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    room = get_object_or_404(MeetingRoom, slug=room_slug)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    session_id = data.get("session_id", "").strip()
    if not session_id:
        return JsonResponse({"error": "session_id required"}, status=400)

    founder = get_current_founder(request)
    display_name = data.get("display_name", "").strip() or founder['name']
    role = data.get("role", "").strip() or founder['role']
    avatar = data.get("avatar", "").strip() or founder['avatar']
    color = data.get("color", "").strip() or founder['color']
    has_video = bool(data.get("has_video", True))
    has_audio = bool(data.get("has_audio", True))
    is_screen_sharing = bool(data.get("is_screen_sharing", False))
    hand_raised = bool(data.get("hand_raised", False))

    now = timezone.now()
    cutoff = now - datetime.timedelta(seconds=25)

    # Upsert current participant
    participant, _ = MeetingParticipant.objects.update_or_create(
        room=room,
        session_id=session_id,
        defaults={
            'user': founder['user'],
            'display_name': display_name,
            'role': role,
            'avatar': avatar,
            'color': color,
            'has_video': has_video,
            'has_audio': has_audio,
            'is_screen_sharing': is_screen_sharing,
            'hand_raised': hand_raised,
            'is_active': True,
            'last_seen': now,
        }
    )

    # Mark inactive stale participants
    room.participants.filter(last_seen__lt=cutoff).update(is_active=False)

    # Fetch active participants
    active_qs = room.participants.filter(is_active=True, last_seen__gte=cutoff)
    participants_list = []
    for p in active_qs:
        participants_list.append({
            'session_id': p.session_id,
            'display_name': p.display_name,
            'role': p.role,
            'avatar': p.avatar,
            'color': p.color,
            'has_video': p.has_video,
            'has_audio': p.has_audio,
            'is_screen_sharing': p.is_screen_sharing,
            'hand_raised': p.hand_raised,
            'is_self': (p.session_id == session_id),
        })

    # Periodically clean old signals older than 5 minutes to keep DB slim
    MeetingSignal.objects.filter(room=room, created_at__lt=now - datetime.timedelta(minutes=5)).delete()

    return JsonResponse({
        "success": True,
        "room_title": room.title,
        "meeting_type": room.meeting_type,
        "participants": participants_list,
        "current_activity": room.current_activity,
        "activity_state": room.activity_state or {},
    })


@csrf_exempt
def meeting_signal_send_api(request, room_slug):
    """WebRTC signaling endpoint: Dispatches SDP offers, answers, ICE candidates, or reactions."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    room = get_object_or_404(MeetingRoom, slug=room_slug)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    from_session = data.get("from_session", "").strip()
    to_session = data.get("to_session", "all").strip()
    signal_type = data.get("signal_type", "").strip()
    payload = data.get("payload", {})

    if not from_session or not signal_type:
        return JsonResponse({"error": "Missing from_session or signal_type"}, status=400)

    signal = MeetingSignal.objects.create(
        room=room,
        from_session=from_session,
        to_session=to_session,
        signal_type=signal_type,
        payload=payload
    )

    return JsonResponse({"success": True, "signal_id": signal.id})


def meeting_signal_poll_api(request, room_slug):
    """WebRTC signaling poll endpoint: Retrieves incoming signals for a given session."""
    room = get_object_or_404(MeetingRoom, slug=room_slug)
    session_id = request.GET.get("session_id", "").strip()
    last_id = int(request.GET.get("last_id", 0) or 0)

    if not session_id:
        return JsonResponse({"error": "session_id required"}, status=400)

    # Fetch signals targeted to this session or broadcast to 'all', excluding signals from self
    signals_qs = (
        MeetingSignal.objects.filter(room=room, id__gt=last_id)
        .exclude(from_session=session_id)
        .filter(to_session__in=[session_id, 'all', 'broadcast'])
        .order_by('id')[:40]
    )

    signals_data = []
    max_id = last_id
    for s in signals_qs:
        signals_data.append({
            'id': s.id,
            'from_session': s.from_session,
            'to_session': s.to_session,
            'signal_type': s.signal_type,
            'payload': s.payload,
            'timestamp': s.created_at.strftime("%H:%M:%S"),
        })
        if s.id > max_id:
            max_id = s.id

    return JsonResponse({
        "success": True,
        "signals": signals_data,
        "last_id": max_id,
    })


@csrf_exempt
def meeting_chat_api(request, room_slug):
    """In-Meeting Chat: Send and retrieve room chat messages in real time."""
    room = get_object_or_404(MeetingRoom, slug=room_slug)

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST

        session_id = data.get("session_id", "").strip()
        sender_name = data.get("sender_name", "").strip()
        sender_avatar = data.get("sender_avatar", "TH").strip()
        sender_color = data.get("sender_color", "yellow").strip()
        message_text = data.get("message", "").strip()
        message_type = data.get("message_type", "chat").strip()

        if not message_text:
            return JsonResponse({"error": "Empty message"}, status=400)

        founder = get_current_founder(request)

        msg = MeetingChatMessage.objects.create(
            room=room,
            sender_session=session_id or "anon",
            sender_name=sender_name or founder['name'],
            sender_avatar=sender_avatar or founder['avatar'],
            sender_color=sender_color or founder['color'],
            sender_user=founder['user'],
            message=message_text,
            message_type=message_type
        )

        return JsonResponse({
            "success": True,
            "message": {
                'id': msg.id,
                'sender_name': msg.sender_name,
                'sender_avatar': msg.sender_avatar,
                'sender_color': msg.sender_color,
                'message': msg.message,
                'message_type': msg.message_type,
                'time': msg.created_at.strftime("%I:%M %p"),
                'is_self': True,
            }
        })

    # GET: fetch messages since last_id
    last_id = int(request.GET.get("last_id", 0) or 0)
    current_session = request.GET.get("session_id", "").strip()

    messages_qs = room.messages.filter(id__gt=last_id).order_by('id')[:60]
    result = []
    max_id = last_id

    for m in messages_qs:
        result.append({
            'id': m.id,
            'sender_name': m.sender_name,
            'sender_avatar': m.sender_avatar,
            'sender_color': m.sender_color,
            'message': m.message,
            'message_type': m.message_type,
            'time': m.created_at.strftime("%I:%M %p"),
            'is_self': (current_session and m.sender_session == current_session),
        })
        if m.id > max_id:
            max_id = m.id

    return JsonResponse({
        "success": True,
        "messages": result,
        "last_id": max_id,
    })


@csrf_exempt
def meeting_activity_api(request, room_slug):
    """
    Handle live club activities inside meeting room:
    - Pitch countdown timer (start, pause, reset)
    - Pitch feedback and upvoting
    - Discussion topic / icebreaker spinner
    - Collaborative live notes
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    room = get_object_or_404(MeetingRoom, slug=room_slug)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    action = data.get("action", "").strip()
    activity_state = dict(room.activity_state or {})

    if action == "start_timer":
        duration = int(data.get("duration", 60))
        speaker = data.get("speaker", "Founder").strip()
        activity_state['pitch_timer'] = {
            'running': True,
            'time_left': duration,
            'total': duration,
            'speaker': speaker,
            'started_at': timezone.now().isoformat(),
        }
        room.current_activity = 'pitch_timer'

        # Broadcast chat system notice
        MeetingChatMessage.objects.create(
            room=room,
            sender_session="system",
            sender_name="Stage Timer",
            sender_avatar="⏱️",
            sender_color="pink",
            message=f"🚀 60-second pitch timer started for {speaker}! Floor is theirs.",
            message_type="system"
        )

    elif action == "stop_timer":
        if 'pitch_timer' in activity_state:
            activity_state['pitch_timer']['running'] = False

    elif action == "reset_timer":
        duration = int(data.get("duration", 60))
        speaker = data.get("speaker", "Founder").strip()
        activity_state['pitch_timer'] = {
            'running': False,
            'time_left': duration,
            'total': duration,
            'speaker': speaker,
        }

    elif action == "next_topic":
        import random
        current_topic = activity_state.get('current_topic', '')
        available = [t for t in CLUB_MASTERMIND_TOPICS if t != current_topic]
        chosen = random.choice(available if available else CLUB_MASTERMIND_TOPICS)
        activity_state['current_topic'] = chosen
        room.current_activity = 'icebreaker'

        MeetingChatMessage.objects.create(
            room=room,
            sender_session="system",
            sender_name="Mastermind Host",
            sender_avatar="💡",
            sender_color="yellow",
            message=f"🎲 New Mastermind Topic: \"{chosen}\"",
            message_type="system"
        )

    elif action == "vote_pitch":
        score = int(data.get("score", 5))
        tags = data.get("tags", [])
        voter_name = data.get("voter_name", "Peer Founder").strip()
        feedback = data.get("feedback", "").strip()

        pitch_votes = activity_state.get('pitch_votes', [])
        vote_entry = {
            'voter': voter_name,
            'score': score,
            'tags': tags,
            'feedback': feedback,
            'time': timezone.now().strftime("%I:%M %p"),
        }
        pitch_votes.append(vote_entry)
        activity_state['pitch_votes'] = pitch_votes[-20:]  # keep recent 20

        # Broadcast announcement in chat
        tags_str = f" [{', '.join(tags)}]" if tags else ""
        feedback_str = f" - \"{feedback}\"" if feedback else ""
        MeetingChatMessage.objects.create(
            room=room,
            sender_session="system",
            sender_name="Pitch Roast Bot",
            sender_avatar="🔥",
            sender_color="pink",
            message=f"⭐ {voter_name} rated pitch {score}/5 stars!{tags_str}{feedback_str}",
            message_type="pitch_vote"
        )

    elif action == "save_notes":
        notes_content = data.get("notes", "").strip()
        activity_state['notes'] = notes_content

    elif action == "switch_activity":
        new_activity = data.get("activity", "discussion").strip()
        room.current_activity = new_activity

    room.activity_state = activity_state
    room.save(update_fields=['activity_state', 'current_activity', 'updated_at'])

    return JsonResponse({
        "success": True,
        "current_activity": room.current_activity,
        "activity_state": room.activity_state,
    })


@csrf_exempt
def meeting_demo_peers_api(request, room_slug):
    """
    Toggle simulated peer founders (e.g. Aarav Sharma, Sneha Patel) to join the room.
    Enables realistic multi-user club masterminds, pitch roasts, and video stage testing
    even when testing solo in one browser tab!
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    room = get_object_or_404(MeetingRoom, slug=room_slug)
    now = timezone.now()

    demo_peers = [
        {
            'session_id': f'demo-peer-aarav-{room.id}',
            'name': 'Aarav Sharma',
            'role': 'Club Host & AI Architect',
            'avatar': 'AS',
            'color': 'purple',
            'welcome': 'Hey everyone! Welcome to today\'s live club mastermind. Excited to roast some pitches today!',
        },
        {
            'session_id': f'demo-peer-sneha-{room.id}',
            'name': 'Sneha Patel',
            'role': 'DeepTech & Hardware Lead',
            'avatar': 'SP',
            'color': 'cyan',
            'welcome': 'Mic and camera working crisp. Ready for the live session!',
        },
    ]

    # Check if demo peers already exist and are active
    existing_demo = room.participants.filter(session_id__startswith='demo-peer-', is_active=True).first()

    if existing_demo:
        # Toggle OFF: Deactivate demo peers
        room.participants.filter(session_id__startswith='demo-peer-').update(is_active=False)
        MeetingChatMessage.objects.create(
            room=room,
            sender_session="system",
            sender_name="Stage Manager",
            sender_avatar="👋",
            sender_color="yellow",
            message="Simulated peer founders stepped off the stage.",
            message_type="system"
        )
        return JsonResponse({"success": True, "active": False, "message": "Demo peers removed from stage"})

    # Toggle ON: Activate demo peers
    for dp in demo_peers:
        MeetingParticipant.objects.update_or_create(
            room=room,
            session_id=dp['session_id'],
            defaults={
                'display_name': dp['name'],
                'role': dp['role'],
                'avatar': dp['avatar'],
                'color': dp['color'],
                'has_video': True,
                'has_audio': True,
                'is_screen_sharing': False,
                'hand_raised': False,
                'is_active': True,
                'last_seen': now,
            }
        )
        # Drop greeting message
        MeetingChatMessage.objects.create(
            room=room,
            sender_session=dp['session_id'],
            sender_name=dp['name'],
            sender_avatar=dp['avatar'],
            sender_color=dp['color'],
            message=dp['welcome'],
            message_type="chat"
        )

    return JsonResponse({
        "success": True,
        "active": True,
        "message": "Demo club co-founders joined the live stage!"
    })


@csrf_exempt
def meeting_leave_api(request, room_slug):
    """Leave meeting room cleanly: Updates participant status and dispatches leave signal."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    room = get_object_or_404(MeetingRoom, slug=room_slug)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    session_id = data.get("session_id", "").strip()
    if session_id:
        room.participants.filter(session_id=session_id).update(is_active=False)
        MeetingSignal.objects.create(
            room=room,
            from_session=session_id,
            to_session="all",
            signal_type="peer_left",
            payload={"session_id": session_id}
        )

    return JsonResponse({"success": True})

