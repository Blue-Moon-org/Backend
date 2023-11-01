import random
import string
import time
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import User
from django.db import models


class Message(models.Model):
    MSG_TYPE_CHOICES = (
        ("image", "image"),
        ("text", "text"),
        ("measure", "measure"),
    )
    contact = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    # msg = models.JSONField(default=str, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    msg_type = models.CharField(max_length=12, choices=MSG_TYPE_CHOICES, default="text")

    def __str__(self):
        return self.contact.fullname


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats", blank=True)
    messages = models.ManyToManyField(Message, blank=True)
    room_name = models.CharField(max_length=50, unique=True)

    def generate_name(self):
        # Try to generate a unique room name
        while True:
            random_string = "".join(random.choices(string.ascii_lowercase, k=8))
            timestamp = str(int(time.time()))
            unique_name = f"room_{timestamp}_{random_string}"
            # Check if the generated room name is unique
            if not Chat.objects.filter(room_name=unique_name).exists():
                return unique_name

    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = self.generate_name()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.room_name


class ImageMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image_messages/")

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        else:
            return ""


# def user_post_save(sender, instance, *arg, **kwargs):

#     if not Contact.objects.filter(user=instance).exists():
#         Contact.objects.create(user=instance)

# post_save.connect(user_post_save, sender=User)

# class Chatroom(Model): # Chatroom == Group == one-to-one | on-to-many users

#     TYPE_CHOICES = (
#             ('W', 'Waiting'),
#             ('G', 'Granted'),
#             ('D', 'Denied'),
#         )

#     name = CharField(max_length=150)
#     users = ManyToManyField(User, related_name='recipients')
#     created_at = DateTimeField(auto_now_add=True)
#     updated_at = DateTimeField(auto_now=True)
#     permission = models.CharField(max_length=32, choices=TYPE_CHOICES, default="W")

#     def __str__(self):
#         return str(self.id)


# class Request(Model):
#     class PermissionsTypes(models.TextChoices):
#         WAITING = 'waiting', _("Waiting")
#         GRANTED = 'granted', _('Granted')
#         DENIED = 'denied', _("Denied")

#     user = ForeignKey(User, related_name='request_owner', on_delete=CASCADE)
#     chatroom = ForeignKey(Chatroom, related_name='request_target', on_delete=CASCADE)
#     permission = models.CharField(max_length=32, choices=PermissionsTypes.choices, default=PermissionsTypes.WAITING)


# class Message(Model):
#     user = ForeignKey(User, on_delete=CASCADE, verbose_name='user', related_name='from_user')
#     chatroom = ForeignKey(Chatroom, on_delete=CASCADE, verbose_name='chatroom', related_name='chatroom')
#     created_at = DateTimeField(auto_now_add=True)
#     updated_at = DateTimeField(auto_now=True)
#     body = TextField(max_length=2000)

#     def __str__(self):
#         return str(self.id)

#     def characters(self):
#         return len(self.body)

#     def notify_ws_clients(self):
#         """
#         Inform client there is a new message.
#         """
#         notification = {
#             'type': 'recieve_group_message',
#             'message': f'{self.id}'
#         }

#         channel_layer = get_channel_layer()
#         print("user.id {}".format(self.user.id))

#         async_to_sync(channel_layer.group_send)(f"{self.user.id}", notification)
#         #async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)

#     def save(self, *args, **kwargs):
#         """
#         Trims white spaces, saves the message and notifies the recipient via WS
#         if the message is new.
#         """
#         new = self.id
#         self.body = self.body.strip()  # Trimming whitespaces from the body
#         super(Message, self).save(*args, **kwargs)
#         if new is None:
#             self.notify_ws_clients()
