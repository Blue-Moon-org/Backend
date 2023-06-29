from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .setup import BaseAPITestCase

User = get_user_model()



### Views Tests
class RegisterViewTest(BaseAPITestCase):
    def test_register_view(self):
        url = reverse(
            "register"
        )  
        data = {
            "email": "tesjpt@example.com",
            "username": "teskjgktuser",
            "phone":"123456pojpj7890",
            "password":"password",
            "brand_name":"My brand",
            "account_type":"Buyer",
            "firstname":"firstname",
            "lastname":"lastname",
        }
       
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        

class VerifyEmailTest(BaseAPITestCase):
    def test_verify_email_view(self):
        user = User.objects.create(email="test@example.com", username="testuser", otp=1234)
        user_data = {"email": "test@example.com", "otp":1234}
        url = reverse(
            "verify-email",
        )  # Assuming 'verify-email' is the URL name for VerifyEmail
        response = self.client.post(url, user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email="test@example.com").is_verified, True)


class LoginAPIViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
    
    def test_login_view(self):          
        user_data = {"email": "user@example.com", "password": "password"}
        url = reverse("login")  # Assuming 'login' is the URL name for LoginAPIView
        response = self.client.post(url, user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], True)


class ResetPasswordAPIViewTest(BaseAPITestCase):
    def test_reset_password_view(self):
        
        user_data = {"email": "user@example.com"}
        url = reverse(
            "reset-password"
        )  # Assuming 'reset-password' is the URL name for ResetPasswordAPIView
        response = self.client.post(url, user_data, format="json")
        user = User.objects.get(email="user@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email="user@example.com").otp, user.otp)


class ProfileViewTest(BaseAPITestCase):
    def test_profile_view(self):
        user = User.objects.create(email="test@example.com", username="testuser")
        self.client.force_authenticate(user=user)
        url = reverse("profile", args=["test@example.com"])  #Assuming 'profile' is the URL name for ProfileView
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")


class UpdateProfileViewTest(BaseAPITestCase):
    def test_update_profile_view(self):
        user = User.objects.create(email="test@example.com", username="testuser")
        self.client.force_authenticate(user=user)
        url = reverse(
            "update-profile"
        )  # Assuming 'update-profile' is the URL name for UpdateProfileView
        data = {"username": "updateduser"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "updateduser")


class ChangePasswordViewTest(BaseAPITestCase):
    def test_change_password_view(self):
        user = User.objects.create(
            email="test@example.com", username="testuser", is_active=True
        )
        self.client.force_authenticate(user=user)
        url = reverse(
            "change-password"
        )  # Assuming 'change-password' is the URL name for ChangePasswordView
        data = {"current_password": "testpassword", "new_password": "newpassword"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            User.objects.get(email="test@example.com").check_password("newpassword"),
            True,
        )


# class LogoutViewTest(BaseAPITestCase):
#     def test_logout_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         self.client.force_authenticate(user=user)
#         url = reverse("logout")  # Assuming 'logout' is the URL name for LogoutView
#         response = self.client.post(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Successfully logged out.")


class ResetPasswordViewTest(BaseAPITestCase):
    def test_reset_password_view(self):
        User.objects.create(email="test@example.com", username="testuser")
        url = reverse(
            "reset-password"
        )  # Assuming 'reset-password' is the URL name for ResetPasswordView
        data = {"email": "test@example.com"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password reset email has been sent.")


# class VerifyResetTokenViewTest(BaseAPITestCase):
#     def test_verify_reset_token_view(self):
#         user = User.objects.create(email="test@example.com", username="testuser")
#         token = user.tokens
#         url = reverse(
#             "verify-reset-token"
#         )  # Assuming 'verify-reset-token' is the URL name for VerifyResetTokenView
#         data = {"email": "test@example.com", "token": token}
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["detail"], "Token is valid.")


class SetNewPasswordViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()


    def test_set_new_password_view(self):
        url = reverse(
            "set-new-password"
        )  # Assuming 'set-new-password' is the URL name for SetNewPasswordView
        data = {
            "email": "user@example.com",
            "token": self.user.tokens,
            "password": "newpassword",
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "Password has been reset successfully."
        )


# class ActivateAccountViewTest(BaseAPITestCase):
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


class DeactivateAccountViewTest(BaseAPITestCase):
    def test_deactivate_account_view(self):
        user = User.objects.create(email="test@example.com", username="testuser")
        self.client.force_authenticate(user=user)
        url = reverse(
            "deactivate-account",
            args=["test@example.com"]
        )  # Assuming 'deactivate-account' is the URL name for DeactivateAccountView
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Account has been deactivated.")


class ChangePasswordViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            "change-password", args=["user@example.com"]
        )  # Assuming 'change-password' is the URL name for ChangePasswordView

    def test_change_password_view_with_valid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "password",
            "new_password": "newpassword",
        }
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(
        #     response.data["detail"], "Password has been changed successfully."
        # )

    def test_change_password_view_with_invalid_old_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword",
            "confirm_password": "newpassword",
        }
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #self.assertEqual(response.data["error"], "Invalid old password.")

    def test_change_password_view_with_mismatched_passwords(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "oldpassword",
            "new_password": "newpassword",
            "confirm_password": "mismatchedpassword",
        }
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(
        #     response.data["error"], "New password and confirm password do not match."
        # )


class UpdateProfileViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            "update-profile", args=["user@example.com"]
        )  

    def test_update_profile_view_with_valid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {"username": "newusername", "first_name": "John", "last_name": "Doe"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "newusername")

    def test_update_profile_view_with_empty_username(self):
        self.client.force_authenticate(user=self.user)
        data = {"email":"","username": "user", "firstname": "John", "lastname": "Doe"}
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "This field may not be blank.")

    def test_update_profile_view_unauthenticated(self):
        data = {"username": "newusername", "firstname": "John", "lastname": "Doe"}
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # self.assertEqual(
        #     response.data["message"], "Authentication credentials were not provided."
        # )


class ResetPasswordViewTest(BaseAPITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="password"
        )
        self.url = reverse(
            "reset-password"
        )  # Assuming 'reset-password' is the URL name for ResetPasswordView

    def test_reset_password_view_with_valid_data(self):
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password reset email has been sent.")

    def test_reset_password_view_with_invalid_email(self):
        data = {"email": "invalid@example.com"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Invalid email address.")

    def test_reset_password_view_with_blank_email(self):
        data = {"email": ""}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data["error"], "Email address is required.")


# class DeleteAccountViewTest(BaseAPITestCase):
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
