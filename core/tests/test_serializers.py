from rest_framework import serializers
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.api.serializers import (
    RegisterSerializer,
    UserLessInfoSerializer,
    UserCountSerializer,
    LogoutSerializer,
    SetNewPasswordSerializer,
    ResendEmailSerializer,
    VerifyOTPResetSerializer,
    ResetPasswordSerializer,
    LoginSerializer,
    VerifyOTPRegisterSerializer,
    UserProfileSerializer,
    ListUserSerializer,
)

User = get_user_model()


class RegisterSerializerTest(TestCase):
    def test_validate_username(self):
        serializer = RegisterSerializer()

        # Test with a valid username
        attrs = {"username": "validusername123"}
        validated_attrs = serializer.validate(attrs)
        self.assertEqual(validated_attrs, attrs)

        # Test with an invalid username
        attrs = {"username": "invalid username!"}
        with self.assertRaises(serializers.ValidationError):
            serializer.validate(attrs)

    def test_create_user(self):
        serializer = RegisterSerializer()

        # Test creating a user with valid data
        data = {
            "email": "test1@example.com",
            "username": "test1user",
            "phone": "1234567891",
            "password": "testpassword",
            "brand_name": "Test Brand",
            "account_type": "Buyer",
            "firstname": "John",
            "lastname": "Doe",
        }
        user = serializer.create(data)
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test1@example.com")
        self.assertEqual(user.username, "test1user")
        self.assertEqual(user.phone, "1234567891")
        self.assertEqual(user.brand_name, "Test Brand")
        self.assertEqual(user.account_type, "Buyer")
        self.assertEqual(user.firstname, "John")
        self.assertEqual(user.lastname, "Doe")

        # Test creating a user with missing required fields
        incomplete_data = {
            "email":"",
            "username": "testuser",
            "password": "testpassword",
        }
        with self.assertRaises(ValueError):
            serializer.create(incomplete_data)


class UserLessInfoSerializerTest(TestCase):
    def test_user_less_info_serializer(self):
        user = User.objects.create(username="testuser", email="test@example.com")
        serializer = UserLessInfoSerializer(user)
        expected_data = {
            "username": "testuser",
            "fullname": " ",
            "image": None,
            "bio": None,
        }
        self.assertEqual(serializer.data, expected_data)


class UserCountSerializerTest(TestCase):
    def test_user_count_serializer(self):
        user = User.objects.create(username="testuser", email="test@example.com")
        serializer = UserCountSerializer(user)
        expected_data = {
            "id": str(user.id),
            "followers_count": 0,
            "following_count": 0,
        }
        self.assertEqual(serializer.data, expected_data)


# class LogoutSerializerTest(TestCase):
#     def test_logout_serializer(self):
#         serializer = LogoutSerializer(data={"refresh": "test_refresh_token"})
#         self.assertTrue(serializer.is_valid())
#         serializer.save()

#         # Add assertions to test the behavior of the save() method


class SetNewPasswordSerializerTest(TestCase):
    def test_set_new_password_serializer(self):
        user = User.objects.create(username="testuser", email="test@example.com")
        serializer = SetNewPasswordSerializer(
            data={"email": "test@example.com", "password": "newpassword"}
        )
        self.assertTrue(serializer.is_valid())
        # user = serializer.save()

        # self.assertIsInstance(user, User)
        # self.assertEqual(user.password, "newpassword")


class ResendEmailSerializerTest(TestCase):
    def test_resend_email_serializer(self):
        user = User.objects.create(
            username="testuser", email="test@example.com", is_active=True
        )
        serializer = ResendEmailSerializer(data={"email": "test@example.com"})
        self.assertTrue(serializer.is_valid())
        attrs = serializer.validate({"email": "test@example.com"})
        self.assertEqual(attrs, {"email": "test@example.com"})


class VerifyOTPResetSerializerTest(TestCase):
    def test_verify_otp_reset_serializer(self):
        user = User.objects.create(
            username="testuser", email="test@example.com", is_active=True, otp=1234
        )
        serializer = VerifyOTPResetSerializer(
            data={"email": "test@example.com", "otp": 1234}
        )
        self.assertTrue(serializer.is_valid())
        validated_attrs = serializer.validate(
            {"email": "test@example.com", "otp": 1234}
        )
        expected_attrs = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "slug": user.slug,
        }
        self.assertEqual(validated_attrs, expected_attrs)


class ResetPasswordSerializerTest(TestCase):
    def test_reset_password_serializer(self):
        serializer = ResetPasswordSerializer(data={"email": "test@example.com"})
        self.assertTrue(serializer.is_valid())
        attrs = serializer.validate({"email": "test@example.com"})
        self.assertEqual(attrs, {"email": "test@example.com"})


# class LoginSerializerTest(TestCase):
#     def test_login_serializer(self):
#         self.maxDiff = None
#         user = User.objects.create(
#             username="testuser", email="test@example.com", is_active=True
#         )
#         user.set_password("testpassword")
#         user.save()

#         serializer = LoginSerializer(
#             data={"email": "test@example.com", "password": "testpassword"}
#         )
#         self.assertTrue(serializer.is_valid())
#         validated_attrs = serializer.validate(
#             {"email": "test@example.com", "password": "testpassword"}
#         )
#         expected_attrs = {
#             "email": "test@example.com",
#             "tokens": user.tokens,
#         }
#         self.assertEqual(validated_attrs, expected_attrs)


# class VerifyOTPRegisterSerializerTest(TestCase):
#     def test_verify_otp_register_serializer(self):
#         self.maxDiff = None
#         user = User.objects.create(
#             username="testuser", email="test@example.com", is_active=True, otp=1234
#         )
#         serializer = VerifyOTPRegisterSerializer(
#             data={"email": "test@example.com", "otp": 1234}
#         )
#         self.assertTrue(serializer.is_valid())
#         validated_attrs = serializer.validate(
#             {"email": "test@example.com", "otp": 1234}
#         )
#         expected_attrs = {
#             "id": user.id,
#             "email": user.email,
#             "username": user.username,
#             "slug": user.slug,
#             "refresh_token": user.tokens["refresh"],
#             "access_token": user.tokens["access"],
#         }
#         self.assertEqual(validated_attrs, expected_attrs)


# class UserProfileSerializerTest(TestCase):
#     def test_user_profile_serializer(self):
#         user = User.objects.create(username="testuser", email="test@example.com")
#         serializer = UserProfileSerializer(user)
#         expected_data = {
#             "id": user.id,
#             "username": "testuser",
#             "email": "test@example.com",
#             "fullname": "",
#             "call_code": "",
#             "phone": "",
#             "bio": "",
#             "sex": "",
#             "country": "",
#             "state": "",
#             "address": "",
#             "city": "",
#             "location": "",
#             "day": None,
#             "month": None,
#             "year": None,
#             "dob": None,
#             "followers_count": 0,
#             "followers": [],
#             "following_count": 0,
#             "following": False,
#             "slug": user.slug,
#             "tos": False,
#             "is_self": False,
#             "created": None,
#             "created_at": None,
#         }
#         self.assertEqual(serializer.data, expected_data)


# class ListUserSerializerTest(TestCase):
#     def test_list_user_serializer(self):
#         user = User.objects.create(username="testuser", email="test@example.com")
#         serializer = ListUserSerializer(user)
#         expected_data = {
#             "id": user.id,
#             "username": "testuser",
#             "email": "test@example.com",
#             "call_code": "",
#             "phone": "",
#             "bio": "",
#             "sex": "",
#             "country": "",
#             "state": "",
#             "address": "",
#             "city": "",
#             "location": "",
#             "day": None,
#             "month": None,
#             "year": None,
#             "dob": None,
#             "otp": 0,
#             "followers_count": 0,
#             "followers": [],
#             "following_count": 0,
#             "following": False,
#             "is_verified": False,
#             "is_active": False,
#             "active": False,
#             "is_staff": False,
#             "is_admin": False,
#             "is_banned": False,
#             "slug": "",
#             "tos": False,
#             "tokens": {},
#             "created": None,
#             "created_at": None,
#         }
#         self.assertEqual(serializer.data, expected_data)
