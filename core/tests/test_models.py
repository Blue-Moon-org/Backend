from django.contrib.auth import get_user_model
from core.models import Feedback
from .setup import BaseTestCase

User = get_user_model()


class UserModelTest(BaseTestCase):

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, "user")
        self.assertEqual(self.user.email, "user@example.com")
        self.assertEqual(self.user.phone, "1234567890")
        self.assertTrue(self.user.check_password("password"))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_banned)
        self.assertFalse(self.user.is_verified)
        self.assertTrue(self.user.is_active)

    def test_user_fullname_property(self):
        self.user.firstname = "John"
        self.user.lastname = "Doe"
        self.assertEqual(self.user.fullname, "John Doe")

    def test_user_followers_count(self):
        follower = User.objects.create_user(
            username="follower",
            email="follower@example.com",
            phone="9876543210",
            password="followerpassword",
        )
        self.user.followers.add(follower)
        self.assertEqual(self.user.followers_count, 1)

    def test_user_following_count(self):
        following = User.objects.create_user(
            username="following",
            email="following@example.com",
            phone="5678901234",
            password="followingpassword",
        )
        self.user.following.add(following)
        self.assertEqual(self.user.following_count, 1)


class FeedbackModelTest(BaseTestCase):
    
    def test_feedback_creation(self):
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(self.feedback.title, "Test Feedback")
        self.assertEqual(self.feedback.text, "This is a test feedback")
        self.assertEqual(self.feedback.user, self.user)
