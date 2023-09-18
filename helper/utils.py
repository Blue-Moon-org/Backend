import random
import time
from django.core.mail import EmailMessage
from string import digits, ascii_lowercase, ascii_uppercase
from secrets import choice as secret_choice
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from random import choice as random_choice
import threading
import datetime
from django.http import HttpResponseForbidden
import uuid
from chat.models import Chat#, Contact

from core.models import User


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def slug_generator(
    size: int = 10, char: str = digits + ascii_uppercase + ascii_lowercase
) -> str:
    return "".join(random_choice(char) for _ in range(size))


def otp_generator(size: int = 6, char: str = digits) -> str:
    return "".join(secret_choice(char) for _ in range(size))


# def get_random_code():
#     code = str(uuid.uuid4())[:8].replace("-", " ").lower()
#     return code

# def get_last_10_messages(chatId):
#     chat = get_object_or_404(Chat, id=chatId)
#     return chat.messages.order_by('-timestamp').all()[:10]


# def get_user_contact(id):
#     user = get_object_or_404(User, id=id)
#     return user


# def get_current_chat(chatId):
#     return get_object_or_404(Chat, id=chatId)

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        email.content_subtype = "html"
        EmailThread(email).start()



DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 12


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'all_data': self.page.paginator.count,
                'page': int(self.request.GET.get('page', DEFAULT_PAGE)),
                'page_size': int(self.request.GET.get('page_size', self.page_size)),
                'next':self.get_next_link(),
                'previous':self.get_previous_link()
            }
        })

def get_timezone_datetime():
    current_date = datetime.datetime.now()
    current_date = current_date.\
        replace(tzinfo=datetime.timezone.utc)

    return current_date.isoformat()

def generate_transaction_id(user_id):
    # Get the current timestamp (in milliseconds)
    timestamp = int(time.time() * 1000)
    # Generate a random 4-digit number
    random_number = random.randint(1000, 9999)
    # Create a unique ID (e.g., user ID)
    unique_id = user_id  # Replace with the actual unique identifier
    # Combine the elements to create the transaction ID
    transaction_id = f"{unique_id}-{timestamp}-{random_number}"
    return transaction_id

def designer_required(view_func):
    """
    Decorator that allows only designer-type users to access the view.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and has the account_type set to "Designer"
        if request.user.is_authenticated and request.user.account_type == User.DESIGNER:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access Denied: Only designer-type users are allowed to access this page.")

    return _wrapped_view