from core.models import User
from helper.utils import CustomPagination
from post.models import Post
from post.api.serializers import PostDetailSerializer
from core.api.serializers import ListUserSerializer
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.permissions import AllowAny
from product.api.serializers import ProductDetailSerializer
from product.models import Product


# LATEST
class SearchLatest(ListAPIView):
    """
    Returns all latest posts.
    """
    queryset = Post.objects.order_by('-created')
    serializer_class = PostDetailSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination    
    #ordering = ['username']
    search_fields = ("title", "owner__lastname", "owner__firstname", "body", "category")


# PEOPLE
class SearchUsers(ListAPIView):
    """
    Returns all users.
    """
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination       
    search_fields = ("brand_name", "bio", "firstname", "lastname", "account_type")


# FeaturedPost
class FeaturedPost(ListAPIView):
    """
    Returns all 10 latest featured post.
    """
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination     
    search_fields = ("fullname", "body", "category",)



# POSTS
class SearchPosts(ListAPIView):
    """
    Returns all posts.
    """
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination     
    search_fields = ("title", "body", "owner__firstname", "owner__lastname", "category")

# PRODUCTS
class SearchProducts(ListAPIView):
    """
    Returns all posts.
    """
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination    
    search_fields = ("title", "description", "owner__firstname", "owner__lastname", "category")


# class ListAllPosts(ListAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostDetailSerializer
#     permission_classes = (AllowAny,)
#     pagination_class = PageNumberPagination    
#     filter_backends = (SearchFilter,)
#     search_fields = ("title", "body", "owner__name", "owner__username")


