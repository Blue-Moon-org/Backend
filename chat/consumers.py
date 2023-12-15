import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from django.shortcuts import get_object_or_404
from chat.models import Chat, Message
from chat.serializers import ChatListSerializer

from core.models import User

log = logging.getLogger(__name__)


def get_user_contact(id):
    user = get_object_or_404(User, id=id)
    return user


def get_last_messages(chatId, more=False, last_message_id=None):
    chat = get_object_or_404(Chat, id=chatId)
    # Set the number of messages to retrieve based on whether more is True or False
    if more:
        num_messages = 50  # Retrieve 50 messages when more is True
    else:
        num_messages = 75  # Retrieve the last 75 messages by default

    # Query the messages
    messages = chat.messages.order_by("-timestamp").all()

    if last_message_id:
        # Filter messages older than the last_message_id
        messages = messages.filter(id__lt=last_message_id)

    # Retrieve the specified number of messages
    messages = messages[:num_messages]

    return messages


def get_last_10_messages(chatId, more=False):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by("-timestamp").all()[:75]


def get_last_message(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by("-timestamp").all()[:1]


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)


class ChatConsumer(WebsocketConsumer):
    def user_online(self, data):
        # Update the user's online status to True
        user = get_user_contact(data["from"])
        user.is_online = True
        user.save()

        # Notify other users that this user is online
        self.notify_user_online(user)

    def user_offline(self, data):
        # Update the user's online status to False
        user = get_user_contact(data["from"])
        user.is_online = False
        user.save()

        # Notify other users that this user is offline
        self.notify_user_offline(user)

    def user_typing(self, data):
        # Notify other users that this user is typing
        sender = get_user_contact(data["from"])
        chatroom = get_current_chat(data["chatId"])
        content = {
            "command": "typing",
            "user": sender.fullname,
        }
        self.send_chat_message(chatroom, content)

    def notify_user_online(self, user):
        # Notify other users that this user is online
        content = {
            "command": "online",
            "user": user.fullname,
        }
        self.broadcast_to_chatroom(user.username, content)

    def notify_user_offline(self, user):
        # Notify other users that this user is offline
        content = {
            "command": "offline",
            "user": user.fullname,
        }
        return self.send_chat_message(content)

    def initiate_call(self, data):
        # Extract necessary information from the data
        caller = get_user_contact(data["from"])
        recipient_username = data["to"]

        # Create a call request message
        content = {
            "command": "initiate_call",
            "caller": caller.fullname,
            "recipient": recipient_username,
        }

        # Send the call request to the recipient
        self.send_chat_message(recipient_username, content)

    def accept_call(self, data):
        # Extract necessary information from the data
        callee = get_user_contact(data["from"])
        caller_username = data["caller"]

        # Create a call accepted response
        content = {
            "command": "accept_call",
            "callee": callee.fullname,
        }

        # Send the call accepted response to the caller
        self.send_chat_message(caller_username, content)

    def reject_call(self, data):
        # Extract necessary information from the data
        callee = get_user_contact(data["from"])
        caller_username = data["caller"]

        # Create a call rejected response
        content = {
            "command": "reject_call",
            "callee": callee.fullname,
        }

        # Send the call rejected response to the caller
        self.send_chat_message(caller_username, content)

    def fetch_messages(self, data):
        messages = get_last_10_messages(data["chatId"])
        content = {"command": "messages", "messages": self.messages_to_json(messages)}
        self.send_message(content)

    def new_message(self, data):
        user_contact = get_user_contact(data["from"])
        message = Message.objects.create(
            contact=user_contact, content=data["message"], msg_type=data["msg_type"]
        )
        current_chat = get_current_chat(data["chatId"])
        current_chat.messages.add(message)
        current_chat.save()
        content = {"command": "new_message", "message": self.message_to_json(message)}
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        msg_type = message.msg_type
        if msg_type == "measure":
            data = {
                "id": message.id,
                "author": message.contact.fullname,
                "content": json.loads(message.content),
                "msg_type": message.msg_type,
                "timestamp": str(message.timestamp),
            }

        else:
            data = {
                "id": message.id,
                "author": message.contact.fullname,
                "content": message.content,
                "msg_type": message.msg_type,
                "timestamp": str(message.timestamp),
            }
        return data

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
        "initiate_call": initiate_call,
        "accept_call": accept_call,
        "reject_call": reject_call,
        "online": user_online,
        "offline": user_offline,
        "typing": user_typing,
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        # print(text_data)
        data = json.loads(text_data)
        # Check for the 'msg_type' field in the incoming message data
        msg_type = data.get("msg_type", "text")

        # Call the appropriate handler based on the 'msg_type'
        if msg_type == "measure":
            data["message"] = json.dumps(data["message"])
            self.commands[data["command"]](self, data)
        else:
            self.commands[data["command"]](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))


class NewChatConsumer(WebsocketConsumer):
    def user_online(self, data):
        # Update the user's online status to True
        user = get_user_contact(data["from"])
        user.is_online = True
        user.save()
        # Notify other users that this user is online
        content = {
            "command": "user_online",
            "room_name": data["room_name"],
            "message": f"{user.fullname} is online",
        }
        return self.send_chat_message(content)

    def user_offline(self, data):
        # Update the user's online status to False
        user = get_user_contact(data["from"])
        user.is_online = False
        user.save()

        # Notify other users that this user is offline
        self.notify_user_offline(user)

    def typing(self, data):
        # Notify other users that this user is typing
        sender = get_user_contact(data["from"])
        chatroom = get_current_chat(data["chatId"])
        content = {
            "command": "typing",
            "user": f"{sender.fullname} is typing",
            "room_name": data["room_name"],
        }
        self.send_chat_message(chatroom, content)

    def notify_user_online(self, user):
        # def notify_user_offline(self, user):
        # Notify other users that this user is offline
        content = {
            "command": "offline",
            "user": user.fullname,
        }
        return self.send_chat_message(content)

    def initiate_call(self, data):
        # Extract necessary information from the data
        caller = get_user_contact(data["from"])
        recipient_username = data["to"]

        # Create a call request message
        content = {
            "command": "initiate_call",
            "caller": caller.fullname,
            "recipient": recipient_username,
            "room_name": data["room_name"],
        }

        # Send the call request to the recipient
        self.send_chat_message(recipient_username, content)

    def accept_call(self, data):
        # Extract necessary information from the data
        callee = get_user_contact(data["from"])
        caller_username = data["caller"]

        # Create a call accepted response
        content = {
            "command": "accept_call",
            "callee": callee.fullname,
            "room_name": data["room_name"],
        }

        # Send the call accepted response to the caller
        self.send_chat_message(caller_username, content)

    def reject_call(self, data):
        # Extract necessary information from the data
        callee = get_user_contact(data["from"])
        caller_username = data["caller"]

        # Create a call rejected response
        content = {
            "command": "reject_call",
            "callee": callee.fullname,
            "room_name": data["room_name"],
        }

        # Send the call rejected response to the caller
        self.send_chat_message(caller_username, content)

    def fetch_messages(self, data):

        more = data.get("more", False)
        last_id = data.get("last_id", None)
        messages = get_last_messages(data["chatId"], more=more, last_message_id=last_id)
        content = {
            "command": "messages",
            "messages": self.messages_to_json(messages),
            "room_name": data["room_name"],
        }
        self.send_message(content)

    def more_messages(self, data):
        messages = get_last_10_messages(data["chatId"])
        content = {
            "command": "messages",
            "messages": self.messages_to_json(messages),
            "room_name": data["room_name"],
        }
        self.send_message(content)
        

    def chat_list(self, data):
        contact = get_user_contact(self.room_name)

        chats = ChatListSerializer(
            contact.chats.all(),
            context={"user": contact},
            many=True,
        )

        log.info(chats.data[0].keys())
        # sorted_messages = sorted(
        #     chats.data, key=lambda x: x['last_message']['timestamp'], reverse=True
        # )
        content = {
            "command": "chat_list",
            "messages": chats.data,
        }
        self.send_message(content)

    def last_message(self, data):
        messages = get_last_message(data["chatId"])
        content = {
            "command": "last_message",
            "messages": self.messages_to_json(messages, room_name=data["room_name"]),
            "room_name": data["room_name"],
        }
        self.send_message(content)

    def new_message(self, data):
        user_contact = get_user_contact(data["from"])
        message = Message.objects.create(
            contact=user_contact, content=data["message"], msg_type=data["msg_type"]
        )
        current_chat = get_current_chat(data["chatId"])
        current_chat.messages.add(message)
        current_chat.save()
        content = {
            "command": "new_message",
            "message": self.message_to_json(message, data["room_name"]),
            "room_name": data["room_name"],
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages, room_name=None):
        result = []
        for message in messages:
            result.append(self.message_to_json(message, room_name))
        return result

    def message_to_json(self, message, room_name=None):
        msg_type = message.msg_type
        if msg_type == "measure" or msg_type == "image":
            data = {
                "id": message.id,
                "author": message.contact.fullname,
                "content": json.loads(message.content),
                "msg_type": message.msg_type,
                "timestamp": str(message.timestamp),
                "room_name": room_name,
            }

        else:
            data = {
                "id": message.id,
                "author": message.contact.fullname,
                "content": message.content,
                "msg_type": message.msg_type,
                "timestamp": str(message.timestamp),
                "room_name": room_name,
            }
        return data

    commands = {
        "fetch_messages": fetch_messages,
        # "more_messages": more_messages,
        "chat_list": chat_list,
        "last_message": last_message,
        "new_message": new_message,
        "initiate_call": initiate_call,
        "accept_call": accept_call,
        "reject_call": reject_call,
        "online": user_online,
        "offline": user_offline,
        "typing": typing,
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["id"]
        users = get_object_or_404(User, id=self.room_name).users_blocked.all()
        rooms = Chat.objects.filter(participants=self.room_name).exclude(participants__in=users)
        print(rooms)
        if rooms.exists():
            for room in rooms:
                room_group_name = f"chat_{room.room_name}"
                async_to_sync(self.channel_layer.group_add)(
                    room_group_name, self.channel_name
                )
        self.accept()

    def disconnect(self, close_code):
        pass
        # async_to_sync(self.channel_layer.group_discard)(
        #     self.room_group_name,
        #     self.channel_name
        # )

    def receive(self, text_data):
        # print(text_data)
        data = json.loads(text_data)
        # Check for the 'msg_type' field in the incoming message data
        msg_type = data.get("msg_type", "text")

        # Call the appropriate handler based on the 'msg_type'
        if msg_type == "measure" or msg_type == "image":
            data["message"] = json.dumps(data["message"])
            self.commands[data["command"]](self, data)

        else:
            self.commands[data["command"]](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            f"chat_{message['room_name']}", {"type": "chat_message", "message": message}
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event["message"]
        msg = message.copy()
        msg["command"] = "incoming-message"
        self.send(text_data=json.dumps(message))
        self.send(text_data=json.dumps(msg))
