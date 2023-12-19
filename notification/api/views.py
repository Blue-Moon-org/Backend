from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notification.models import Notification
from .serializers import NotificationSerializer
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from helper.utils import CustomPagination



class NotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    # def get_queryset(self):
    #     return Notification.objects.filter(owner=self.request.user).order_by("-id")
    
    def list(self, request):
        queryset = Notification.objects.filter(owner=self.request.user).order_by("-id")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": True,
            "data": serializer.data,
        }

        return self.get_paginated_response(response_data)

# class NotificationView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         notify_list = Notification.objects.filter(owner=request.user).order_by("-id")
#         paginator = CustomPagination()
#         result_page = paginator.paginate_queryset(notify_list, request)
#         noti_count = Notification.objects.filter(owner=request.user).count()

#         # Instead of doing, if 0 then not show notification badge in the client side,
#         # we just send a null value to notification count from the server if the count is 0.
#         if noti_count == 0:
#             noti_count = None

#         serializer = NotificationSerializer(
#             result_page, many=True, context={"request": request}
#         )

#         return paginator.get_paginated_response(
#             {"data": serializer.data, "noti_count": noti_count}
#         )


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
