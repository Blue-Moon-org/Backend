from django.urls import path
from .views import (
    # UserIDView,
    RegisterView,
    UserProfile,
    # ResendRegisterEmailView,
    VerifyEmail,
    LoginAPIView,
    # ResendLoginEmailView,
    # VerifyLoginEmail,
    ResetPasswordAPIView,
    # ResendResetPasswordView,
    # VerifyResetEmail,
    SetNewPasswordAPIView,
    LogoutAPIView,
    VerifyResetPassword,
    follow_unfollow_user,
    UserFollowers,
    UserFollowing,
    user_followed_user,
    ChangePassword,
    UserUpdateView,
    UserDetailView,
    UserDeleteView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    # path("user-id/", UserIDView.as_view(), name="user-id"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/<str:email>/", UserProfile.as_view(), name="profile"),
    # path(
    #     "resend-register-code/",
    #     ResendRegisterEmailView.as_view(),
    #     name="resend-register-code",
    # ),
    path("login/", LoginAPIView.as_view(), name="login"),
    # path(
    #     "resend-login-code/", ResendLoginEmailView.as_view(), name="resend-login-code"
    # ),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("forgot-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path(
        "verify-forgot-password/",
        VerifyResetPassword.as_view(),
        name="verify-forgot-password",
    ),
    path("set-new-password/", SetNewPasswordAPIView.as_view(), name="set-new-password"),
    path("verify-email/", VerifyEmail.as_view(), name="verify-email"),
    # path("email-login-verify/", VerifyLoginEmail.as_view(), name="email-login-verify"),
    # path("email-reset-verify/", VerifyResetEmail.as_view(), name="email-reset-verify"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("user/update/<email>/", UserUpdateView.as_view(), name="update-profile"),
    path("user/delete/<email>/", UserDeleteView.as_view(), name="deactivate-account"),
    path("user/retrieve/<username>/", UserDetailView.as_view(), name="user-detail"),
    path("follow/user/", follow_unfollow_user, name="follow_unfollow_user"),
    path("followers/<username>/", UserFollowers.as_view(), name="user_followers"),
    path("following/<username>/", UserFollowing.as_view(), name="user_following"),
    path("user/followed/user/", user_followed_user, name="user_followed_user"),
    path("password/<email>/", ChangePassword.as_view(), name="change-password"),
]
