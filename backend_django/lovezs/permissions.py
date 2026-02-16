"""
LoveZs 自定义权限模块
实现共享查看 + 创建者编辑的权限控制
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    共享查看 + 创建者/管理员编辑权限

    权限规则:
    - 安全方法 (GET, HEAD, OPTIONS): 所有人可访问
    - 写方法 (POST, PUT, PATCH, DELETE): 创建者或管理员可操作
    """

    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True

        # 管理员可操作任何对象
        if request.user and request.user.is_staff:
            return True

        # 写权限仅限创建者
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可写，其他用户只读"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
