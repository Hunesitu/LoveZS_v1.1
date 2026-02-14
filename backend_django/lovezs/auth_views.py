"""
LoveZs 认证 API 视图
提供用户注册、登录、登出、个人信息管理功能
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, UserRegisterSerializer

User = get_user_model()


# ========================================
# 响应辅助函数
# ========================================

def success_response(data=None, message="操作成功"):
    """成功响应"""
    response_data = {"success": True}
    if data is not None:
        response_data["data"] = data
    if message:
        response_data["message"] = message
    return Response(response_data)


def error_response(message="操作失败", http_status=status.HTTP_400_BAD_REQUEST):
    """错误响应"""
    return Response({
        "success": False,
        "message": message,
    }, status=http_status)


# ========================================
# 注册
# ========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    用户注册（简化版：无需邮箱）
    POST /api/auth/register/
    Body: { username, password }
    """
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # 生成 token
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'message': '注册成功',
            'data': {
                'user': UserSerializer(user).data,
                'token': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'message': '注册失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ========================================
# 登录
# ========================================

class LoginView(TokenObtainPairView):
    """
    用户登录
    POST /api/auth/login/
    Body: { username, password }
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        # 先检查用户是否存在
        if not User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': '该用户不存在，请先注册',
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                user = User.objects.get(username=username)
                return Response({
                    'success': True,
                    'message': '登录成功',
                    'data': {
                        'user': UserSerializer(user).data,
                        'token': response.data
                    }
                })
            return response
        except Exception:
            return Response({
                'success': False,
                'message': '密码错误',
            }, status=status.HTTP_401_UNAUTHORIZED)


# ========================================
# 登出
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    用户登出
    POST /api/auth/logout/
    Body: { refresh }
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return success_response(message='登出成功')
    except Exception as e:
        return error_response(f'登出失败: {str(e)}')


# ========================================
# 个人信息
# ========================================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    获取/更新个人信息
    GET /api/auth/profile/ - 获取当前用户信息
    PUT /api/auth/profile/ - 更新当前用户信息
    """
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return success_response({'user': serializer.data})

    elif request.method == 'PUT':
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return success_response(
                {'user': serializer.data},
                message='个人信息更新成功'
            )
        return Response({
            'success': False,
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ========================================
# 修改密码
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    修改密码
    POST /api/auth/change-password/
    Body: { old_password, new_password }
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return error_response('请提供旧密码和新密码')

    if not request.user.check_password(old_password):
        return error_response('旧密码错误', status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, request.user)
    except Exception as e:
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)

    request.user.set_password(new_password)
    request.user.save()
    return success_response(message='密码修改成功')
