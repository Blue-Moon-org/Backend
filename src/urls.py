from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("core/", include("core.api.urls")),
    path("post/", include("post.api.urls")),
    path("notification/", include("notification.api.urls")),
    path("api/", include("product.api.urls")),
    path("chat/", include("chat.urls")),
    path("search/", include("search.api.urls")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)