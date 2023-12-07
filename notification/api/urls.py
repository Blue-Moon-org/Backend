from django.urls import path
from .views import NotificationView, NotificationSeen, NotificationDelete

app_name = "notifications"

urlpatterns = [
    path("list/", NotificationView.as_view(), name="notification-list"),
    path("seen/", NotificationSeen.as_view(), name="notification-seen"),
    path(
        "delete/", NotificationDelete.as_view(), name="notification-delete"
    ),
]
