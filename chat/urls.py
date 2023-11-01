from django.urls import path
from .views import (
    ChatCreateView,
    ImageMessageView,
    ChatDeleteView,
    ChatDetailView,
    ChatListView,
    ChatUpdateView,
)

app_name = "chat"

urlpatterns = [
    path("", ChatListView.as_view()),
    path("create/", ChatCreateView.as_view()),
    path("image-message/", ImageMessageView.as_view()),
    path("<int:pk>/", ChatDetailView.as_view()),
    path("<pk>/update/", ChatUpdateView.as_view()),
    path("<pk>/delete/", ChatDeleteView.as_view()),
]
