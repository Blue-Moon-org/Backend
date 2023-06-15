from django.urls import path
from .views import NotificationView, NotificationSeen, NotificationDelete

app_name = "notifications"

urlpatterns = [
    path("notification_list/", NotificationView, name="notification-list"),
    path("notification_seen/", NotificationSeen.as_view(), name="notification-seen"),
    path(
        "notification_delete/", NotificationDelete.as_view(), name="notification-delete"
    ),
]
