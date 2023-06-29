from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Feedback
from rest_framework.test import APITestCase

User = get_user_model()

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            phone="1234567890",
            password="password",
        )

        self.feedback = Feedback.objects.create(
            title="Test Feedback", text="This is a test feedback", user=self.user
        )

        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def register_user(self):
        return User.objects.create_user(**self.user_data)

    def verified_user(self):
        user = User.objects.create_user(**self.user_data)
        user.is_verified = True
        user.save()
        return user

class BaseTestCase(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            phone="1234567890",
            password="password",
        )

        self.feedback = Feedback.objects.create(
            title="Test Feedback", text="This is a test feedback", user=self.user
        )