from post.models import Post  # , Comment, Category, LikedPost
from core.models import User
#from ..helper import Helper, get_data
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
)
from rest_framework import status
from post.api.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


class FeaturedPosts(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request):
        featured_posts = Post.objects.filter(is_featured=True)
        serializer = PostSerializer(featured_posts, many=True)

        return Response(
            {
                "status": True,
                "message": "Featured posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        posts = Post.objects.all()
        serializer = PostDetailSerializer(posts, many=True)

        return Response(
            {
                "status": True,
                "message": "Posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    

class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.POST
        serializer = PostSerializer(data=data)
        # Get a list of all uploaded image files
        images = request.FILES.getlist('images')
        
        if serializer.is_valid():
            post = serializer.save(owner=user)
        
            # Save each image associated with the post
            for image in images:
                Image.objects.create(post=post, image=image)
            return Response(
                {
                    "status": True,
                    "message": "Post created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostDetailSerializer(posts, many=True)
        return Response(
            {
                "status": True,
                "message": "Posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
class PostDetail(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer


class LikePost(APIView):
    """
    get:
        Likes the desired post.
        parameters = [pk]
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = User.objects.filter(id=request.user.id).first()
        print(request.user)
        post = get_object_or_404(Post, pk=pk)

        if user in post.likes.all():
            post.likes.remove(user)
            return Response(
                {"status": True, "message": "Post Unliked"},
                status=status.HTTP_200_OK,
            )

        else:
            post.likes.add(user)

            return Response(
                {"status": True, "message": "Post liked"},
                status=status.HTTP_200_OK,
            )

class SharePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        post = get_object_or_404(Post, pk=pk)

        post.shares.add(user.id)

        return Response(
            {
                "status": True,
                "message": "Post shared successfully",
            },
            status=status.HTTP_201_CREATED,
        )

class FavoritePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        post = get_object_or_404(Post, pk=pk)
        if user not in post.favourite.all():
            post.favourite.add(user)

            return Response(
                {
                    "status": True,
                    "message": "Post marked as favorite",
                },
                status=status.HTTP_200_OK,
            )
        else:
            post.favourite.remove(user)

            return Response(
                {"status": True, "message": "Post removed as favorite"},
                status=status.HTTP_200_OK,
            )

# class CategoryList(APIView):
#     def post(self, request):

#         auth_status = Helper(request).is_autheticated()
#         if auth_status["status"]:
#             user = User.objects.filter(id=auth_status["payload"]["id"]).first()
#             data = get_data(request.POST)
#             serializer = CategorySerializer(data=data)
#             if serializer.is_valid():
#                 serializer.save(authur=user)

#                 return Response(
#                     {
#                         "status": True,
#                         "message": "Post created successfully",
#                         "data": serializer.data,
#                     },
#                     status=status.HTTP_201_CREATED,
#                 )

#             else:
#                 return Response(
#                     {"status": False, "message": serializer.errors},
#                     status=status.HTTP_200_OK,
#                 )
#         else:
#             return Response(
#                 {"status": False, "message": "Unathorised"},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#     def get(self, request):
#         cats = Category.objects.all()
#         serializer = CategorySerializer(cats, many=True)
#         return Response(
#             {
#                 "status": True,
#                 "message": "Category fetched successfully",
#                 "data": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CommentList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = request.data
        post = get_object_or_404(Post, pk=pk)
        data["post"] = post.id
        user = request.user  # Use the authenticated user
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(
                {
                    "status": True,
                    "message": "Comment created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(
            {
                "status": True,
                "message": "Posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

# class BookmarksView(APIView):
#     def post(self, request):

#         pid = request.GET.get("post")
#         auth_status = Helper(request).is_autheticated()
#         if auth_status["status"]:
#             user = User.objects.filter(id=auth_status["payload"]["id"]).first()
#             post = get_object_or_404(Post, pk=pid)

#             if not Bookmarks.objects.filter(user=user).exists():

#                 bmk = Bookmarks.objects.create(user=user)
#                 bmk.post.add(post)
#                 bmk.save()
#                 serializer = BookmarksSerializer(bmk)

#                 return Response(
#                     {
#                         "status": True,
#                         "message": "New bookmark created successfully",
#                         "data": serializer.data,
#                     },
#                     status=status.HTTP_201_CREATED,
#                 )
#             else:
#                 bmk = Bookmarks.objects.get(user=user)
#                 bmk.post.add(post)
#                 serializer = BookmarksSerializer(bmk)
#                 return Response(
#                     {
#                         "status": True,
#                         "message": "New post added successfully",
#                         "data": serializer.data,
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#         else:

#             return Response(
#                 {
#                     "status": False,
#                     "message": "Unathorised",
#                 },
#                 status=status.HTTP_200_OK,
#             )

#     def get(self, request):

#         auth_status = Helper(request).is_autheticated()
#         if auth_status["status"]:
#             user = User.objects.filter(id=auth_status["payload"]["id"]).first()
#             bmk = get_object_or_404(Bookmarks, user=user)
#             serializer = BookmarksSerializer(bmk)

#             return Response(
#                 {
#                     "status": True,
#                     "message": "Bookmark fetched successfully",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         else:

#             return Response(
#                 {
#                     "status": False,
#                     "message": "Unathorised",
#                 },
#                 status=status.HTTP_200_OK,
#             )

#     def delete(self, request):

#         pid = request.GET.get("post")
#         auth_status = Helper(request).is_autheticated()
#         if auth_status["status"]:
#             user = User.objects.filter(id=auth_status["payload"]["id"]).first()
#             post = get_object_or_404(Post, pk=pid)
#             bmk = get_object_or_404(Bookmarks, user=user)

#             bmk.post.remove(post)
#             bmk.save()
#             serializer = BookmarksSerializer(bmk)

#             return Response(
#                 {
#                     "status": True,
#                     "message": "Bookmark removed successfully",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_204_NO_CONTENT,
#             )
#         else:

#             return Response(
#                 {
#                     "status": False,
#                     "message": "Unathorised",
#                 },
#                 status=status.HTTP_200_OK,
#             )
