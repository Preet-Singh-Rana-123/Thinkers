from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile, Notification
from .models import Conversation, Message

class ChatSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="preet_test",
            email="preet@test.com",
            password="password123",
            first_name="Preet",
            last_name="Rana"
        )
        UserProfile.objects.create(
            user=self.user1,
            role="Full-Stack Founder",
            avatar="PR",
            college="Engineering College"
        )

        self.user2 = User.objects.create_user(
            username="aarav_test",
            email="aarav@test.com",
            password="password123",
            first_name="Aarav",
            last_name="Sharma"
        )
        UserProfile.objects.create(
            user=self.user2,
            role="Technical Hacker",
            avatar="AS",
            college="Tech Institute"
        )

    def test_conversation_creation_and_helper_methods(self):
        """Test creating 1-on-1 direct conversation and helper functions."""
        conv, created = Conversation.get_or_create_direct_chat(self.user1, self.user2)
        self.assertTrue(created)
        self.assertEqual(conv.participants.count(), 2)
        self.assertEqual(conv.get_other_participant(self.user1), self.user2)
        self.assertEqual(conv.get_other_participant(self.user2), self.user1)

        # Call again: should return same conversation
        conv2, created2 = Conversation.get_or_create_direct_chat(self.user1, self.user2)
        self.assertFalse(created2)
        self.assertEqual(conv.id, conv2.id)

    def test_messages_and_unread_counts(self):
        """Test message sending, ordering, and unread counts."""
        conv, _ = Conversation.get_or_create_direct_chat(self.user1, self.user2)
        
        m1 = Message.objects.create(conversation=conv, sender=self.user1, content="Hello Aarav!", is_read=False)
        m2 = Message.objects.create(conversation=conv, sender=self.user2, content="Hey Preet! Great to connect.", is_read=False)

        self.assertEqual(conv.last_message.id, m2.id)

        # Unread for user1 should be 1 (m2 from user2)
        self.assertEqual(conv.unread_count_for(self.user1), 1)
        # Unread for user2 should be 1 (m1 from user1)
        self.assertEqual(conv.unread_count_for(self.user2), 1)

        # Mark read for user1
        conv.mark_as_read(self.user1)
        self.assertEqual(conv.unread_count_for(self.user1), 0)
        # user2 still has 1 unread
        self.assertEqual(conv.unread_count_for(self.user2), 1)

    def test_inbox_view(self):
        """Test rendering the inbox page."""
        self.client.login(username="preet_test", password="password123")
        conv, _ = Conversation.get_or_create_direct_chat(self.user1, self.user2)
        Message.objects.create(conversation=conv, sender=self.user2, content="Hey check out this pitch!", is_read=False)

        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aarav Sharma")
        self.assertContains(response, "Hey check out this pitch!")

    def test_start_chat_with_message(self):
        """Test starting a conversation via POST to start_chat."""
        self.client.login(username="preet_test", password="password123")
        response = self.client.post(
            reverse('start_chat', kwargs={'username': self.user2.username}),
            {'message': 'Hey Aarav, loved your pitch! Let us sync.'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Verify conversation and message exists
        conv = Conversation.objects.filter(participants=self.user1).filter(participants=self.user2).first()
        self.assertIsNotNone(conv)
        self.assertEqual(conv.messages.count(), 1)
        self.assertIn("loved your pitch", conv.messages.first().content)

        # Verify Notification dispatched to recipient (user2)
        notif = Notification.objects.filter(recipient=self.user2, notification_type='direct_message').first()
        self.assertIsNotNone(notif)
        self.assertIn("sent you a direct message", notif.verb)

    def test_send_message_api_ajax(self):
        """Test AJAX sending message via API endpoint."""
        self.client.login(username="preet_test", password="password123")
        conv, _ = Conversation.get_or_create_direct_chat(self.user1, self.user2)

        response = self.client.post(
            reverse('send_message_api', kwargs={'conversation_id': conv.id}),
            {'content': 'Testing real-time message delivery.'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message']['content'], 'Testing real-time message delivery.')
        self.assertTrue(data['message']['is_me'])

    def test_get_messages_api_polling(self):
        """Test live polling API endpoint for new messages."""
        self.client.login(username="preet_test", password="password123")
        conv, _ = Conversation.get_or_create_direct_chat(self.user1, self.user2)
        m1 = Message.objects.create(conversation=conv, sender=self.user2, content="First note", is_read=False)
        m2 = Message.objects.create(conversation=conv, sender=self.user2, content="Second note", is_read=False)

        # Poll after m1
        response = self.client.get(
            reverse('get_messages_api', kwargs={'conversation_id': conv.id}) + f'?after_id={m1.id}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['content'], 'Second note')

    def test_chat_unread_count_api(self):
        """Test API endpoint returning unread count."""
        self.client.login(username="preet_test", password="password123")
        conv, _ = Conversation.get_or_create_direct_chat(self.user1, self.user2)
        Message.objects.create(conversation=conv, sender=self.user2, content="Unread 1", is_read=False)
        Message.objects.create(conversation=conv, sender=self.user2, content="Unread 2", is_read=False)

        response = self.client.get(reverse('chat_unread_count_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['unread_count'], 2)
