import random
import string
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
from chat.models import Chat  # , Contact
from django.utils import timezone
from core.models import User
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from firebase_admin import messaging


CATEGORY = (
    ("Men", "Men"),
    ("Women", "Women"),
    ("Native", "Native"),
    ("Ankara", "Ankara"),
)


def pluralize(value, unit):
    if value == 1:
        return f"1{unit}"
    return f"{value}{unit}"


def time_ago(dt):
    t = timezone.now() - dt
    if t.days == 0:
        if t.seconds < 60:
            return "just now"
        if t.seconds < 3600:
            return pluralize(t.seconds // 60, "m")
        if t.seconds < 3600 * 24:
            return pluralize(t.seconds // 3600, "h")
    if t.days < 30:
        return pluralize(t.days, "d")
    if t.days < 365:
        return pluralize(t.days // 30, "mo")
    return pluralize(t.days // 365, "yr")


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def gen_tracking_number(LineItem):
    # Define the length of the tracking number
    length = 15
    while True:
        # Generate a random tracking number with uppercase letters and digits
        tracking_number = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=length)
        )

        # Check if the generated tracking number already exists in the database
        if not LineItem.objects.filter(tracking_number=tracking_number).exists():
            return tracking_number


def slug_generator(
    size: int = 10, char: str = digits + ascii_uppercase + ascii_lowercase
) -> str:
    return "".join(random_choice(char) for _ in range(size))


def otp_generator(size: int = 6, char: str = digits) -> str:
    return "".join(secret_choice(char) for _ in range(size))


def get_random_code():
    code = str(uuid.uuid4())[:8].replace("-", " ").lower()
    return code


def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by("-timestamp").all()[:10]


def get_user_contact(id):
    user = get_object_or_404(User, id=id)
    return user


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)


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
DEFAULT_PAGE_SIZE = 18


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "meta": {
                    "all_data": self.page.paginator.count,
                    "page": int(self.request.GET.get("page", DEFAULT_PAGE)),
                    "page_size": int(self.request.GET.get("page_size", self.page_size)),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
            }
        )


def get_timezone_datetime():
    current_date = datetime.datetime.now()
    current_date = current_date.replace(tzinfo=datetime.timezone.utc)

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
            return HttpResponseForbidden(
                "Access Denied: Only designer-type users are allowed to access this page."
            )

    return _wrapped_view


# Define a TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()
from post.models import Post
# Create a TF-IDF matrix for all posts
tfidf_matrix = tfidf_vectorizer.fit_transform(Post.objects.values_list('body', flat=True))

def calculate_cosine_similarity(post1, post2):
    
    # Get the indices of the posts in the database
    index1 = post1.id - 1  # Assuming IDs are 1-based
    index2 = post2.id - 1

    # Get the TF-IDF vectors for the posts
    tfidf_post1 = tfidf_matrix[index1]
    tfidf_post2 = tfidf_matrix[index2]

    # Calculate the cosine similarity between the TF-IDF vectors
    similarity = cosine_similarity(tfidf_post1, tfidf_post2)[0][0]

    return similarity


def sendPush(title, msg, registration_token, dataObject=None):
    # See documentation on defining a message payload.
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg
        ),
        data=dataObject,
        tokens=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send_multicast(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)