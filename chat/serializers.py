import datetime
from chat.views import get_user_contact
from product.models import LineItem
from .models import Chat, Message
from rest_framework import serializers
from core.models import User
import json


class ContactListSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    fullname = serializers.SerializerMethodField(method_name="get_fullname")
    owner = serializers.SerializerMethodField(method_name="get_owner")

    class Meta:
        model = User
        fields = ("id","fullname", "profile_pic", "owner")
        # read_only_fields = ('id','fullname','profile_pic')

    def get_profile_pic(self, obj):
        if obj.account_type == "Designer":
            pic = obj.brand_image_url
        else:
            pic = obj.image_url
        return pic

    def get_fullname(self, obj):
        return f"{obj.firstname} {obj.lastname}"

    def get_owner(self, obj):
        user = self.context.get("user")
        return obj == user


class ContactSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    fullname = serializers.SerializerMethodField(method_name="get_fullname")
    owner = serializers.SerializerMethodField(method_name="get_owner")

    class Meta:
        model = User
        fields = ("fullname", "profile_pic", "owner")
        # read_only_fields = ('id','fullname','profile_pic')

    def get_profile_pic(self, obj):
        if obj.account_type == "Designer":
            pic = obj.brand_image_url
        else:
            pic = obj.image_url
        return pic

    def get_fullname(self, obj):
        return f"{obj.firstname} {obj.lastname}"

    def get_owner(self, obj):
        request = self.context.get("request")
        return obj == request.user


class ChatMessageSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField("get_content")

    class Meta:
        model = Message
        fields = ("content", "msg_type", "timestamp")

    def get_content(self, obj):
        if obj.msg_type == "measure" or obj.msg_type == "image":
            return json.loads(obj.content)
        else:
            return obj.content


class ChatSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField(method_name="get_participants")
    last_message = serializers.SerializerMethodField("get_last_message")
    is_blocked = serializers.SerializerMethodField("get_is_blocked")
    can_block = serializers.SerializerMethodField("get_can_block")

    class Meta:
        model = Chat
        fields = (
            "id",
            "room_name",
            "is_blocked",
            "can_block",
            "last_message",
            "participants",
        )
        read_only = "id"

    def get_participants(self, obj):
        request = self.context.get("request")
        data = ContactSerializer(
            obj.participants, context={"request": request}, many=True
        ).data

        return data

    def create(self, validated_data):
        participants = validated_data.pop("participants")
        chat = Chat()
        chat.save()
        for nickname in participants:
            user = get_user_contact(nickname)
            chat.participants.add(user)
        chat.save()
        return chat

    def get_last_message(self, obj):
        if len(list(obj.messages.all())) < 1:
            return {}
        return ChatMessageSerializer(list(obj.messages.all())[-1]).data

    def get_is_blocked(self, obj):
        request = self.context.get("request")
        other = obj.participants.exclude(id=request.user.id).first()
        return other.users_blocked.filter(id=request.user.id).exists()

    def get_can_block(self, obj):
        request = self.context.get("request")
        other = obj.participants.exclude(id=request.user.id).first()
        exist = LineItem.objects.filter(
            user__in=[request.user, other], seller__in=[request.user, other]
        ).exists()
        return not exist


class ChatListSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField(method_name="get_participants")
    last_message = serializers.SerializerMethodField("get_last_message")
    is_blocked = serializers.SerializerMethodField("get_is_blocked")
    active_order = serializers.SerializerMethodField("get_active_order")

    class Meta:
        model = Chat
        fields = (
            "id",
            "room_name",
            "active_order",
            "is_blocked",
            "last_message",
            "participants",
        )
        read_only = "id"

    def get_participants(self, obj):
        user = self.context.get("user")
        data = ContactListSerializer(
            obj.participants, context={"user": user}, many=True
        ).data
        return data

    def create(self, validated_data):
        participants = validated_data.pop("participants")
        chat = Chat()
        chat.save()
        for nickname in participants:
            user = get_user_contact(nickname)
            chat.participants.add(user)
        chat.save()
        return chat

    def get_last_message(self, obj):
        if len(list(obj.messages.all())) < 1:
            return {}
        return ChatMessageSerializer(list(obj.messages.all())[-1]).data

    def get_is_blocked(self, obj):
        user = self.context.get("user")
        other = obj.participants.exclude(id=user.id).first()
        val = other.users_blocked.filter(id=user.id).exists() if other else False
        return val

    def get_active_order(self, obj):
        user = self.context.get("user")
        other = obj.participants.exclude(id=user.id).first()
        exist = LineItem.objects.filter(
            user__in=[user, other], seller__in=[user, other]
        ).exists()
        return not exist


# class UserMessageSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ['username', 'avatar', 'name']


# class ChatroomSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Chatroom
#         fields = ['id', 'name']

#     def to_representation(self, instance):

#         data = super(ChatroomSerializer, self).to_representation(instance)
#         return data#['name']

#     def create(self, validated_data):
#         users = validated_data.pop('users')
#         chat = Chatroom()
#         chat.save()
#         for user in users:
#             user = User.objects.get(username=user)
#             chat.users.add(user)
#         chat.save()
#         return chat

# class RequestSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Request
#         fields = '__all__'


# class ChatMessageSerializer(serializers.ModelSerializer):
#     chatroom = ChatroomSerializer(read_only=True)
#     user = UserMessageSerializer(read_only=True)

#     class Meta:
#         model = Message
#         fields = ['id', 'chatroom', 'user', 'body', 'created_at']
