from rest_framework import serializers
from notification.models import Notification
from core.api.serializers import UserLessInfoSerializer
from post.api.serializers import CommentDetailSerializer, PostDetailSerializer
from post.models import Comment, Post
from product.api.serializers import LineItemIndexSerializer, ReviewSerializer
from product.models import LineItem, Review


class NotificationSerializer(serializers.ModelSerializer):
    # user = UserLessInfoSerializer()
    # owner = UserLessInfoSerializer()
    noti_count = serializers.SerializerMethodField(read_only=True)
    detail = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SerializerMethodField(method_name="get_owner")
    user = serializers.SerializerMethodField(method_name="get_user")


    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "owner",
            "noti_count",
            "notification_type",
            "comments",
            "user_has_seen",
            "created_time_ago",
            "detail",
        ]

    def get_noti_count(self, obj):
        count = self.context.get("noti_count")
        return count
    
    def get_owner(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(obj.owner, context={"request": request}).data
        return data
    
    def get_user(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(obj.user, context={"request": request}).data
        return data
    
    def get_detail(self, obj):
        request = self.context.get("request")
        obj_id = obj.object_id
        if obj_id:
            if obj.notification_type == "P":
                data = PostDetailSerializer(Post.objects.get(id=obj_id), context={"request": request}).data

            elif obj.notification_type == "C":
                data = CommentDetailSerializer(Comment.objects.get(id=obj_id), context={"request": request}).data

            elif obj.notification_type == "R":
                data = ReviewSerializer(Review.objects.get(id=obj_id), context={"request": request}).data
            elif obj.notification_type == "F":
                data = obj_id
            elif obj.notification_type == "NO":
                data = LineItemIndexSerializer(LineItem.objects.get(id=obj_id), context={"request": request}).data
            elif obj.notification_type == "UO":
                data = LineItemIndexSerializer(LineItem.objects.get(id=obj_id), context={"request": request}).data
        else:
            data = {}
        
        return data
