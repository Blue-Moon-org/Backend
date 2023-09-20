from django.db import models
from core.models import User
from django.utils.translation import gettext_lazy as _

from helper.utils import CATEGORY




class Post(models.Model):

    title = models.CharField(max_length=100, blank=True, default="")
    body = models.TextField(blank=True, default="")
    owner = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    category = models.CharField(choices=CATEGORY, max_length=20, default="Native")
    created = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="post_like",
        verbose_name=_("Likes"),
    )
    shares = models.ManyToManyField(
        User,
        blank=True,
        related_name="post_share",
        verbose_name=_("Shares"),
    )
    favourite = models.ManyToManyField(
        User,
        blank=True,
        related_name="fav_like",
        verbose_name=_("Favs"),
    )

    class Meta:
        ordering = ["created"]

    # @property
    # def thumbnail_url(self):

    #     if self.thumbnail and hasattr(self.thumbnail, "url"):
    #         return self.thumbnail.url
    #     else:
    #         return ""
        
class Image(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')
    @property
    def image_url(self):

        if self.image and hasattr(self.image, "url"):
            return self.image.url
        else:
            return ""

class Category(models.Model):
    authur = models.ForeignKey(User, related_name="post_category", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, default="", unique=True)

    class Meta:
        verbose_name_plural = "categories"


class Comment(models.Model):

    body = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="post_comments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]
