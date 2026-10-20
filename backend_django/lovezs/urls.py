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
from . import auth_views
from . import game_views

# 创建 DRF Router
router = DefaultRouter()

# 注册 ViewSets
# 对应原 Express 路由配置
router.register(r'diaries', views.DiaryViewSet, basename='diary')
router.register(r'photos', views.PhotoViewSet, basename='photo')
router.register(r'countdowns', views.CountdownViewSet, basename='countdown')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

app_name = 'lovezs'

urlpatterns = [
    # API 路由
    path('api/', include(router.urls)),

    # 认证 API
    path('api/auth/register/', auth_views.register, name='register'),
    path('api/auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', auth_views.logout, name='logout'),
    path('api/auth/profile/', auth_views.profile, name='profile'),
    path('api/auth/change-password/', auth_views.change_password, name='change-password'),

    # 健康检查
    path('api/health/', views.health_check, name='health-check'),

    # 数字炸弹小游戏
    path('api/games/stats/', game_views.game_stats, name='game-stats'),
    path('api/games/pve/', game_views.start_pve, name='game-pve'),
    path('api/games/match/', game_views.match_pvp, name='game-match'),
    path('api/games/room/', game_views.current_room, name='game-current-room'),
    path('api/games/room/<int:room_id>/', game_views.room_detail, name='game-room'),
    path('api/games/room/<int:room_id>/secret/', game_views.set_secret, name='game-secret'),
    path('api/games/room/<int:room_id>/guess/', game_views.make_guess, name='game-guess'),
    path('api/games/room/<int:room_id>/cancel/', game_views.cancel_room, name='game-cancel'),

    # 备份导出与清除数据
    path('api/backup/export/', views.backup_export, name='backup-export'),
    path('api/admin/clear/', views.clear_all_data, name='admin-clear'),
]
