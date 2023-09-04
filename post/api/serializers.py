from rest_framework import serializers
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
    owner = serializers.ReadOnlyField(source="owner.nickname")
    likes = serializers.SerializerMethodField(method_name="get_likes")
    shares = serializers.SerializerMethodField(method_name="get_shares")
    favs = serializers.SerializerMethodField(method_name="get_favs")
    comments = serializers.SerializerMethodField(method_name="get_comments")
    no_comments = serializers.SerializerMethodField(method_name="get_no_comments")
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
            "likes",
            "shares",
            "favs",
            "no_comments",
            "images",
            "comments",
            "url",
        ]

        read_only_fields = [
            "likes",
        ]

    def get_likes(self, obj):
        return obj.likes.count()
    
    def get_shares(self, obj):
        return obj.shares.count()
    
    def get_favs(self, obj):
        return obj.favourite.count()

    def get_url(self, obj):
        return reverse("post-detail", kwargs={"pk": obj.pk})

    def get_comments(self, obj):
        return CommentSerializer(Comment.objects.filter(post=obj.id), many=True).data
    
    def get_no_comments(self, obj):
        return Comment.objects.filter(post=obj.id).count()
    
    def get_images(self, obj):
        return ImagesSerializer(Image.objects.filter(post=obj.id), many=True).data


class CategorySerializer(serializers.ModelSerializer):
    authur = serializers.ReadOnlyField(source="authur.fullname")

    class Meta:
        model = Category
        fields = ["id", "name", "authur"]


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")

    class Meta:
        model = Comment
        fields = ["id", "post", "body", "owner", "created"]

class ImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ["image"]