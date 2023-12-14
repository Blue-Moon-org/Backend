from core.models import User
from helper.utils import CustomPagination
from post.models import Post
from post.api.serializers import PostDetailSerializer, SearchPostDetailSerializer
from core.api.serializers import SearchListUserSerializer
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from product.api.serializers import ProductDetailSerializer
from product.models import Product

import django_filters


class ContactFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'firstname': ['startswith'],
            'lastname': ['startswith'],
        }
        together = ['first_name', 'last_name']


# LATEST
class SearchLatest(ListAPIView):
    """
    Returns all latest posts.
    """
    queryset = Post.objects.order_by('-created')
    serializer_class = PostDetailSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination    
    search_fields = ("title", "owner__lastname", "owner__firstname", "body", "category")

# PEOPLE
class SearchUsers(ListAPIView):
    """
    Returns all users.
    """
    queryset = User.objects.filter(account_type="Designer")
    serializer_class = SearchListUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination       
    search_fields = ("brand_name", "bio", "firstname", "lastname", "account_type")
    filter_class = ContactFilter

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
    serializer_class = SearchPostDetailSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination     
    search_fields = ("title", "body", "owner__firstname", "owner__lastname", "owner__brand_name","category")

# PRODUCTS
class SearchProducts(ListAPIView):
    """
    Returns all posts.
    """
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination    
    search_fields = ("title", "description", "owner__firstname", "owner__lastname", "owner__brand_name","category")



