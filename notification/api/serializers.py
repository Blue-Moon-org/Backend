from rest_framework import serializers
from notification.models import Notification
from core.api.serializers import UserLessInfoSerializer


class NotificationSerializer(serializers.ModelSerializer):
    from_user = UserLessInfoSerializer()
    to_user = UserLessInfoSerializer()
    noti_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "from_user",
            "to_user",
            "noti_count",
            "notification_type",
            "comments",
            "user_has_seen",
            "created_time_ago",
        ]

    def get_noti_count(self, obj):
        count = self.context.get("noti_count")
        return count
