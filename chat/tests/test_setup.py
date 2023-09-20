from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker
import random
from core.models import User


class TestSetUp(APITestCase):
    def setUp(self):
        self.headerInfo = {"content-type": "application/json"}
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.fake = Faker()

        self.user_data = {
            "email": self.fake.email(),
            "username": self.fake.email().split("@")[0],
            "password": self.fake.email(),
            "phone": str(random.randint(0000000000, 9999999999)),
        }

        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def register_user(self):
        return User.objects.create_user(**self.user_data)
