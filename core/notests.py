# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from .models import Feedback
# from django.test import TestCase
# from .api.serializers import (
#     RegisterSerializer,
#     UserLessInfoSerializer,
#     UserCountSerializer,
#     LogoutSerializer,
#     SetNewPasswordSerializer,
#     ResendEmailSerializer,
#     VerifyOTPResetSerializer,
#     ResetPasswordSerializer,
#     LoginSerializer,
#     VerifyOTPRegisterSerializer,
#     UserProfileSerializer,
#     ListUserSerializer,
# )
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from .models import User

# User = get_user_model()


# # class UserModelTest(TestCase):
# #     def setUp(self):
# #         self.user = User.objects.create_user(
# #             username="testuser",
# #             email="test@example.com",
# #             phone="1234567890",
# #             password="testpassword",
# #         )

# #     def test_user_creation(self):
# #         self.assertEqual(User.objects.count(), 1)
# #         self.assertEqual(self.user.username, "testuser")
# #         self.assertEqual(self.user.email, "test@example.com")
# #         self.assertEqual(self.user.phone, "1234567890")
# #         self.assertTrue(self.user.check_password("testpassword"))
# #         self.assertFalse(self.user.is_staff)
# #         self.assertFalse(self.user.is_superuser)
# #         self.assertFalse(self.user.is_banned)
# #         self.assertFalse(self.user.is_verified)
# #         self.assertTrue(self.user.is_active)

# #     def test_user_fullname_property(self):
# #         self.user.firstname = "John"
# #         self.user.lastname = "Doe"
# #         self.assertEqual(self.user.fullname, "John Doe")

# #     def test_user_followers_count(self):
# #         follower = User.objects.create_user(
# #             username="follower",
# #             email="follower@example.com",
# #             phone="9876543210",
# #             password="followerpassword",
# #         )
# #         self.user.followers.add(follower)
# #         self.assertEqual(self.user.followers_count, 1)

# #     def test_user_following_count(self):
# #         following = User.objects.create_user(
# #             username="following",
# #             email="following@example.com",
# #             phone="5678901234",
# #             password="followingpassword",
# #         )
# #         self.user.following.add(following)
# #         self.assertEqual(self.user.following_count, 1)


# # class FeedbackModelTest(TestCase):
# #     def setUp(self):
# #         self.user = User.objects.create_user(
# #             username="testuser",
# #             email="test@example.com",
# #             phone="1234567890",
# #             password="testpassword",
# #         )
# #         self.feedback = Feedback.objects.create(
# #             title="Test Feedback", text="This is a test feedback", user=self.user
# #         )

# #     def test_feedback_creation(self):
# #         self.assertEqual(Feedback.objects.count(), 1)
# #         self.assertEqual(self.feedback.title, "Test Feedback")
# #         self.assertEqual(self.feedback.text, "This is a test feedback")
# #         self.assertEqual(self.feedback.user, self.user)


# # class RegisterSerializerTest(TestCase):
# #     def test_validate_username(self):
# #         serializer = RegisterSerializer()

# #         # Test with a valid username
# #         attrs = {"username": "validusername123"}
# #         validated_attrs = serializer.validate(attrs)
# #         self.assertEqual(validated_attrs, attrs)

# #         # Test with an invalid username
# #         attrs = {"username": "invalid username!"}
# #         with self.assertRaises(serializer.ValidationError):
# #             serializer.validate(attrs)

# #     def test_create_user(self):
# #         serializer = RegisterSerializer()

# #         # Test creating a user with valid data
# #         data = {
# #             "email": "test@example.com",
# #             "username": "testuser",
# #             "phone": "1234567890",
# #             "password": "testpassword",
# #             "brand_name": "Test Brand",
# #             "account_type": "Buyer",
# #             "firstname": "John",
# #             "lastname": "Doe",
# #         }
# #         user = serializer.create(data)
# #         self.assertIsInstance(user, User)
# #         self.assertEqual(user.email, "test@example.com")
# #         self.assertEqual(user.username, "testuser")
# #         self.assertEqual(user.phone, "1234567890")
# #         self.assertEqual(user.brand_name, "Test Brand")
# #         self.assertEqual(user.account_type, "Buyer")
# #         self.assertEqual(user.firstname, "John")
# #         self.assertEqual(user.lastname, "Doe")

# #         # Test creating a user with missing required fields
# #         incomplete_data = {
# #             "email": "test@example.com",
# #             "username": "testuser",
# #             "password": "testpassword",
# #         }
# #         with self.assertRaises(KeyError):
# #             serializer.create(incomplete_data)


# # class UserLessInfoSerializerTest(TestCase):
# #     def test_user_less_info_serializer(self):
# #         user = User.objects.create(username="testuser", email="test@example.com")
# #         serializer = UserLessInfoSerializer(user)
# #         expected_data = {
# #             "username": "testuser",
# #             "fullname": "",
# #             "image": "",
# #             "bio": "",
# #         }
# #         self.assertEqual(serializer.data, expected_data)


# # class UserCountSerializerTest(TestCase):
# #     def test_user_count_serializer(self):
# #         user = User.objects.create(username="testuser", email="test@example.com")
# #         serializer = UserCountSerializer(user)
# #         expected_data = {
# #             "id": user.id,
# #             "followers_count": 0,
# #             "following_count": 0,
# #         }
# #         self.assertEqual(serializer.data, expected_data)


# # class LogoutSerializerTest(TestCase):
# #     def test_logout_serializer(self):
# #         serializer = LogoutSerializer(data={"refresh": "test_refresh_token"})
# #         self.assertTrue(serializer.is_valid())
# #         serializer.save()

# #         # Add assertions to test the behavior of the save() method


# # class SetNewPasswordSerializerTest(TestCase):
# #     def test_set_new_password_serializer(self):
# #         user = User.objects.create(username="testuser", email="test@example.com")
# #         serializer = SetNewPasswordSerializer(
# #             data={"email": "test@example.com", "password": "newpassword"}
# #         )
# #         self.assertTrue(serializer.is_valid())
# #         user = serializer.save()

# #         # Add assertions to test the behavior of the save() method


# # class ResendEmailSerializerTest(TestCase):
# #     def test_resend_email_serializer(self):
# #         user = User.objects.create(
# #             username="testuser", email="test@example.com", is_active=True
# #         )
# #         serializer = ResendEmailSerializer(data={"email": "test@example.com"})
# #         self.assertTrue(serializer.is_valid())
# #         attrs = serializer.validate({"email": "test@example.com"})
# #         self.assertEqual(attrs, {"email": "test@example.com"})


# # class VerifyOTPResetSerializerTest(TestCase):
# #     def test_verify_otp_reset_serializer(self):
# #         user = User.objects.create(
# #             username="testuser", email="test@example.com", is_active=True, otp=1234
# #         )
# #         serializer = VerifyOTPResetSerializer(
# #             data={"email": "test@example.com", "otp": 1234}
# #         )
# #         self.assertTrue(serializer.is_valid())
# #         validated_attrs = serializer.validate(
# #             {"email": "test@example.com", "otp": 1234}
# #         )
# #         expected_attrs = {
# #             "id": user.id,
# #             "email": user.email,
# #             "username": user.username,
# #             "slug": user.slug,
# #         }
# #         self.assertEqual(validated_attrs, expected_attrs)


# # class ResetPasswordSerializerTest(TestCase):
# #     def test_reset_password_serializer(self):
# #         serializer = ResetPasswordSerializer(data={"email": "test@example.com"})
# #         self.assertTrue(serializer.is_valid())
# #         attrs = serializer.validate({"email": "test@example.com"})
# #         self.assertEqual(attrs, {"email": "test@example.com"})


# # class LoginSerializerTest(TestCase):
# #     def test_login_serializer(self):
# #         user = User.objects.create(
# #             username="testuser", email="test@example.com", is_active=True
# #         )
# #         user.set_password("testpassword")
# #         user.save()

# #         serializer = LoginSerializer(
# #             data={"email": "test@example.com", "password": "testpassword"}
# #         )
# #         self.assertTrue(serializer.is_valid())
# #         validated_attrs = serializer.validate(
# #             {"email": "test@example.com", "password": "testpassword"}
# #         )
# #         expected_attrs = {
# #             "email": "test@example.com",
# #             "tokens": user.tokens,
# #         }
# #         self.assertEqual(validated_attrs, expected_attrs)


# # class VerifyOTPRegisterSerializerTest(TestCase):
# #     def test_verify_otp_register_serializer(self):
# #         user = User.objects.create(
# #             username="testuser", email="test@example.com", is_active=True, otp=1234
# #         )
# #         serializer = VerifyOTPRegisterSerializer(
# #             data={"email": "test@example.com", "otp": 1234}
# #         )
# #         self.assertTrue(serializer.is_valid())
# #         validated_attrs = serializer.validate(
# #             {"email": "test@example.com", "otp": 1234}
# #         )
# #         expected_attrs = {
# #             "id": user.id,
# #             "email": user.email,
# #             "username": user.username,
# #             "slug": user.slug,
# #             "refresh_token": user.refresh_token,
# #             "access_token": user.access_token,
# #         }
# #         self.assertEqual(validated_attrs, expected_attrs)


# # class UserProfileSerializerTest(TestCase):
# #     def test_user_profile_serializer(self):
# #         user = User.objects.create(username="testuser", email="test@example.com")
# #         serializer = UserProfileSerializer(user)
# #         expected_data = {
# #             "id": user.id,
# #             "username": "testuser",
# #             "email": "test@example.com",
# #             "fullname": "",
# #             "call_code": "",
# #             "phone": "",
# #             "bio": "",
# #             "sex": "",
# #             "country": "",
# #             "state": "",
# #             "address": "",
# #             "city": "",
# #             "location": "",
# #             "day": None,
# #             "month": None,
# #             "year": None,
# #             "dob": None,
# #             "followers_count": 0,
# #             "followers": [],
# #             "following_count": 0,
# #             "following": False,
# #             "slug": "",
# #             "tos": False,
# #             "is_self": False,
# #             "created": None,
# #             "created_at": None,
# #         }
# #         self.assertEqual(serializer.data, expected_data)


# # class ListUserSerializerTest(TestCase):
# #     def test_list_user_serializer(self):
# #         user = User.objects.create(username="testuser", email="test@example.com")
# #         serializer = ListUserSerializer(user)
# #         expected_data = {
# #             "id": user.id,
# #             "username": "testuser",
# #             "email": "test@example.com",
# #             "name": "",
# #             "call_code": "",
# #             "phone": "",
# #             "bio": "",
# #             "sex": "",
# #             "country": "",
# #             "state": "",
# #             "address": "",
# #             "city": "",
# #             "location": "",
# #             "day": None,
# #             "month": None,
# #             "year": None,
# #             "dob": None,
# #             "otp": 0,
# #             "followers_count": 0,
# #             "followers": [],
# #             "following_count": 0,
# #             "following": False,
# #             "is_verified": False,
# #             "is_active": False,
# #             "active": False,
# #             "is_staff": False,
# #             "is_admin": False,
# #             "is_banned": False,
# #             "slug": "",
# #             "tos": False,
# #             "tokens": {},
# #             "created": None,
# #             "created_at": None,
# #         }
# #         self.assertEqual(serializer.data, expected_data)


# ### Views Tests
# class RegisterViewTest(APITestCase):
#     def test_register_view(self):
#         url = reverse(
#             "register"
#         )  # Assuming 'register' is the URL name for RegisterView
#         data = {
#             "email": "test@example.com",
#             "username": "testuser",
#             "password": "testpassword",
#         }
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(User.objects.count(), 1)
#         self.assertEqual(User.objects.get().email, "test@example.com")


# class VerifyEmailTest(APITestCase):
#     def test_verify_email_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         user_data = {"email": "test@example.com"}
#         url = reverse(
#             "verify-email", kwargs={"email": user.email}
#         )  # Assuming 'verify-email' is the URL name for VerifyEmail
#         response = self.client.post(url, user_data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(User.objects.get(email="test@example.com").is_verified, True)


# class LoginAPIViewTest(APITestCase):
#     def test_login_view(self):
#         user = User.objects.create(
#             email="test@example.com", username="testuser", is_active=True
#         )
#         user_data = {"email": "test@example.com", "password": "testpassword"}
#         url = reverse("login")  # Assuming 'login' is the URL name for LoginAPIView
#         response = self.client.post(url, user_data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["status"], True)


# class ResetPasswordAPIViewTest(APITestCase):
#     def test_reset_password_view(self):
#         user = User.objects.create(
#             email="test@example.com", username="testuser", is_active=True
#         )
#         user_data = {"email": "test@example.com"}
#         url = reverse(
#             "reset-password"
#         )  # Assuming 'reset-password' is the URL name for ResetPasswordAPIView
#         response = self.client.post(url, user_data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(User.objects.get(email="test@example.com").otp, 0)


# class ProfileViewTest(APITestCase):
#     def test_profile_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         self.client.force_authenticate(user=user)
#         url = reverse("profile")  # Assuming 'profile' is the URL name for ProfileView
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["username"], "testuser")


# class UpdateProfileViewTest(APITestCase):
#     def test_update_profile_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         self.client.force_authenticate(user=user)
#         url = reverse(
#             "update-profile"
#         )  # Assuming 'update-profile' is the URL name for UpdateProfileView
#         data = {"username": "updateduser"}
#         response = self.client.patch(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["username"], "updateduser")


# class ChangePasswordViewTest(APITestCase):
#     def test_change_password_view(self):
#         user = User.objects.create(
#             email="test@example.com", username="testuser", is_active=True
#         )
#         self.client.force_authenticate(user=user)
#         url = reverse(
#             "change-password"
#         )  # Assuming 'change-password' is the URL name for ChangePasswordView
#         data = {"current_password": "testpassword", "new_password": "newpassword"}
#         response = self.client.patch(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(
#             User.objects.get(email="test@example.com").check_password("newpassword"),
#             True,
#         )


# class LogoutViewTest(APITestCase):
#     def test_logout_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         self.client.force_authenticate(user=user)
#         url = reverse("logout")  # Assuming 'logout' is the URL name for LogoutView
#         response = self.client.post(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Successfully logged out.")


# class ResetPasswordViewTest(APITestCase):
#     def test_reset_password_view(self):
#         User.objects.create(email="test@example.com", username="testuser")
#         url = reverse(
#             "reset-password"
#         )  # Assuming 'reset-password' is the URL name for ResetPasswordView
#         data = {"email": "test@example.com"}
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Password reset email has been sent.")


# class VerifyResetTokenViewTest(APITestCase):
#     def test_verify_reset_token_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         token = user.generate_reset_token()
#         url = reverse(
#             "verify-reset-token"
#         )  # Assuming 'verify-reset-token' is the URL name for VerifyResetTokenView
#         data = {"email": "test@example.com", "token": token}
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Token is valid.")


# class SetNewPasswordViewTest(APITestCase):
#     def test_set_new_password_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         token = user.generate_reset_token()
#         url = reverse(
#             "set-new-password"
#         )  # Assuming 'set-new-password' is the URL name for SetNewPasswordView
#         data = {
#             "email": "test@example.com",
#             "token": token,
#             "new_password": "newpassword",
#         }
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(
#             response.data["detail"], "Password has been reset successfully."
#         )


# class ActivateAccountViewTest(APITestCase):
#     def test_activate_account_view(self):
#         user = User.objects.create(
#             email="test@example.com", username="testuser", is_active=False
#         )
#         token = user.generate_activation_token()
#         url = reverse(
#             "activate-account"
#         )  # Assuming 'activate-account' is the URL name for ActivateAccountView
#         data = {"email": "test@example.com", "token": token}
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Account has been activated.")


# class DeactivateAccountViewTest(APITestCase):
#     def test_deactivate_account_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         self.client.force_authenticate(user=user)
#         url = reverse(
#             "deactivate-account"
#         )  # Assuming 'deactivate-account' is the URL name for DeactivateAccountView
#         response = self.client.post(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Account has been deactivated.")


# class ChangePasswordViewTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email="test@example.com", username="testuser", password="oldpassword"
#         )
#         self.url = reverse(
#             "change-password"
#         )  # Assuming 'change-password' is the URL name for ChangePasswordView

#     def test_change_password_view_with_valid_data(self):
#         self.client.force_authenticate(user=self.user)
#         data = {
#             "old_password": "oldpassword",
#             "new_password": "newpassword",
#             "confirm_password": "newpassword",
#         }
#         response = self.client.post(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(
#             response.data["detail"], "Password has been changed successfully."
#         )

#     def test_change_password_view_with_invalid_old_password(self):
#         self.client.force_authenticate(user=self.user)
#         data = {
#             "old_password": "wrongpassword",
#             "new_password": "newpassword",
#             "confirm_password": "newpassword",
#         }
#         response = self.client.post(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Invalid old password.")

#     def test_change_password_view_with_mismatched_passwords(self):
#         self.client.force_authenticate(user=self.user)
#         data = {
#             "old_password": "oldpassword",
#             "new_password": "newpassword",
#             "confirm_password": "mismatchedpassword",
#         }
#         response = self.client.post(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             response.data["error"], "New password and confirm password do not match."
#         )


# class UpdateProfileViewTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email="test@example.com", username="testuser", password="password"
#         )
#         self.url = reverse(
#             "update-profile"
#         )  # Assuming 'update-profile' is the URL name for UpdateProfileView

#     def test_update_profile_view_with_valid_data(self):
#         self.client.force_authenticate(user=self.user)
#         data = {"username": "newusername", "first_name": "John", "last_name": "Doe"}
#         response = self.client.patch(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["username"], "newusername")
#         self.assertEqual(response.data["first_name"], "John")
#         self.assertEqual(response.data["last_name"], "Doe")

#     def test_update_profile_view_with_empty_username(self):
#         self.client.force_authenticate(user=self.user)
#         data = {"username": "", "first_name": "John", "last_name": "Doe"}
#         response = self.client.patch(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["username"][0], "This field may not be blank.")

#     def test_update_profile_view_unauthenticated(self):
#         data = {"username": "newusername", "first_name": "John", "last_name": "Doe"}
#         response = self.client.patch(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(
#             response.data["detail"], "Authentication credentials were not provided."
#         )


# class ResetPasswordViewTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email="test@example.com", username="testuser", password="password"
#         )
#         self.url = reverse(
#             "reset-password"
#         )  # Assuming 'reset-password' is the URL name for ResetPasswordView

#     def test_reset_password_view_with_valid_data(self):
#         data = {"email": "test@example.com"}
#         response = self.client.post(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Password reset email has been sent.")

#     def test_reset_password_view_with_invalid_email(self):
#         data = {"email": "invalid@example.com"}
#         response = self.client.post(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Invalid email address.")

#     def test_reset_password_view_with_blank_email(self):
#         data = {"email": ""}
#         response = self.client.post(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Email address is required.")


# class DeleteAccountViewTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email="test@example.com", username="testuser", password="password"
#         )
#         self.url = reverse(
#             "delete-account"
#         )  # Assuming 'delete-account' is the URL name for DeleteAccountView

#     def test_delete_account_view_with_valid_credentials(self):
#         self.client.force_authenticate(user=self.user)
#         data = {"password": "password"}
#         response = self.client.delete(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(response.data, None)

#     def test_delete_account_view_with_invalid_password(self):
#         self.client.force_authenticate(user=self.user)
#         data = {"password": "wrongpassword"}
#         response = self.client.delete(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Invalid password.")

#     def test_delete_account_view_unauthenticated(self):
#         data = {"password": "password"}
#         response = self.client.delete(self.url, data)

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(
#             response.data["detail"], "Authentication credentials were not provided."
#         )
