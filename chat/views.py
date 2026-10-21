from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Max
from .models import Conversation, Message
from accounts.models import create_notification

def get_current_user(request):
    """Return logged in user, or default to demo user 'preet_builder' for preview."""
    if request.user.is_authenticated:
        return request.user
    demo_user = User.objects.filter(username="preet_builder").first()
    return demo_user or User.objects.first()


def inbox_view(request, conversation_id=None):
    """Main Chat & Messaging inbox showing conversation threads and active chat window."""
    current_user = get_current_user(request)
    if not current_user:
        messages.info(request, "Please log in to access messages.")
        return redirect('login')

    is_demo_mode = not request.user.is_authenticated

    # Fetch user's conversations ordered by latest activity
    user_conversations = (
        Conversation.objects.filter(participants=current_user)
        .prefetch_related('participants', 'messages', 'participants__profile')
        .annotate(latest_message_time=Max('messages__created_at'))
        .order_by('-updated_at')
    )

    conversations_data = []
    for conv in user_conversations:
        other_user = conv.get_other_participant(current_user)
        last_msg = conv.last_message
        unread_count = conv.unread_count_for(current_user)
        other_profile = getattr(other_user, 'profile', None) if other_user else None

        conversations_data.append({
            'conversation': conv,
            'other_user': other_user,
            'other_profile': other_profile,
            'last_message': last_msg,
            'unread_count': unread_count,
        })

    # Determine active conversation
    active_conv = None
    if conversation_id:
        active_conv = get_object_or_404(Conversation, id=conversation_id, participants=current_user)
    elif conversations_data:
        active_conv = conversations_data[0]['conversation']

    active_other = None
    active_other_profile = None
    messages_list = []

    if active_conv:
        # Mark unread incoming messages as read
        active_conv.mark_as_read(current_user)
        active_other = active_conv.get_other_participant(current_user)
        active_other_profile = getattr(active_other, 'profile', None) if active_other else None
        messages_list = active_conv.messages.select_related('sender', 'sender__profile').order_by('created_at')

    # Other members for 'New Chat' modal
    network_members = (
        User.objects.exclude(id=current_user.id)
        .select_related('profile')
        .order_by('first_name', 'username')[:40]
    )

    context = {
        'conversations_data': conversations_data,
        'active_conv': active_conv,
        'active_other': active_other,
        'active_other_profile': active_other_profile,
        'messages_list': messages_list,
        'network_members': network_members,
        'current_user': current_user,
        'is_demo_mode': is_demo_mode,
    }
    return render(request, 'chat/inbox.html', context)


def start_or_get_conversation(request, username):
    """Start or open 1-on-1 direct conversation with the given username."""
    current_user = get_current_user(request)
    if not current_user:
        messages.info(request, "Please log in to send messages.")
        return redirect('login')

    target_user = get_object_or_404(User, username=username)

    if current_user == target_user:
        messages.warning(request, "You cannot message yourself.")
        return redirect('inbox')

    conv, created = Conversation.get_or_create_direct_chat(current_user, target_user)

    if request.method == 'POST':
        initial_content = request.POST.get('message', '').strip()
        if initial_content:
            msg = Message.objects.create(conversation=conv, sender=current_user, content=initial_content)
            conv.save()
            snippet = initial_content[:45] + ('...' if len(initial_content) > 45 else '')
            create_notification(
                recipient=target_user,
                actor=current_user,
                verb=f"sent you a direct message: '{snippet}'",
                notification_type='direct_message',
                target_url=f"/chat/{conv.id}/"
            )
            messages.success(request, f"Message sent to {target_user.get_full_name() or target_user.username}!")

    return redirect('conversation_detail', conversation_id=conv.id)


def send_message_api(request, conversation_id):
    """API endpoint to post a message in a conversation."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required.'}, status=405)

    current_user = get_current_user(request)
    if not current_user:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    conv = get_object_or_404(Conversation, id=conversation_id, participants=current_user)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'success': False, 'error': 'Message content cannot be empty.'}, status=400)

    msg = Message.objects.create(conversation=conv, sender=current_user, content=content)
    conv.save()

    # Dispatch notification to other participant
    other_user = conv.get_other_participant(current_user)
    if other_user:
        snippet = content[:45] + ('...' if len(content) > 45 else '')
        create_notification(
            recipient=other_user,
            actor=current_user,
            verb=f"sent you a direct message: '{snippet}'",
            notification_type='direct_message',
            target_url=f"/chat/{conv.id}/"
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'content': msg.content,
                'sender_id': msg.sender.id,
                'sender_name': msg.sender_name,
                'sender_avatar': msg.sender_avatar,
                'time': msg.formatted_time,
                'date': msg.formatted_date,
                'is_me': True,
            }
        })

    return redirect('conversation_detail', conversation_id=conv.id)


def get_messages_api(request, conversation_id):
    """Polling API endpoint to fetch new messages since after_id."""
    current_user = get_current_user(request)
    if not current_user:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

    conv = get_object_or_404(Conversation, id=conversation_id, participants=current_user)
    after_id = request.GET.get('after_id')

    if after_id and after_id.isdigit():
        new_msgs = conv.messages.filter(id__gt=int(after_id)).select_related('sender', 'sender__profile').order_by('created_at')
    else:
        new_msgs = conv.messages.select_related('sender', 'sender__profile').order_by('created_at')

    # Mark unread incoming messages as read
    new_msgs.exclude(sender=current_user).filter(is_read=False).update(is_read=True)

    messages_data = []
    for m in new_msgs:
        messages_data.append({
            'id': m.id,
            'content': m.content,
            'sender_id': m.sender.id,
            'sender_name': m.sender_name,
            'sender_avatar': m.sender_avatar,
            'time': m.formatted_time,
            'date': m.formatted_date,
            'is_me': (m.sender_id == current_user.id),
        })

    latest_id = messages_data[-1]['id'] if messages_data else (int(after_id) if after_id and after_id.isdigit() else 0)

    return JsonResponse({
        'success': True,
        'messages': messages_data,
        'latest_id': latest_id,
    })


def chat_unread_count_api(request):
    """API endpoint to get total unread messages count for navbar polling."""
    current_user = get_current_user(request)
    if not current_user:
        return JsonResponse({'unread_count': 0})

    total_unread = Message.objects.filter(
        conversation__participants=current_user,
        is_read=False
    ).exclude(sender=current_user).count()

    return JsonResponse({'unread_count': total_unread})
