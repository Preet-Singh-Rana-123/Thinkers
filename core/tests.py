from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from clubs.models import Club, ClubMembership
from collaboration.models import Pitch, CoFounderPost
from discussions.models import DiscussionChannel, Thread

class ThinkersPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username="testfounder",
            password="testpassword123",
            first_name="Test",
            last_name="Founder"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role="Technical Founder",
            role_badge="yellow",
            college="Test Engineering College",
            skills_text="Python, Django, React"
        )

        # Create test club
        self.club = Club.objects.create(
            name="Quantum Computing Lab",
            category="ai",
            category_label="AI & DeepTech",
            tagline="Building quantum circuits",
            description="A club for quantum researchers.",
            lead="Test Lead"
        )

        # Create test pitch
        self.pitch = Pitch.objects.create(
            title="QuantumFlow",
            one_liner="Visual quantum circuit designer",
            founder_user=self.user,
            seeking="Co-founder",
            upvotes=5
        )

        # Create test channel and thread
        self.channel = DiscussionChannel.objects.create(
            name="Test Roasts",
            slug="roasts"
        )
        self.thread = Thread.objects.create(
            channel=self.channel,
            title="How to price quantum software?",
            content="Looking for feedback on student pricing.",
            author_user=self.user,
            upvotes=10
        )

    def test_core_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quantum Computing Lab")

    def test_club_list_and_detail(self):
        response = self.client.get(reverse('club_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quantum Computing Lab")

        response = self.client.get(reverse('club_detail', kwargs={'club_slug': self.club.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Building quantum circuits")

    def test_club_create(self):
        self.client.login(username="testfounder", password="testpassword123")
        response = self.client.post(reverse('club_create'), {
            'name': 'Robotics Mavericks',
            'category': 'ai',
            'tagline': 'Building autonomous mobile robots',
            'description': 'Hardware and software club.',
            'university': 'Test Campus',
            'frequency': 'Every Friday',
            'color_theme': 'cyan',
            'tags': 'Robotics, ROS, C++'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Club.objects.filter(name='Robotics Mavericks').exists())

    def test_club_join(self):
        self.client.login(username="testfounder", password="testpassword123")
        response = self.client.get(reverse('club_join', kwargs={'club_slug': self.club.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ClubMembership.objects.filter(club=self.club, user=self.user).exists())

    def test_pitch_wall_and_submission(self):
        self.client.login(username="testfounder", password="testpassword123")
        response = self.client.post(reverse('pitch_wall'), {
            'title': 'AutonomousDrone',
            'one_liner': 'Campus drone delivery',
            'category': 'Developer Tools',
            'stage': 'Live Beta',
            'seeking': 'Hardware engineer'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Pitch.objects.filter(title='AutonomousDrone').exists())

    def test_pitch_upvote(self):
        initial_votes = self.pitch.upvotes
        response = self.client.get(reverse('upvote_pitch', kwargs={'pitch_id': self.pitch.id}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.pitch.refresh_from_db()
        self.assertEqual(self.pitch.upvotes, initial_votes + 1)

    def test_discussions_forum_and_reply(self):
        # Create reply
        response = self.client.post(reverse('thread_detail', kwargs={'thread_id': self.thread.id}), {
            'content': 'Charge per simulation compute minute!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.thread.replies.count(), 1)

    def test_user_authentication_flow(self):
        # Logout
        self.client.logout()

        # Login
        response = self.client.post(reverse('login'), {
            'username': 'testfounder',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)

        # Profile
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Founder")

    def test_coffee_chat_send_and_accept_notifications(self):
        # Create second user
        user2 = User.objects.create_user(username="founder2", password="password123", first_name="Founder", last_name="Two")
        UserProfile.objects.create(user=user2, role="Designer")

        # User 1 logs in and invites User 2
        self.client.login(username="testfounder", password="testpassword123")
        response = self.client.post(reverse('member_profile', kwargs={'username': user2.username}), {
            'focus': 'Discuss Co-Founding Opportunity',
            'note': 'Let us collaborate on QuantumFlow!'
        })
        self.assertEqual(response.status_code, 302)

        # Check notification created for user2
        from accounts.models import Notification, CoffeeChatRequest
        self.assertTrue(Notification.objects.filter(recipient=user2, notification_type='coffee_chat_request').exists())
        chat_req = CoffeeChatRequest.objects.filter(from_user=self.user, to_user=user2).first()
        self.assertIsNotNone(chat_req)

        # User 2 logs in and accepts the coffee chat
        self.client.login(username="founder2", password="password123")
        response = self.client.get(reverse('respond_coffee_chat', kwargs={'request_id': chat_req.id}) + '?action=accept')
        self.assertEqual(response.status_code, 302)

        # Check coffee chat status updated to accepted
        chat_req.refresh_from_db()
        self.assertEqual(chat_req.status, 'accepted')

        # Check notification created for User 1
        self.assertTrue(Notification.objects.filter(recipient=self.user, notification_type='coffee_chat_accepted').exists())

    def test_mark_notifications_read(self):
        from accounts.models import Notification
        Notification.objects.create(recipient=self.user, verb="sent you a test alert", is_read=False)
        self.client.login(username="testfounder", password="testpassword123")

        response = self.client.get(reverse('mark_notifications_read'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)

    def test_navbar_notification_bell_and_badge(self):
        # Guest user receives navbar with notification bell and count badge
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="notificationToggleBtn"')
        self.assertContains(response, 'id="notificationDropdownMenu"')

        # Authenticated user with unread notification
        from accounts.models import Notification
        Notification.objects.create(recipient=self.user, verb="applied for your startup", is_read=False)
        self.client.login(username="testfounder", password="testpassword123")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="notificationToggleBtn"')
        self.assertContains(response, 'notification-count-badge')

    def test_open_notification_redirects_and_marks_read(self):
        from accounts.models import Notification
        notif = Notification.objects.create(
            recipient=self.user,
            verb="applied for Co-Founder role",
            target_url="/collaboration/co-founders/",
            is_read=False
        )
        self.client.login(username="testfounder", password="testpassword123")

        response = self.client.get(reverse('open_notification', kwargs={'notification_id': notif.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/collaboration/co-founders/")

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
