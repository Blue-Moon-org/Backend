from django.db import models
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    DESIGNER = "Designer"
    BUYER = "Buyer"
    BOTH = "Both"

    TYPES = (
        (DESIGNER, "Designer"),
        (BUYER, "Buyer"),
        (BOTH, "Both"),
    )
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    stripe_charge_id = models.CharField(max_length=50, default="")
    image = models.ImageField(upload_to="profile/", blank=True, null=True)
    brand_image = models.ImageField(upload_to="brand/", blank=True, null=True)

    account_type = models.CharField(max_length=9, choices=TYPES, default=BUYER)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    phone = models.CharField(max_length=255, unique=True, null=False, blank=False)
    username = models.CharField(max_length=255, null=True, blank=True)
    brand_name = models.CharField(max_length=255, null=True, blank=True)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, null=True)
    sex = models.CharField(max_length=32, null=True, blank=True)

    call_code = models.CharField(max_length=500, null=True, blank=True)
    otp = models.IntegerField(blank=True, null=True, default=0)
    country = models.CharField(max_length=500, null=True, blank=True)
    region = models.CharField(max_length=500, null=True, blank=True)
    subregion = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=244, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    day = models.CharField(max_length=3, null=True, blank=True)
    month = models.CharField(max_length=15, null=True, blank=True)
    year = models.CharField(max_length=7, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    dob = models.CharField(max_length=255, null=True, blank=True)
    push_token = models.TextField(default="", blank=True, null=True)
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    followers = models.ManyToManyField(
        "self", related_name="user_followers", blank=True, symmetrical=False
    )
    following = models.ManyToManyField(
        "self", related_name="user_following", blank=True, symmetrical=False
    )
    users_notify = models.ManyToManyField(
        "self", related_name="notify", blank=True, symmetrical=False
    )
    users_blocked = models.ManyToManyField(
        "self", related_name="block", blank=True, symmetrical=False
    )
    friends = models.ManyToManyField("self", blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    google = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    tos = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created = models.CharField(max_length=255, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    @property
    def fullname(self):
        return self.firstname + " " + self.lastname

    def get_short_name(self):
        return self.firstname

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    @property
    def followers_count(self):
        return self.followers.all().count()

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        else:
            return ""

    @property
    def brand_image_url(self):
        if self.brand_image and hasattr(self.brand_image, "url"):
            return self.brand_image.url
        else:
            return ""

    @property
    def following_count(self):
        return self.following.all().count()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.email


class Feedback(models.Model):
    title = models.CharField(max_length=10000, blank=True, null=True)
    text = models.TextField(max_length=10000)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=True, null=True
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} gave feedback {self.title}"
