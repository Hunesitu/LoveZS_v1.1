"""
LoveZs App URL 配置
对应原 Express 路由:
- backend/src/routes/diary.ts
- backend/src/routes/photo.ts
- backend/src/routes/countdown.ts
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建 DRF Router
router = DefaultRouter()

# 注册 ViewSets
# 对应原 Express 路由配置
router.register(r'diaries', views.DiaryViewSet, basename='diary')
router.register(r'photos', views.PhotoViewSet, basename='photo')
router.register(r'countdowns', views.CountdownViewSet, basename='countdown')

app_name = 'lovezs'

urlpatterns = [
    # API 路由
    path('api/', include(router.urls)),

    # 健康检查
    path('api/health/', views.health_check, name='health-check'),

    # 备份导出与清除数据
    path('api/backup/export/', views.backup_export, name='backup-export'),
    path('api/admin/clear/', views.clear_all_data, name='admin-clear'),
]
