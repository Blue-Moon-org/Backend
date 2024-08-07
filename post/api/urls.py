from django.urls import path
from .views import (
    CommentList,
    CommentView,
    FavouritePostsView,
    FeaturedPosts,
    FeedView,
    LikeComment,
    PostView,
    PostDetail,
    LikePost,
    SharePost,
    FavoritePost,
    MyPostsView,
    MyLikedPostsView,
    MyPostsNewView,
    LikedPostsView,
    PostRecommendationView
)

urlpatterns = [
    path('featured/', FeaturedPosts.as_view(), name='featured-posts'),
    path('feed/<str:category>/', FeedView.as_view(), name='feed'),
    path('myposts/', MyPostsView.as_view(), name='myposts'),
    path('user-posts/<str:id>/', MyPostsNewView.as_view(), name='user-posts'),
    path('liked/', MyLikedPostsView.as_view(), name='liked'),
    path('mylike/<str:id>/', LikedPostsView.as_view(), name='mylike'),
    path('posts/', PostView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    path('like/<int:pk>/', LikePost.as_view(), name='like-post'),
    path('like-comment/<int:pk>/', LikeComment.as_view(), name='like-comment'),
    path('share/<int:pk>/', SharePost.as_view(), name='share-post'),
    path('favorite/<int:pk>/', FavoritePost.as_view(), name='favorite-post'),
    path('myfavorites/', FavouritePostsView.as_view(), name='favorites'),
    path('see-more/<int:post>/', PostRecommendationView.as_view(), name='see-more-post'),
   # path('categories/', CategoryList.as_view(), name='category-list'),
   # path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('comments/<int:pk>/', CommentList.as_view(), name='comment-list'),
    path('post-comments/<int:pk>/', CommentView.as_view(), name='post-comments'),
    
]
