from rest_framework import serializers
from core.api.serializers import UserLessInfoSerializer
from core.models import User
from post.models import Image
from post.models import Post, Category, Comment
from django.urls import reverse


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")
    url = serializers.SerializerMethodField(method_name="get_url")

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "owner",
            "created",
            "category",
            "url",
        ]

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})


class PostDetailSerializer(serializers.ModelSerializer):
    # owner = serializers.ReadOnlyField()
    
    likes = serializers.SerializerMethodField(method_name="get_likes")
    shares = serializers.SerializerMethodField(method_name="get_shares")
    favs = serializers.SerializerMethodField(method_name="get_favs")
    no_comments = serializers.SerializerMethodField(method_name="get_no_comments")
    url = serializers.SerializerMethodField(method_name="get_url")
    images = serializers.SerializerMethodField(method_name="get_images")
    owner = serializers.SerializerMethodField(method_name="get_owner")
    user_has_liked = serializers.SerializerMethodField(method_name="get_user_has_liked")
    user_has_favorited = serializers.SerializerMethodField(
        method_name="get_user_has_favorited"
    )  # New field
    user_has_shared = serializers.SerializerMethodField(
        method_name="get_user_has_shared"
    )  # New field

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "owner",
            "created",
            "category",
            "likes",
            "shares",
            "favs",
            "no_comments",
            "images",
            "url",
            "user_has_liked",
            "user_has_favorited",
            "user_has_shared",
        ]

        read_only_fields = [
            "likes",
            "shares",
            "favs",
            "user_has_liked",
            "user_has_favorited",
            "user_has_shared",
        ]

    def get_likes(self, obj):
        return obj.likes.count()

    def get_shares(self, obj):
        return obj.shares.count()

    def get_favs(self, obj):
        return obj.favourite.count()

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})

    def get_no_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()

    def get_images(self, obj):
        data = ImagesSerializer(Image.objects.filter(post=obj.id), many=True).data
        return data

    def get_owner(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(
            User.objects.filter(id=obj.owner.id).first(), context={"request": request}
        ).data
        return data

    def get_user_has_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        else:
            return False

    # New method to check if the current user has favorited the post
    def get_user_has_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favourite.filter(id=request.user.id).exists()
        else:
            return False

    # New method to check if the current user has shared the post
    def get_user_has_shared(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.shares.filter(id=request.user.id).exists()
        else:
            return False



class SearchPostDetailSerializer(serializers.ModelSerializer):
    # owner = serializers.ReadOnlyField()
    user = serializers.SerializerMethodField(method_name="get_user")
    
    likes = serializers.SerializerMethodField(method_name="get_likes")
    shares = serializers.SerializerMethodField(method_name="get_shares")
    favs = serializers.SerializerMethodField(method_name="get_favs")
    no_comments = serializers.SerializerMethodField(method_name="get_no_comments")
    url = serializers.SerializerMethodField(method_name="get_url")
    images = serializers.SerializerMethodField(method_name="get_images")
    owner = serializers.SerializerMethodField(method_name="get_owner")
    user_has_liked = serializers.SerializerMethodField(method_name="get_user_has_liked")
    user_has_favorited = serializers.SerializerMethodField(
        method_name="get_user_has_favorited"
    )  # New field
    user_has_shared = serializers.SerializerMethodField(
        method_name="get_user_has_shared"
    )  # New field

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "user",
            "owner",
            "created",
            "category",
            "likes",
            "shares",
            "favs",
            "no_comments",
            "images",
            "url",
            "user_has_liked",
            "user_has_favorited",
            "user_has_shared",
        ]

        read_only_fields = [
            "likes",
            "shares",
            "favs",
            "user_has_liked",
            "user_has_favorited",
            "user_has_shared",
        ]

    def get_user(self, obj):
        data = UserLessInfoSerializer(User.objects.filter(id=obj.owner.id).first()).data
        return data

    def get_likes(self, obj):
        return obj.likes.count()

    def get_shares(self, obj):
        return obj.shares.count()

    def get_favs(self, obj):
        return obj.favourite.count()

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})

    def get_no_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()

    def get_images(self, obj):
        data = ImagesSerializer(Image.objects.filter(post=obj.id), many=True).data
        return data

    def get_owner(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(
            User.objects.filter(id=obj.owner.id).first(), context={"request": request}
        ).data
        return data

    def get_user_has_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        else:
            return False

    # New method to check if the current user has favorited the post
    def get_user_has_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favourite.filter(id=request.user.id).exists()
        else:
            return False

    # New method to check if the current user has shared the post
    def get_user_has_shared(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.shares.filter(id=request.user.id).exists()
        else:
            return False

class UserPostDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")
    url = serializers.SerializerMethodField(method_name="get_url")
    images = serializers.SerializerMethodField(method_name="get_images")

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "owner",
            "created",
            "category",
            "images",
            "url",
        ]

    def get_images(self, obj):
        data = ImagesSerializer(Image.objects.filter(post=obj.id), many=True).data
        return data

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})


class CategorySerializer(serializers.ModelSerializer):
    authur = serializers.ReadOnlyField(source="authur.fullname")

    class Meta:
        model = Category
        fields = ["id", "name", "authur"]


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(method_name="get_owner")
    likes = serializers.SerializerMethodField(method_name="get_likes")
    user_has_liked = serializers.SerializerMethodField(method_name="get_user_has_liked")

    class Meta:
        model = Comment
        fields = ["id", "post", "body", "owner", "likes", "user_has_liked", "created"]
        read_only_fields = [
            "likes",
            "user_has_liked",
        ]

    def get_owner(self, obj):
        data = UserLessInfoSerializer(User.objects.filter(id=obj.owner.id).first()).data
        return data

    def get_user_has_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # print("User is in request")
            return obj.likes.filter(email=request.user.email).exists()
        else:
            return False

    def get_likes(self, obj):
        return obj.likes.count()


class CommentDetailSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(method_name="get_owner")
    likes = serializers.SerializerMethodField(method_name="get_likes")
    user_has_liked = serializers.SerializerMethodField(method_name="get_user_has_liked")

    class Meta:
        model = Comment
        fields = ["id", "body", "owner", "likes", "user_has_liked", "created"]
        read_only_fields = [
            "likes",
            "user_has_liked",
        ]

    def get_owner(self, obj):
        data = UserLessInfoSerializer(User.objects.filter(id=obj.owner.id).first()).data
        return data

    def get_likes(self, obj):
        return obj.likes.count()

    def get_user_has_liked(self, obj):
        request = self.context.get("request")
        # print(obj.likes.all(), request.user.is_authenticated)
        if request and request.user.is_authenticated:
            print("User exists")
            return obj.likes.filter(email=request.user.email).exists()
        else:
            return False


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image"]
