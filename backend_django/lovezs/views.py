"""
LoveZs API Views
使用 Django REST Framework ViewSets

对应原 Express 控制器:
- backend/src/controllers/diaryController.ts
- backend/src/controllers/photoController.ts
- backend/src/controllers/countdownController.ts
- backend/src/controllers/backupController.ts
"""

from datetime import datetime
import os
import shutil
import tempfile
import uuid
import zipfile

from django.conf import settings
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from PIL import Image
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from django.db.models import Q

from .models import Album, Photo, Diary, DiaryPhoto, DiaryTag, Countdown, DiaryComment
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    PhotoSerializer, PhotoListSerializer, PhotoCreateSerializer,
    DiarySerializer, DiaryListSerializer, DiaryCreateSerializer,
    DiaryCommentSerializer,
    CountdownSerializer, CountdownListSerializer,
    CategoryListSerializer, TagListSerializer,
)


# ========================================
# 自定义响应格式
# ========================================

def success_response(data=None, message="操作成功"):
    """
    成功响应格式
    对应 Express 的 res.json({ success: true, data, message })
    """
    response_data = {"success": True}
    if data is not None:
        response_data["data"] = data
    if message:
        response_data["message"] = message
    return Response(response_data)


def error_response(message="操作失败", http_status=status.HTTP_400_BAD_REQUEST):
    """
    错误响应格式
    对应 Express 的 res.status(400).json({ success: false, message })
    """
    return Response({
        "success": False,
        "message": message,
    }, status=http_status)


# ========================================
# Diary ViewSet
# 对应: backend/src/controllers/diaryController.ts
# ========================================

class DiaryViewSet(viewsets.ModelViewSet):
    """
    日记 API 视图集
    """
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'mood', 'date']
    search_fields = ['title', 'content']
    ordering_fields = ['date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """公开日记所有人可见，私密日记仅作者可见"""
        qs = Diary.objects.prefetch_related(
            'attached_photos', 'comments', 'comments__created_by'
        ).select_related('created_by')
        if self.request.user.is_authenticated:
            return qs.filter(Q(is_public=True) | Q(created_by=self.request.user))
        return qs.filter(is_public=True)

    def perform_create(self, serializer):
        """创建时自动设置创建者"""
        return serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'list':
            return DiaryListSerializer
        if self.action == 'create':
            return DiaryCreateSerializer
        return DiarySerializer

    def list(self, request, *args, **kwargs):
        """
        获取日记列表
        对应: getDiaries
        """
        queryset = self.filter_queryset(self.get_queryset())

        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'diaries': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return success_response({'diaries': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """
        获取单篇日记
        对应: getDiary
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response({'diary': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        创建日记
        对应: createDiary
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        diary = self.perform_create(serializer)

        diary_serializer = DiarySerializer(diary)
        return success_response(
            {'diary': diary_serializer.data},
            message='日记创建成功'
        )

    def update(self, request, *args, **kwargs):
        """
        更新日记
        对应: updateDiary
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = DiaryCreateSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        diary_serializer = DiarySerializer(instance)
        return success_response(
            {'diary': diary_serializer.data},
            message='日记更新成功'
        )

    def destroy(self, request, *args, **kwargs):
        """
        删除日记
        对应: deleteDiary
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='日记删除成功')

    # ========================================
    # 自定义 Actions
    # ========================================

    @action(detail=True, methods=['post'], url_path='photos')
    def attach_photos(self, request, pk=None):
        """
        关联照片到日记
        对应: attachPhotos
        POST /api/diaries/{id}/photos
        Body: { photoIds: [1, 2, 3] }
        """
        diary = self.get_object()
        photo_ids = request.data.get('photoIds', [])

        for photo_id in photo_ids:
            try:
                photo = Photo.objects.get(id=photo_id)
                DiaryPhoto.objects.get_or_create(diary=diary, photo=photo)
            except Photo.DoesNotExist:
                return error_response(f'照片 ID {photo_id} 不存在', status.HTTP_404_NOT_FOUND)

        return success_response(message='照片关联成功')

    @action(detail=True, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)')
    def remove_photo(self, request, pk=None, photo_id=None):
        """
        从日记移除照片
        对应: removePhoto
        DELETE /api/diaries/{id}/photos/{photo_id}
        """
        diary = self.get_object()
        try:
            diary_photo = DiaryPhoto.objects.get(diary=diary, photo_id=photo_id)
            diary_photo.delete()
            return success_response(message='照片移除成功')
        except DiaryPhoto.DoesNotExist:
            return error_response('照片关联不存在', status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='meta/categories')
    def categories(self, request):
        """
        获取所有日记分类
        对应: getCategories
        GET /api/diaries/meta/categories
        """
        categories = Diary.objects.values_list('category', flat=True).distinct()
        serializer = CategoryListSerializer({'categories': list(categories)})
        return success_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='meta/tags')
    def tags(self, request):
        """
        获取所有日记标签
        对应: getTags
        GET /api/diaries/meta/tags
        """
        tags = DiaryTag.objects.values_list('tag', flat=True).distinct()
        serializer = TagListSerializer({'tags': list(tags)})
        return success_response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='comments',
            permission_classes=[permissions.IsAuthenticated])
    def comments(self, request, pk=None):
        """
        获取/发表日记评论
        GET  /api/diaries/{id}/comments/ — 获取评论列表
        POST /api/diaries/{id}/comments/ — 发表评论
        """
        diary = self.get_object()

        if request.method == 'GET':
            comments_qs = diary.comments.select_related('created_by').all()
            serializer = DiaryCommentSerializer(comments_qs, many=True)
            return success_response({'comments': serializer.data})

        # POST
        serializer = DiaryCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(diary=diary, created_by=request.user)
        return success_response(
            {'comment': serializer.data},
            message='评论发表成功'
        )

    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)',
            permission_classes=[permissions.IsAuthenticated])
    def delete_comment(self, request, pk=None, comment_id=None):
        """
        删除评论（仅评论作者可删除）
        DELETE /api/diaries/{id}/comments/{comment_id}/
        """
        diary = self.get_object()
        try:
            comment = DiaryComment.objects.get(id=comment_id, diary=diary)
        except DiaryComment.DoesNotExist:
            return error_response('评论不存在', status.HTTP_404_NOT_FOUND)

        if comment.created_by != request.user:
            return error_response('只能删除自己的评论', status.HTTP_403_FORBIDDEN)

        comment.delete()
        return success_response(message='评论删除成功')


# ========================================
# Photo ViewSet
# 对应: backend/src/controllers/photoController.ts
# ========================================

class PhotoViewSet(viewsets.ModelViewSet):
    """
    照片 API 视图集
    """
    queryset = Photo.objects.select_related('album', 'created_by').all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['album']
    search_fields = ['original_name', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """创建时自动设置上传者"""
        serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'list':
            return PhotoListSerializer
        return PhotoSerializer

    def list(self, request, *args, **kwargs):
        """获取照片列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'photos': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return success_response({'photos': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """获取单张照片"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response({'photo': serializer.data})

    def destroy(self, request, *args, **kwargs):
        """删除照片"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='照片删除成功')

    # ========================================
    # 文件上传 Action
    # ========================================

    @action(detail=False, methods=['post'], url_path='upload', parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        上传照片
        对应: uploadPhotos
        POST /api/photos/upload
        Body: FormData with 'photos' file list
        """
        uploaded_files = request.FILES.getlist('photos')

        if not uploaded_files:
            return error_response('没有上传文件', status.HTTP_400_BAD_REQUEST)

        album, _ = Album.objects.get_or_create(
            is_default=True,
            defaults={'name': '默认相册'}
        )

        photos = []
        for uploaded_file in uploaded_files:
            if not uploaded_file.content_type or not uploaded_file.content_type.startswith('image/'):
                return error_response('仅支持图片文件上传', status.HTTP_400_BAD_REQUEST)

            ext = os.path.splitext(uploaded_file.name)[1].lower()
            filename = f"{uuid.uuid4().hex}{ext}"

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            original_path = os.path.join(settings.MEDIA_ROOT, filename)

            with open(original_path, 'wb') as target_file:
                for chunk in uploaded_file.chunks():
                    target_file.write(chunk)

            thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
            os.makedirs(thumbnails_dir, exist_ok=True)
            thumbnail_path = os.path.join(thumbnails_dir, filename)

            with Image.open(original_path) as image:
                image.thumbnail((400, 400))
                image.save(thumbnail_path)

            photo_data = {
                'filename': filename,
                'original_name': uploaded_file.name,
                'path': f'/{filename}',
                'url': f'{settings.MEDIA_URL}{filename}',
                'size': uploaded_file.size,
                'mimetype': uploaded_file.content_type,
                'album': album.id,
            }

            serializer = PhotoCreateSerializer(data=photo_data)
            serializer.is_valid(raise_exception=True)
            photo = serializer.save()
            photos.append(photo)

        result_serializer = PhotoSerializer(photos, many=True)
        return success_response(
            {'photos': result_serializer.data},
            message=f'成功上传 {len(photos)} 张照片'
        )


# ========================================
# Countdown ViewSet
# 对应: backend/src/controllers/countdownController.ts
# ========================================

class CountdownViewSet(viewsets.ModelViewSet):
    """
    重要日 API 视图集
    """
    queryset = Countdown.objects.select_related('created_by').all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'direction']
    search_fields = ['title', 'description']
    ordering_fields = ['target_date']
    ordering = ['target_date']

    def perform_create(self, serializer):
        """创建时自动设置创建者"""
        return serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'list':
            return CountdownListSerializer
        return CountdownSerializer

    def list(self, request, *args, **kwargs):
        """获取重要日列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'countdowns': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return success_response({'countdowns': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """获取单个重要日"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response({'countdown': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        创建重要日
        对应: createCountdown

        自动判断 direction:
        - 如果 target_date 在过去，自动设为 countup
        - 如果 target_date 在未来，自动设为 countdown
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_date = serializer.validated_data.get('target_date')
        if not serializer.validated_data.get('direction'):
            today = datetime.now().date()
            if target_date < today:
                serializer.validated_data['direction'] = 'countup'
            else:
                serializer.validated_data['direction'] = 'countdown'

        countdown = self.perform_create(serializer)
        return success_response(
            {'countdown': CountdownSerializer(countdown).data},
            message='重要日创建成功'
        )

    def update(self, request, *args, **kwargs):
        """更新重要日"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            {'countdown': serializer.data},
            message='重要日更新成功'
        )

    def destroy(self, request, *args, **kwargs):
        """删除重要日"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='重要日删除成功')


# ========================================
# 备份导出与清除数据
# ========================================

def backup_export(request):
    """
    导出媒体文件备份
    GET /api/backup/export
    """
    media_root = settings.MEDIA_ROOT
    filename = f"lovezs-media-backup-{timezone.now().date().isoformat()}.zip"

    temp_file = tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024)
    with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(media_root):
            for root, _, files in os.walk(media_root):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(file_path, media_root)
                    zipf.write(file_path, rel_path)

    temp_file.seek(0)
    return FileResponse(temp_file, as_attachment=True, filename=filename)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def clear_all_data(request):
    """
    清除全部数据（数据库 + 媒体文件）
    POST /api/admin/clear
    仅管理员可操作
    """

    with transaction.atomic():
        DiaryComment.objects.all().delete()
        DiaryPhoto.objects.all().delete()
        DiaryTag.objects.all().delete()
        Diary.objects.all().delete()
        Photo.objects.all().delete()
        Album.objects.all().delete()
        Countdown.objects.all().delete()

    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    return success_response(message='数据已清除')


# ========================================
# Health Check
# ========================================

def health_check(request):
    """
    健康检查接口
    GET /api/health
    """
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'service': 'LoveZs API',
    })
