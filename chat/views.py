from core.models import User
from helper.utils import get_user_contact
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Chat, ImageMessage
from rest_framework.views import APIView
from .serializers import ChatSerializer

from rest_framework.generics import RetrieveAPIView, DestroyAPIView, UpdateAPIView


class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contact = get_user_contact(request.user.id)
        chats = ChatSerializer(contact.chats.all(), context={"request":request},many=True, )

        return Response({"status": True, "data": chats.data}, status=status.HTTP_200_OK)


class ChatDetailView(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]


class ChatCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = User.objects.get(id=request.user.id).id
        other_user = User.objects.get(id=data["id"]).id

        if other_user != user:
            my_contact = get_user_contact(user)
            other_contact = get_user_contact(other_user)
            intersections = (
                Chat.objects.filter(participants=my_contact) & other_contact.chats.all()
            )
            # print(intersections)
            if not intersections.exists():
                chat = Chat.objects.create()
                chat.participants.add(my_contact, other_contact)
                chat.save()
                serializer = ChatSerializer(chat, context={"request":request})

                return Response(
                    {
                        "status": True,
                        "message": "New chat created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                serializer = ChatSerializer(intersections.first(), context={"request":request})
                return Response(
                    {
                        "status": True,
                        "message": "This chat already exist",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {
                    "status": False,
                    "message": "You can't create chat with yourself",
                },
                status=status.HTTP_200_OK,
            )


class ChatUpdateView(UpdateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]


class ChatDeleteView(DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]



class ImageMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.POST
        data["chatId"]
        chat = Chat.objects.get(id=data["chatId"])
        images = request.FILES.getlist("images")
        # Save each image associated with the post
        imgs = []
        for image in images:
            img = ImageMessage.objects.create(chat=chat, image=image)
            imgs.append(img.image_url)
            img.save()
        i = "Image" if len(imgs) < 2 else "Images"
        return Response(
            {
                "status": True,
                "message": f"{i} sent successfully",
                "data": imgs,
            },
            status=status.HTTP_201_CREATED,
        )
        
# class ChatCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         data = request.data

#         serializer = ChatroomSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             instance = serializer.instance
#             user = instance.users.filter(username=request.user.email)
#             others = instance.users.exclude(username=request.user.email).first()
#             Notification.objects.get_or_create(
#                 notification_type="CR",
#                 comments=(f"@{user.fullname} request to chat you"),
#                 to_user=others,
#                 from_user=user,
#             )

#             return Response({
#                 "status": True,
#                 "message": "New chat created successfully",
#                 "data": serializer.data},
#                 status=status.HTTP_201_CREATED)
#         else:

#             return Response({
#                 "status": False,
#                 "errors":serializer.errors,},
#                 status=status.HTTP_200_OK)

# class ChatDetail(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, pk):
#         data = request.data

#         chatroom = Chatroom.objects.filter(id=pk)
#         serializer = ChatroomSerializer(data=data, partial=True)
#         if serializer.is_valid():
#             serializer.instance = chatroom
#             serializer.save()
#             instance = serializer.instance
#             user = instance.users.filter(username=request.user.username)
#             others = instance.users.exclude(username=request.user.username).first()
#             if instance.permission == "G":
#                 Notification.objects.get_or_create(
#                     notification_type="AC",
#                     comments=(f"@{user.username} request accepted"),
#                     to_user=others,
#                     from_user=user,
#                 )
#             else:
#                 Notification.objects.get_or_create(
#                     notification_type="DC",
#                     comments=(f"@{user.username} request denied"),
#                     to_user=others,
#                     from_user=user,
#                 )
#             return Response({
#                 "status": True,
#                 "message": "New chat created successfully",
#                 "data": serializer.data},
#                 status=status.HTTP_201_CREATED)
#         else:

#             return Response({
#                 "status": False,
#                 "errors":serializer.errors,},
#                 status=status.HTTP_200_OK)


# class ChatroomViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = Chatroom.objects.all()
#     serializer_class = ChatroomSerializer

#     @action(methods=['get'], detail=True, url_path='chat-history')
#     def get_chatroom_chat_history(self, request):
#         user = request.user
#         chatroom = self.get_object()
#         data = ChatroomSerializer(chatroom).data
#         return Response({'message': 'success', 'history': data})

#     @action(methods=['patch'], detail=True, url_path='exit')
#     def exit_chatroom(self, request, pk=None):
#         chatroom = self.get_object()

#         user = request.user
#         return Response({})


# class MessageViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = Message.objects.all()
#     serializer_class = ChatMessageSerializer
