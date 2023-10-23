from chat.views import get_user_contact
from .models import Chat,  Message
from rest_framework import serializers
from core.models import User



class ContactSerializer(serializers.ModelSerializer):

    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    fullname = serializers.SerializerMethodField(method_name="get_fullname")

    class Meta:
        model = User
        fields = ('fullname','profile_pic')
        read_only_fields = ('id','fullname','profile_pic')

    def get_profile_pic(self, obj):
        if obj.account_type == "Designer":
            pic = obj.brand_image_url
        else:
             pic = obj.image_url

        return pic
    
    def get_fullname(self, obj):
        return obj.firstname + " " + obj.lastname

class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ("content", "timestamp")


class ChatSerializer(serializers.ModelSerializer):
    
    owner = serializers.SerializerMethodField(method_name="get_owner")
    other = serializers.SerializerMethodField(method_name="get_other")
    last_message = serializers.SerializerMethodField("get_last_message")

    class Meta:
        model = Chat
        fields = ('id', "room_name",'last_message', "owner", "other",)
        read_only = ('id')

    def get_owner(self, obj):
        request = self.context.get("request")
        data = ContactSerializer(User.objects.filter(id=request.user.id).first()).data
        return data
    
    def get_other(self, obj):
        request = self.context.get("request")
        data = ContactSerializer(User.objects.exclude(chats__participants=request.user.id).first()).data
        return data

    def create(self, validated_data):
        participants = validated_data.pop('participants')
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