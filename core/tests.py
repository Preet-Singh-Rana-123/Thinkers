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
