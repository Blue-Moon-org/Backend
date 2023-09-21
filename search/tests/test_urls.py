from django.urls import reverse, resolve
from rest_framework.test import APITestCase
from django.test import TestCase
from search.api.views import SearchUsers, SearchLatest, BlockCategoryView, SearchPosts, SearchBlocks
from rest_framework import generics, status, views, permissions


class UrlTestCase(APITestCase):
    def test_get_user_search_request(self):
        url = reverse('users')
        self.assertEquals(resolve(url).func.view_class, SearchUsers)

    def test_get_lastest_search_request(self):
        url = reverse('latest')
        self.assertEquals(resolve(url).func.view_class, SearchLatest)

    def test_get_blockcategory_search_request(self):
        url = reverse('block-category')
        self.assertEquals(resolve(url).func.view_class, BlockCategoryView)

    def test_get_posts_search_request(self):
        url = reverse('posts')
        self.assertEquals(resolve(url).func.view_class, SearchPosts)

    def test_get_blocks_search_request(self):
        url = reverse('blocks')
        self.assertEquals(resolve(url).func.view_class, SearchBlocks)
