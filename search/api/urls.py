from django.urls import path
from .views import SearchLatest, SearchProducts, SearchUsers, SearchPosts

urlpatterns = [
    #PEOPLE
    path('latest/', SearchLatest.as_view(), name='latest'),
    #PEOPLE
    path('users/', SearchUsers.as_view(), name='users'),
    #POST
    path('posts/', SearchPosts.as_view(), name='posts'),
    #PRODUCT
    path('products/', SearchProducts.as_view(), name='products'),
]
