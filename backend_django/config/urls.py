"""
URL configuration for LoveZs project.

对应原 Express 路由:
- backend/src/server.ts (路由注册)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # API 路由
    path("", include("lovezs.urls")),

    # 历史兼容：将 /uploads/* 统一重定向到 /media/*
    path(
        "uploads/<path:path>",
        RedirectView.as_view(url=f"{settings.MEDIA_URL}%(path)s", permanent=False),
    ),
]

# 开发环境提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
