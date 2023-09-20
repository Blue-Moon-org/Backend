from chat.views import get_user_contact
from .models import Chat,  Message
from rest_framework import serializers
from core.models import User



class ContactSerializer(serializers.ModelSerializer):
    # fullname = serializers.CharField('fullname')
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")

    class Meta:
        model = User
        fields = ('fullname','profile_pic')
        read_only_fields = ('id','fullname','profile_pic')

    def get_profile_pic(self, obj):
        return obj.image_url

class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ("content", "timestamp")


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)
    last_message = serializers.SerializerMethodField("get_last_message")

    class Meta:
        model = Chat
        fields = ('id', "room_name",'last_message', 'participants')
        read_only = ('id')

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