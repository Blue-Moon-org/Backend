import random
from datetime import date

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import get_template

from core.models import User, Feedback
from notification.models import Notification
from .serializers import (
    ListUserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LogoutSerializer,
    LoginSerializer,
    VerifyOTPRegisterSerializer,
    FeedbackSerializer,
    SetNewPasswordSerializer,
    ResetPasswordSerializer,
)
from core.email import *
from rest_framework import generics, status, permissions
from rest_framework.generics import (
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from helper.utils import Util


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        user_data = {}

        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data
            otp = random.randint(100000, 999999)
            user = User.objects.get(email=user_data["email"])
            print(otp)
            user.otp = otp
            now = date.today()
            user.day = now.day
            user.month = now.month
            user.year = now.year
            user.is_active = True

            user_data["email"] = user.email
            user_data["username"] = user.username
            user_data["phone"] = user.phone
            html_tpl_path = "email/welcome.html"
            html_intro_path = "email/intro.html"
            context_data = {"name": user.username, "code": user.otp}
            email_html_template = get_template(html_tpl_path).render(context_data)
            intro_html_template = get_template(html_intro_path).render(context_data)
            data = {
                "email_body": email_html_template,
                "to_email": user.email,
                "email_subject": "Please verify your BlueMoon email",
            }
            intro = {
                "email_body": intro_html_template,
                "to_email": user.email,
                "email_subject": "Welcome To BlueMoon",
            }
            Util.send_email(data)
            Util.send_email(intro)
            user.save()
            return Response(user_data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyEmail(generics.GenericAPIView):
    serializer_class = VerifyOTPRegisterSerializer
    permission_classes = (permissions.AllowAny,)

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
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = User.objects.get(email=user_data["email"])
        if user.is_active:
            html_tpl_path = "email/login.html"
            context_data = {"name": user.username, "code": user.otp}
            email_html_template = get_template(html_tpl_path).render(context_data)
            data = {
                "email_body": email_html_template,
                "to_email": user.email,
                "email_subject": "BlueMoon login verification",
            }

            Util.send_email(data)
            return Response(
                {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"status": False, "message": "User is not active"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        user_data = serializer.data
        user = User.objects.filter(email=user_data["email"]).first()
        if user and user.is_active:
            # otp = random.randint(100000, 999999)
            # user.otp = otp
            user.save()
            html_tpl_path = "email/reset.html"
            context_data = {"name": user.username
                            # , "code": user.otp
                            }
            email_html_template = get_template(html_tpl_path).render(context_data)
            data = {
                "email_body": email_html_template,
                "to_email": user.email,
                "email_subject": "BlueMoon reset password verification",
            }

            Util.send_email(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    permission_classes = (permissions.AllowAny,)

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset successful"},
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
    permission_classes = (AllowAny,)
    serializer_class = ListUserSerializer

    def get(self, request, username, format=None):
        try:
            found_user = User.objects.get(username=username)
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
    def get(self, request, username, format=None):
        try:
            found_user = User.objects.get(username=username)
            print(f"found user {found_user}")
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_following = found_user.following.all()
        serializer = ListUserSerializer(
            user_following, many=True, context={"request": request}
        )

        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def follow_unfollow_user(request):
    if request.method == "POST":
        username = request.data.get("username")
        fu_user = get_object_or_404(User, username=username)
        user = request.user

        if fu_user in user.following.all():
            following = False
            user.following.remove(fu_user)
            user.save()
            fu_user.followers.remove(user)
            fu_user.save()

            Notification.objects.get_or_create(
                notification_type="UF",
                comments=(f"@{user.username} unfollowed you"),
                to_user=fu_user,
                from_user=user,
            )
        else:
            following = True
            user.following.add(fu_user)
            user.save()
            fu_user.followers.add(user)
            fu_user.save()

            Notification.objects.get_or_create(
                notification_type="F",
                comments=(f"@{user.username} followed you"),
                to_user=fu_user,
                from_user=user,
            )
        return Response(
            {
                "following": following,
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes((AllowAny,))
def user_followed_user(request):
    if request.method == "POST":
        username = request.data.get("username")
        fu_user = get_object_or_404(User, username=username)
        user = request.user
        if user in fu_user.followers.all():
            following = True
        else:
            following = False
        return Response(
            {
                "following": following,
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfile(APIView):
    ##permission_classes = (permissions.AllowAny,)
    def get_user(self, username):
        try:
            found_user = User.objects.get(username=username)
            return found_user
        except User.DoesNotExist:
            return None

    def get(self, request, username, format=None):
        found_user = self.get_user(username)

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


class UserDetailView(RetrieveAPIView):
    lookup_field = "username"
    permission_classes = (AllowAny,)
    serializer_class = ListUserSerializer
    queryset = User.objects.all()


class UserUpdateView(UpdateAPIView):
    lookup_field = "username"
    permission_classes = (AllowAny,)
    serializer_class = ListUserSerializer
    queryset = User.objects.all()
    parser_classes = (FormParser, MultiPartParser)


class UserDeleteView(DestroyAPIView):
    lookup_field = "username"
    permission_classes = (AllowAny,)
    serializer_class = ListUserSerializer
    queryset = User.objects.all()


class ChangePassword(APIView):
    def put(self, request, username, format=None):
        user = request.user

        if user.username == username:
            current_password = request.data.get("current_password", None)

            if current_password is not None:
                passwords_match = user.check_password(current_password)

                if passwords_match:
                    new_password = request.data.get("new_password", None)

                    if new_password is not None:
                        user.set_password(new_password)

                        user.save()

                        return Response(status=status.HTTP_200_OK)

                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)