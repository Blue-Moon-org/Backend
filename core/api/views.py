import random
from datetime import date

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import get_template

from core.models import User, Feedback
from notification.models import Notification
from .serializers import (
    GetEmailSerializer,
    ListUserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LogoutSerializer,
    LoginSerializer,
    VerifyOTPRegisterSerializer,
    FeedbackSerializer,
    SetNewPasswordSerializer,
    ResetPasswordSerializer,
    VerifyOTPResetSerializer,
)
from core.email import *
from rest_framework import generics, status, permissions
from rest_framework.generics import (
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from helper.utils import Util
from twilio.rest import Client


class RegisterView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        data = request.data
        data["email"] = data["email"].lower()
        if not User.objects.filter(email=data["email"]).exists():
            serializer = RegisterSerializer(data=data)
            user_data = {}

            if serializer.is_valid():
                serializer.save()
                user_data = serializer.data
                otp = random.randint(100000, 999999)
                user = User.objects.get(email=user_data["email"])
                user.otp = otp
                now = date.today()
                user.day = now.day
                user.month = now.month
                user.year = now.year
                user.is_active = True
                user_data["email"] = user.email
                user_data["phone"] = user.phone

                if not user_data.get("google", False):
                    html_tpl_path = "email/welcome.html"
                    context_data = {"name": user.firstname, "code": user.otp}
                    email_html_template = get_template(html_tpl_path).render(
                        context_data
                    )
                    data = {
                        "email_body": email_html_template,
                        "to_email": user.email,
                        "email_subject": "BlueMoon email Verification",
                    }
                    Util.send_email(data)
                user.save()
                return Response(user_data, status=status.HTTP_201_CREATED)

            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"status": False, "message": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyEmail(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = VerifyOTPRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPRegisterSerializer(data=request.data)
        user_data = {}

        if serializer.is_valid():
            user_data = serializer.data
            email = serializer.data["email"]
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user=user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)
            user.is_verified = True
            user.is_active = True
            user.active = True
            user.otp = 0
            user.save()
            return Response(
                {
                    "status": True,
                    "data": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "phone": user.phone,
                        "slug": user.slug,
                        "refresh_token": refresh_token,
                        "access_token": access_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = UserProfileSerializer(User.objects.get(email=user_data["email"])).data
        data = {"tokens": user_data["tokens"], "user_data": user}
        return Response({"status": True, "data": data}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = User.objects.filter(email=user_data["email"]).first()
        if user and user.is_active:
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()
            html_tpl_path = "email/reset.html"
            context_data = {"name": user.firstname, "code": user.otp}
            email_html_template = get_template(html_tpl_path).render(context_data)
            data = {
                "email_body": email_html_template,
                "to_email": user.email,
                "email_subject": "BlueMoon reset password verification",
            }

            Util.send_email(data)
            return Response(
                {
                    "status": True,
                    "data": serializer.data,
                    "message": "Password reset email has been sent.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Invalid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResendOtpAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = GetEmailSerializer

    def post(self, request, email):
        serializer = GetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = User.objects.filter(email=user_data["email"]).first()
        if user and user.is_active:
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            if email == "email":
                # Send the verification code via email
                html_tpl_path = "email/welcome.html"
                context_data = {"name": user.firstname, "code": user.otp}
                email_html_template = get_template(html_tpl_path).render(context_data)
                data = {
                    "email_body": email_html_template,
                    "to_email": user.email,
                    "email_subject": "BlueMoon email Verification",
                }
                Util.send_email(data)
            else:
                # Send the verification code via SMS using Twilio
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=f"Your verification code is: {user.otp}",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to="+234" + user.phone[1:],
                )

            return Response(
                {
                    "status": True,
                    "data": serializer.data,
                    "message": "Verification code has been sent.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Invalid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PhoneVerifyAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = GetEmailSerializer

    def post(self, request):
        serializer = GetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = User.objects.filter(email=user_data["email"]).first()
        if user and user.is_active:
            verification_code = random.randint(100000, 999999)
            user.otp = verification_code
            user.save()

            # Send the verification code via SMS using Twilio
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your verification code is: {verification_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to="+234" + user.phone[1:],
            )

            return Response(
                {
                    "status": True,
                    "data": serializer.data,
                    "message": "Verification code has been sent.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Invalid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyResetPassword(generics.GenericAPIView):
    serializer_class = VerifyOTPResetSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPResetSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.data
            email = user_data["email"]
            user = User.objects.get(email=email)
            # refresh = RefreshToken.for_user(user=user)
            # refresh_token = str(refresh)
            # access_token = str(refresh.access_token)
            user.otp = 0
            user.save()
            return Response(
                {
                    "status": True,
                    "data": {
                        "email": user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(id=user_data["id"])
        if user.is_verified:
            user.active = False
            user.otp = 0
            user.save()

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class FeedbackCreateView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        title = request.data.get("title")
        text = request.data.get("text")
        username = request.data.get("username")
        author = request.user

        with transaction.atomic():
            feedback = Feedback.objects.create(title=title, text=text, user=author)
        d = FeedbackSerializer(feedback).data
        return Response(d, status=status.HTTP_201_CREATED)


class UserFollowers(APIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ListUserSerializer

    def get(self, request, id, format=None):
        try:
            found_user = User.objects.get(id=id)
            print(f"found user {found_user}")
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_followers = found_user.followers.all()
        serializer = self.serializer_class(user_followers, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserFollowing(APIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ListUserSerializer

    def get(self, request, id, format=None):
        try:
            found_user = User.objects.get(id=id)
            print(f"found user {found_user}")
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_following = found_user.following.all()
        serializer = self.serializer_class(
            user_following, many=True, context={"request": request}
        )

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class FollowUnfollowUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        id = request.data.get("id")
        fu_user = get_object_or_404(User, id=id)
        user = request.user

        if fu_user in user.following.all():
            following = False
            user.following.remove(fu_user)
            user.save()
            fu_user.followers.remove(user)
            fu_user.save()

            notify, _ = Notification.objects.get_or_create(
                notification_type="UF",
                comments=f"@{user.firstname} unfollowed you",
                to_user=fu_user,
                from_user=user,
            )
        else:
            following = True
            user.following.add(fu_user)
            user.save()
            fu_user.followers.add(user)
            fu_user.save()

            notify, _ = Notification.objects.get_or_create(
                notification_type="F",
                comments=f"@{user.firstname} followed you",
                to_user=fu_user,
                from_user=user,
            )
        notify.save()
        
        return Response(
            {
                "following": following,
            },
            status=status.HTTP_201_CREATED,
        )




class AddToNotify(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        id = request.data.get("id")
        fu_user = get_object_or_404(User, id=id)
        user = request.user

        if fu_user in user.users_notify.all():
            user_added = False
            user.users_notify.remove(fu_user)
            user.save()
            
        else:
            user_added = True
            user.users_notify.add(fu_user)
            user.save()
        
        return Response(
            {
                "user_added": user_added,
            },
            status=status.HTTP_201_CREATED,
        )



# @api_view(["POST"])
# @permission_classes((AllowAny,))
# def user_followed_user(request):
#     if request.method == "POST":
#         username = request.data.get("username")
#         fu_user = get_object_or_404(User, username=username)
#         user = request.user
#         if user in fu_user.followers.all():
#             following = True
#         else:
#             following = False
#         return Response(
#             {
#                 "following": following,
#             },
#             status=status.HTTP_201_CREATED,
#         )


class UserProfile(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_user(self, email):
        try:
            found_user = User.objects.get(email=email)
            return found_user
        except User.DoesNotExist:
            return None

    def get(self, request, email, format=None):
        found_user = self.get_user(email)

        if found_user is None:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserProfileSerializer(found_user, context={"request": request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, username, format=None):
        user = request.user
        found_user = self.get_user(username)

        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        elif found_user.username != user.username:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = UserProfileSerializer(
                found_user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    def patch(self, request, username, format=None):
        user = request.user

        found_user = self.get_user(username)

        if found_user is None:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        elif found_user.username != user.username:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = UserProfileSerializer(
                found_user, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.update(instance=user)

                return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = get_object_or_404(User, email=request.user)
        serializer = UserProfileSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            serializer.instance = user
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Profile Updated Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )


class UserDetailView(RetrieveAPIView):
    lookup_field = "username"
    permission_classes = (AllowAny,)
    serializer_class = ListUserSerializer
    queryset = User.objects.all()


class UserDeleteView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, email):
        users = User.objects.filter(email=email)

        if users.exists():
            user = users.first()
            user.is_active = False
            user.is_deleted = True

            html_tpl_path = "email/delete.html"
            context_data = {"name": user.username}
            delete_html_template = get_template(html_tpl_path).render(context_data)

            data = {
                "email_body": delete_html_template,
                "to_email": user.email,
                "email_subject": "BlueMoon Account Deletion",
            }
            Util.send_email(data)

            user.save()
            return Response(
                {"status": True, "message": "Account has been deactivated."},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"status": False, "message": "User is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePassword(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, email, format=None):
        users = User.objects.filter(email=email)

        if not users.exists():
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = users.first()

        current_password = request.data.get("current_password")
        if current_password is None:
            return Response(
                {"status": False, "message": "You must enter your old password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        passwords_match = user.check_password(current_password)
        if not passwords_match:
            return Response(
                {"status": False, "message": "Incorrect Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = request.data.get("new_password")
        if new_password is None:
            return Response(
                {"status": False, "message": "New password must  not be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"status": True, "message": "Password changed succesfully"},
            status=status.HTTP_200_OK,
        )
