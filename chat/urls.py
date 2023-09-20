from django.urls import path
from .views import ChatCreateView, ChatDeleteView, ChatDetailView, ChatListView, ChatUpdateView

# router = routers.DefaultRouter()
# router.register(r'chatrooms', ChatroomViewSet)
# router.register(r'messages', MessageViewSet)

app_name = 'chat'

urlpatterns = [
    path('', ChatListView.as_view()),
    path('create/', ChatCreateView.as_view()),
    path('<int:pk>/', ChatDetailView.as_view()),
    path('<pk>/update/', ChatUpdateView.as_view()),
    path('<pk>/delete/', ChatDeleteView.as_view())
]

# urlpatterns = [
#     path('', include(router.urls)),
#     path('create/', ChatCreateView.as_view()),
#     path('update/<pk>/', ChatDetail.as_view()),
# ]