from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from django.shortcuts import get_object_or_404
from chat.models import Chat, Message

from core.models import User


def get_user_contact(id):
    user = get_object_or_404(User, id=id)
    return user

def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:10]


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)

class ChatConsumer(WebsocketConsumer):


    def user_online(self, data):
        # Update the user's online status to True
        user = get_user_contact(data['from'])
        user.is_online = True
        user.save()

        # Notify other users that this user is online
        self.notify_user_online(user)

    def user_offline(self, data):
        # Update the user's online status to False
        user = get_user_contact(data['from'])
        user.is_online = False
        user.save()

        # Notify other users that this user is offline
        self.notify_user_offline(user)

    def user_typing(self, data):
        # Notify other users that this user is typing
        sender = get_user_contact(data['from'])
        chatroom = get_current_chat(data['chatId'])
        content = {
            'command': 'typing',
            'user': sender.fullname,
        }
        self.send_chat_message(chatroom, content)

    def notify_user_online(self, user):
        # Notify other users that this user is online
        content = {
            'command': 'online',
            'user': user.fullname,
        }
        self.broadcast_to_chatroom(user.username, content)

    def notify_user_offline(self, user):
        # Notify other users that this user is offline
        content = {
            'command': 'offline',
            'user': user.fullname,
        }
        return self.send_chat_message(content)
        
    def initiate_call(self, data):
        # Extract necessary information from the data
        caller = get_user_contact(data['from'])
        recipient_username = data['to']

        # Create a call request message
        content = {
            'command': 'initiate_call',
            'caller': caller.fullname,
            'recipient': recipient_username,
        }

        # Send the call request to the recipient
        self.send_chat_message(recipient_username, content)

    def accept_call(self, data):
        # Extract necessary information from the data
        callee = get_user_contact(data['from'])
        caller_username = data['caller']

        # Create a call accepted response
        content = {
            'command': 'accept_call',
            'callee': callee.fullname,
        }

        # Send the call accepted response to the caller
        self.send_chat_message(caller_username, content)

    def reject_call(self, data):
        # Extract necessary information from the data
        callee = get_user_contact(data['from'])
        caller_username = data['caller']

        # Create a call rejected response
        content = {
            'command': 'reject_call',
            'callee': callee.fullname,
        }

        # Send the call rejected response to the caller
        self.send_chat_message(caller_username, content)

    def fetch_messages(self, data):
        messages = get_last_10_messages(data['chatId'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        user_contact = get_user_contact(data['from'])
        message = Message.objects.create(
            contact=user_contact,
            content=data['message'])
        current_chat = get_current_chat(data['chatId'])
        current_chat.messages.add(message)
        current_chat.save()
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'id': message.id,
            'author': message.contact.fullname,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'initiate_call': initiate_call,
        'accept_call': accept_call,
        'reject_call': reject_call,
        'online': user_online,
        'offline': user_offline,
        'typing': user_typing,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        #print(text_data)
        data = json.loads(text_data)        
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))








# from channels.generic.websocket import WebsocketConsumer
# import json
# from django.shortcuts import get_object_or_404
# from core.models import User
# from fixchat.models import Message, Chatroom
# from fixchat.serializers import ChatMessageSerializer
# from asgiref.sync import async_to_sync


# def get_user(username):
#     return get_object_or_404(User, username=username)


# def get_current_chat(chatId):
#     return get_object_or_404(Chatroom, id=chatId)

# class ChatConsumer(WebsocketConsumer):

#     # def fetch_messages(self, data):
#     #     messages = get_last_10_messages(data['chatId'])
#     #     content = {
#     #         'command': 'messages',
#     #         'messages': self.messages_to_json(messages)
#     #     }
#     #     self.send_message(content)

#     def user_online(self, data):
#         # Update the user's online status to True
#         user = get_user(data['from'])
#         user.is_online = True
#         user.save()

#         # Notify other users that this user is online
#         self.notify_user_online(user)

#     def user_offline(self, data):
#         # Update the user's online status to False
#         user = get_user(data['from'])
#         user.is_online = False
#         user.save()

#         # Notify other users that this user is offline
#         self.notify_user_offline(user)

#     def user_typing(self, data):
#         # Notify other users that this user is typing
#         sender = get_user(data['from'])
#         chatroom = get_current_chat(data['chatId'])
#         content = {
#             'command': 'typing',
#             'user': sender.username,
#         }
#         self.send_chat_message(chatroom, content)

#     def notify_user_online(self, user):
#         # Notify other users that this user is online
#         content = {
#             'command': 'online',
#             'user': user.username,
#         }
#         self.broadcast_to_chatroom(user.username, content)

#     def notify_user_offline(self, user):
#         # Notify other users that this user is offline
#         content = {
#             'command': 'offline',
#             'user': user.username,
#         }
#         return self.send_chat_message(content)
        
#     def initiate_call(self, data):
#         # Extract necessary information from the data
#         caller = get_user(data['from'])
#         recipient_username = data['to']

#         # Create a call request message
#         content = {
#             'command': 'initiate_call',
#             'caller': caller.username,
#             'recipient': recipient_username,
#         }

#         # Send the call request to the recipient
#         self.send_chat_message(recipient_username, content)

#     def accept_call(self, data):
#         # Extract necessary information from the data
#         callee = get_user(data['from'])
#         caller_username = data['caller']

#         # Create a call accepted response
#         content = {
#             'command': 'accept_call',
#             'callee': callee.username,
#         }

#         # Send the call accepted response to the caller
#         self.send_chat_message(caller_username, content)

#     def reject_call(self, data):
#         # Extract necessary information from the data
#         callee = get_user(data['from'])
#         caller_username = data['caller']

#         # Create a call rejected response
#         content = {
#             'command': 'reject_call',
#             'callee': callee.username,
#         }

#         # Send the call rejected response to the caller
#         self.send_chat_message(caller_username, content)

#     def new_message(self, data):
#         user = get_user(data['from'])
#         chat = get_current_chat(data['chatId'])        
#         message = Message.objects.create(
#             user=user,
#             body=data['message'], 
#             chatroom=chat)
       
#         message.save()
#         content = {
#             'command': 'new_message',
#             'message': ChatMessageSerializer(message).data
#         }
#         return self.send_chat_message(content)

#     commands = {
#        # 'fetch_messages': fetch_messages,
#         'new_message': new_message,
#         'initiate_call': initiate_call,
#         'accept_call': accept_call,
#         'reject_call': reject_call,
#         'online': user_online,
#         'offline': user_offline,
#         'typing': user_typing,
#     }

#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_id']
#         self.group_name = f"chat_{self.room_name}"

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.group_name,
#             self.channel_name
#         )
#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data=None, bytes_data=None):

#         ## data --> chatId, from, message, commend
#         data = json.loads(text_data)
#         self.commands[data['command']](self, data)

#     def recieve_group_message(self, event):
#         message = event['message']

#         # Send message to WebSocket
#         self.send(
#              text_data=json.dumps({
#             'message': message
#         }))
    
#     def send_chat_message(self, message):
#         async_to_sync(self.channel_layer.group_send)(
#             self.group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     def send_message(self, message):
#         self.send(text_data=json.dumps(message))

#     def chat_message(self, event):
#         message = event['message']
#         self.send(text_data=json.dumps(message))