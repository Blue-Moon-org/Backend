from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from core.models import User, Feedback
from drf_extra_fields.fields import Base64ImageField


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    # default_error_messages = {
    #     "username": "The username should only contain alphanumeric characters"
    # }

    class Meta:
        model = User
        fields = [
            "email",
            # "username",
            "google",
            "phone",
            "password",
            "brand_name",
            "account_type",
            "firstname",
            "lastname",
        ]

    # def validate(self, attrs):
    #     username = attrs.get("username", "")
    #     if not username.isalnum():
    #         raise serializers.ValidationError(self.default_error_messages)
    #     return attrs

    def create(self, validated_data):
        ##print(validated_data)
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ("id", "title", "text", "user", "created_on")

class UserLessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "fullname", "image", "bio"]

class UserCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "followers_count", "following_count")

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {"bad_token": ("Token is expired or invalid")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail("bad_token")

class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)

    class Meta:
        fields = ["email", "password"]

    def validate(self, attrs):
        try:
            email = attrs.get("email")
            password = attrs.get("password")

            user = User.objects.filter(email=email).first()
            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed("User not found", 401)
        # return super().validate(attrs)

class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email", "")

        users = User.objects.filter(email=email)

        if not users.exists():
            raise AuthenticationFailed("User not found")
        
        user = users.first()

        if not user.is_active:
            raise AuthenticationFailed("Account has been disabled")
        return attrs

class VerifyOTPResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "otp", "username", "slug"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        otp = attrs.get("otp", "")

        users = User.objects.filter(email=email)

        if not users.exists():
            raise AuthenticationFailed("User not found")
        
        user = users.first()

        if not user.is_active:
            raise AuthenticationFailed("Account has been disabled")
        if user.otp != otp:
            raise AuthenticationFailed("The OTP Code is invalid")

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "slug": user.slug,
        }

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials, try again")
        if not user.is_active:
            raise AuthenticationFailed("Account has been disabled")

        return {"email": user.email, "tokens":user.tokens}

class VerifyOTPRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "otp", "tokens", "username", "slug"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        otp = attrs.get("otp", "")

        users = User.objects.filter(email=email)

        if not users.exists():
            raise AuthenticationFailed("User not found")
        
        user = users.first()
        refresh = RefreshToken.for_user(user=user)
        refresh_token = str(refresh)
        access_token = str(refresh.access_token)

        if not user.is_active:
            raise AuthenticationFailed("Account has been disabled")
        if user.otp != otp:
            raise AuthenticationFailed("The OTP Code is invalid")

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "slug": user.slug,
            # "tokens": user.tokens,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_self = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "fullname",
            "call_code",
            "phone",
            "bio",
            "sex",
            # "avatar",
            # "cover",
            "country",
            "state",
            "address",
            "city",
            "location",
            "day",
            "month",
            "year",
            "dob",
            "followers_count",
            "followers",
            "following_count",
            "following",
            "slug",
            "tos",
            "is_self",
            "created",
            "created_at",
        )

    def get_is_self(self, user):
        if "request" in self.context:
            request = self.context["request"]
            if user.id == request.user.id:
                return True
            else:
                return False
        return False

    def get_following(self, obj):
        if "request" in self.context:
            request = self.context["request"]
            if obj in request.user.following.all():
                return True
        return False

class ListUserSerializer(serializers.ModelSerializer):
    # avatar = Base64ImageField()
    # cover = Base64ImageField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            # "name",
            "call_code",
            "phone",
            "bio",
            "sex",
            # "avatar",
            # "cover",
            "country",
            "state",
            "address",
            "city",
            "location",
            "day",
            "month",
            "year",
            "dob",
            "otp",
            "followers_count",
            "followers",
            "following_count",
            "following",
            "is_verified",
            "is_active",
            "active",
            "is_staff",
            "is_admin",
            "is_banned",
            "slug",
            "tos",
            "tokens",
            "created",
            "created_at",
        )
        depth = 1
