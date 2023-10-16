from notification.models import Notification
from post.models import Post  # , Comment, Category, LikedPost
from core.models import User
from helper.utils import CustomPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework import status
from post.api.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
import logging

log = logging.getLogger(__name__)


class FeaturedPosts(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        featured_posts = Post.objects.filter(is_featured=True)
        serializer = PostDetailSerializer(featured_posts, many=True)

        return Response(
            {
                "status": True,
                "message": "Featured posts fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class FeedView(ListAPIView):
    serializer_class = PostDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, category="All", *args, **kwargs):
        if category == "All":
            queryset = Post.objects.all()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(
                    page, many=True, context={"request": request}
                )
            else:
                serializer = self.get_serializer(
                    queryset, many=True, context={"request": request}
                )

        else:
            queryset = Post.objects.filter(category=category)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(
                    page, many=True, context={"request": request}
                )
            else:
                serializer = self.get_serializer(
                    queryset, many=True, context={"request": request}
                )

        category_data = {
            "category": category,
            "posts": serializer.data,
        }

        response_data = {
            "status": True,
            "message": "Posts fetched successfully",
            "categoryData": category_data,
        }

        return self.get_paginated_response(response_data)


class CommentList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class

    def list(self, request, pk, *args, **kwargs):
        queryset = Comment.objects.filter(post=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
        else:
            serializer = self.get_serializer(
                queryset, many=True, context={"request": request}
            )
        response_data = {
            "status": True,
            "message": "comments fetched successfully",
            "comments": serializer.data,
        }
        return self.get_paginated_response(response_data)


class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.POST
        serializer = PostSerializer(data=data)
        # Get a list of all uploaded image files
        images = request.FILES.getlist("images")
        # log.info(images)
        if serializer.is_valid():
            post = serializer.save(owner=user)
            # Save each image associated with the post
            for image in images:
                img = Image.objects.create(post=post, image=image)
                img.save()
            data = UserPostDetailSerializer(Post.objects.get(id=post.id)).data
            return Response(
                {
                    "status": True,
                    "message": "Post created successfully",
                    "data": data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
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

    def post(self, request, pk):
        user = User.objects.filter(id=request.user.id).first()
        post = get_object_or_404(Post, pk=pk)

        if user in post.likes.all():
            post.likes.remove(user)
            post.save()
            data = PostDetailSerializer(
                Post.objects.get(id=post.id), context={"request": request}
            ).data

            return Response(
                {"status": True, "data": data, "message": "Post Unliked"},
                status=status.HTTP_200_OK,
            )

        else:
            post.likes.add(user)
            post.save()
            data = PostDetailSerializer(
                Post.objects.get(id=post.id), context={"request": request}
            ).data
            notify = Notification.objects.create(
                notification_type="UF",
                comments=f"@{user.firstname} liked your post",
                to_user=post.owner,
                from_user=user,
            )
            notify.save()
            return Response(
                {"status": True, "data": data, "message": "Post liked"},
                status=status.HTTP_200_OK,
            )


class SharePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        post = get_object_or_404(Post, pk=pk)

        post.shares.add(user.id)
        post.save()
        data = PostDetailSerializer(
            Post.objects.get(id=post.id), context={"request": request}
        ).data

        return Response(
            {
                "status": True,
                "data": data,
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
            post.save()
            data = PostDetailSerializer(
                Post.objects.get(id=post.id), context={"request": request}
            ).data

            return Response(
                {
                    "status": True,
                    "data": data,
                    "message": "Post marked as favorite",
                },
                status=status.HTTP_200_OK,
            )
        else:
            post.favourite.remove(user)
            post.save()
            data = PostDetailSerializer(
                Post.objects.get(id=post.id), context={"request": request}
            ).data

            return Response(
                {"status": True, "data": data, "message": "Post removed as favorite"},
                status=status.HTTP_200_OK,
            )


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = request.data
        post = get_object_or_404(Post, pk=pk)
        data["post"] = post.id
        user = request.user  # Use the authenticated user
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(owner=user)
            notify = Notification.objects.create(
                notification_type="C",
                comments=f"@{user.firstname} commented on your post",
                to_user=post.owner,
                from_user=user,
            )
            notify.save()
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


class LikeComment(APIView):
    """
    get:
        Likes the desired comment.
        parameters = [pk]
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user  # User.objects.filter(id=.id).first()
        comment = get_object_or_404(Comment, pk=pk)

        if user in comment.likes.all():
            comment.likes.remove(user)
            comment.save()
            data = CommentDetailSerializer(
                Comment.objects.get(id=comment.id), context={"request": request}
            ).data
            return Response(
                {"status": True, "data": data, "message": "Comment Unliked"},
                status=status.HTTP_200_OK,
            )

        else:
            comment.likes.add(user)
            comment.save()
            data = CommentDetailSerializer(
                Comment.objects.get(id=comment.id), context={"request": request}
            ).data

            return Response(
                {"status": True, "data": data, "message": "Comment liked"},
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


class MyPostsView(ListAPIView):
    serializer_class = PostDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": True,
            "message": "Posts fetched successfully",
            "posts": serializer.data,
        }

        return self.get_paginated_response(response_data)


class MyLikedPostsView(ListAPIView):
    serializer_class = PostDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(likes__id=request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": True,
            "message": "Liked posts fetched successfully",
            "posts": serializer.data,
        }

        return self.get_paginated_response(response_data)
