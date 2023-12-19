from django.urls import path
from .views import (
    AddToNotify,
    CheckEmailView,
    CheckPhoneView,
    FollowUnfollowUser,
    PhoneVerifyAPIView,
    RegisterView,
    ResendOtpAPIView,
    UserLocationView,
    UserProfile,
    VerifyEmail,
    LoginAPIView,
    ResetPasswordAPIView,
    SetNewPasswordAPIView,
    LogoutAPIView,
    VerifyResetPassword,
    UserFollowers,
    UserFollowing,
    ChangePassword,
    UserUpdateView,
    UserDetailView,
    UserDeleteView,
    FeedbackCreateView,
    VerifyPhone,
    BlockUserView,
    ReportView
)
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/<str:email>/", UserProfile.as_view(), name="profile"),
    path("checkemail/<str:email>/", CheckEmailView.as_view(), name="check-email"),
    path("checkphone/<str:phone>/", CheckPhoneView.as_view(), name="check-phone"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("forgot-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path(
        "verify-forgot-password/",
        VerifyResetPassword.as_view(),
        name="verify-forgot-password",
    ),
    path("resend-otp/<str:email>/", ResendOtpAPIView.as_view(), name="resend-otp"),
    path("phone-verify/", PhoneVerifyAPIView.as_view(), name="phone-verify"),
    path("set-new-password/", SetNewPasswordAPIView.as_view(), name="set-new-password"),
    path("verify-email/", VerifyEmail.as_view(), name="verify-email"),
    path("verify-phone/", VerifyPhone.as_view(), name="verify-phone"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("user/update/", UserUpdateView.as_view(), name="update-profile"),
    path("user/delete/<email>/", UserDeleteView.as_view(), name="deactivate-account"),
    path("user/retrieve/<username>/", UserDetailView.as_view(), name="user-detail"),
    path("follow/user/", FollowUnfollowUser.as_view(), name="follow_unfollow_user"),
    path("followers/<id>/", UserFollowers.as_view(), name="user_followers"),
    path("following/<id>/", UserFollowing.as_view(), name="user_following"),
    path("add_to_notify/<id>/", AddToNotify.as_view(), name="user_following"),
    path("block_user/", BlockUserView.as_view(), name="user_blocked"),
    #path("user/followed/user/", user_followed_user, name="user_followed_user"),
    path("password/<email>/", ChangePassword.as_view(), name="change-password"),
    path("feedback/", FeedbackCreateView.as_view(), name="feedback"),
    path("report/", ReportView.as_view(), name="feedback"),
    path('get_users_within_range/', UserLocationView.as_view(), name='get_users_within_range'),
    # Only allow creation of devices by authenticated users
    path('devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),

]
