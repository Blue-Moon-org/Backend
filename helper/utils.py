from django.core.mail import EmailMessage
from string import digits, ascii_lowercase, ascii_uppercase
from secrets import choice as secret_choice
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from random import choice as random_choice
import threading
import datetime
import uuid


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


def get_random_code():
    code = str(uuid.uuid4())[:8].replace("-", " ").lower()
    return code


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
DEFAULT_PAGE_SIZE = 10


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