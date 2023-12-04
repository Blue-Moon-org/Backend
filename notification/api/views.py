from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notification.models import Notification
from .serializers import NotificationSerializer

from django.shortcuts import get_object_or_404
from helper.utils import CustomPagination


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def NotificationView(request):
    notify_list = Notification.objects.filter(
        owner=request.user,
    ).order_by("-id")
    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(notify_list, request)
    noti_count = Notification.objects.filter(owner=request.user).count()
    """
    instead of doing ,if 0 then not show notificaton badge in client side 
    we just send null value to notification count from server if count is 0
    """
    if noti_count == 0:
        noti_count = None
    serializer = NotificationSerializer(
        result_page, many=True, context={"request": request}
    )
    return paginator.get_paginated_response(
        {"data": serializer.data, "noti_count": noti_count}
    )


class NotificationSeen(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data

        notification = get_object_or_404(Notification, id=data.get("notify_id"))
        notification.user_has_seen = True
        notification.save()
        return Response({"notification_seen": True})


class NotificationDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        notification = get_object_or_404(Notification, id=data.get("notify_id"))
        if notification.to_user == request.user:
            notification.delete()
            return Response({"notification_deleted": True})
