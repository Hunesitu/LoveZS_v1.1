"""
LoveZs API Serializers
将 Django Model 转换为 JSON 格式

对应原 Express 控制器中的响应格式
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Album, Photo, Diary, DiaryPhoto, DiaryTag, Countdown, DiaryComment, Notification

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# ========================================
# Album Serializer
# ========================================

class AlbumSerializer(serializers.ModelSerializer):
    """
    相册序列化器
    """
    photo_count = serializers.SerializerMethodField()
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)

    class Meta:
        model = Album
        fields = [
            'id', 'name', 'description', 'cover_photo',
            'is_default', 'photo_count', 'created_by', 'created_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_count(self, obj):
        """获取相册中的照片数量"""
        return obj.photos.count()


class AlbumListSerializer(serializers.ModelSerializer):
    """
    相册列表序列化器（精简版）
    """
    class Meta:
        model = Album
        fields = ['id', 'name', 'cover_photo', 'is_default', 'photo_count']
        read_only_fields = ['id']

    photo_count = serializers.SerializerMethodField()

    def get_photo_count(self, obj):
        return obj.photos.count()


# ========================================
# Photo Serializer
# ========================================

class PhotoSerializer(serializers.ModelSerializer):
    """
    照片序列化器
    包含虚拟字段的序列化
    """
    # 虚拟字段（对应 Mongoose 的 virtual）
    size_formatted = serializers.ReadOnlyField()
    thumbnail_url = serializers.ReadOnlyField()

    # 相册信息（嵌套序列化）
    album_details = AlbumSerializer(source='album', read_only=True)
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'filename', 'original_name', 'path', 'url',
            'size', 'size_formatted', 'mimetype',
            'album', 'album_details',
            'description', 'location', 'exif', 'compressed_url',
            'thumbnail_url', 'created_by', 'created_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhotoListSerializer(serializers.ModelSerializer):
    """
    照片列表序列化器（精简版）
    """
    size_formatted = serializers.ReadOnlyField()
    thumbnail_url = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = [
            'id', 'filename', 'original_name', 'url',
            'size_formatted', 'mimetype', 'thumbnail_url',
            'album', 'description', 'created_at'
        ]


class PhotoCreateSerializer(serializers.ModelSerializer):
    """
    照片创建序列化器
    """
    class Meta:
        model = Photo
        fields = [
            'filename', 'original_name', 'path', 'url',
            'size', 'mimetype', 'album',
            'description', 'location', 'exif', 'compressed_url'
        ]


# ========================================
# Diary Serializer
# ========================================

class DiaryPhotoSerializer(serializers.ModelSerializer):
    """
    日记照片关联序列化器
    """
    photo_details = PhotoSerializer(source='photo', read_only=True)

    class Meta:
        model = DiaryPhoto
        fields = ['id', 'photo', 'photo_details', 'attached_at']


class DiaryTagSerializer(serializers.ModelSerializer):
    """
    日记标签序列化器
    """
    class Meta:
        model = DiaryTag
        fields = ['id', 'tag']


class DiaryCommentReplySerializer(serializers.ModelSerializer):
    """
    子评论序列化器（不再嵌套）
    """
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)

    class Meta:
        model = DiaryComment
        fields = ['id', 'content', 'parent', 'created_by', 'created_by_details', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class DiaryCommentSerializer(serializers.ModelSerializer):
    """
    日记评论序列化器（顶级评论，嵌套 replies）
    """
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)
    replies = DiaryCommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = DiaryComment
        fields = ['id', 'content', 'parent', 'created_by', 'created_by_details', 'created_at', 'replies']
        read_only_fields = ['id', 'created_by', 'created_at']


class DiarySerializer(serializers.ModelSerializer):
    """
    日记序列化器
    """
    # 虚拟字段
    formatted_date = serializers.ReadOnlyField()
    word_count = serializers.ReadOnlyField()

    # 关联数据
    attached_photos = PhotoSerializer(many=True, read_only=True)
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Diary
        fields = [
            'id', 'title', 'content', 'mood', 'category',
            'date', 'formatted_date', 'is_public', 'is_pinned',
            'attached_photos',
            'word_count',
            'created_by', 'created_by_details',
            'comments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_comments(self, obj):
        top_level = obj.comments.filter(parent__isnull=True).select_related(
            'created_by'
        ).prefetch_related('replies', 'replies__created_by')
        return DiaryCommentSerializer(top_level, many=True).data


class DiaryListSerializer(serializers.ModelSerializer):
    """
    日记列表序列化器（精简版）
    """
    formatted_date = serializers.ReadOnlyField()
    word_count = serializers.ReadOnlyField()
    photo_count = serializers.SerializerMethodField()
    attached_photos = PhotoListSerializer(many=True, read_only=True)
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)

    class Meta:
        model = Diary
        fields = [
            'id', 'title', 'content', 'mood', 'category',
            'date', 'formatted_date', 'is_public', 'is_pinned',
            'attached_photos',
            'word_count', 'photo_count',
            'created_by', 'created_by_details',
            'created_at'
        ]

    def get_photo_count(self, obj):
        """获取关联照片数量"""
        return obj.attached_photos.count()


class DiaryCreateSerializer(serializers.ModelSerializer):
    """
    日记创建序列化器
    """
    photo_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        write_only=True
    )

    class Meta:
        model = Diary
        fields = [
            'title', 'content', 'mood', 'category',
            'date', 'is_public', 'photo_ids', 'created_by'
        ]
        extra_kwargs = {
            'created_by': {'required': False},
            'content': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        """
        创建日记，处理照片关联
        """
        photo_ids = validated_data.pop('photo_ids', [])

        # 创建日记
        diary = Diary.objects.create(**validated_data)

        # 创建照片关联
        for photo_id in photo_ids:
            try:
                photo = Photo.objects.get(id=photo_id)
                DiaryPhoto.objects.get_or_create(diary=diary, photo=photo)
            except Photo.DoesNotExist:
                pass

        return diary

    def update(self, instance, validated_data):
        """
        更新日记，处理照片关联
        """
        photo_ids = validated_data.pop('photo_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if photo_ids is not None:
            DiaryPhoto.objects.filter(diary=instance).delete()
            for photo_id in photo_ids:
                try:
                    photo = Photo.objects.get(id=photo_id)
                    DiaryPhoto.objects.get_or_create(diary=instance, photo=photo)
                except Photo.DoesNotExist:
                    pass

        return instance


# ========================================
# Countdown Serializer
# ========================================

class CountdownSerializer(serializers.ModelSerializer):
    """
    重要日序列化器
    """
    # 虚拟字段
    days = serializers.ReadOnlyField()
    absolute_days = serializers.ReadOnlyField()
    formatted_target_date = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    # 新增：重复日期字段
    recurring_month = serializers.IntegerField(required=False, allow_null=True)
    recurring_day = serializers.IntegerField(required=False, allow_null=True)

    # 创建者信息
    created_by_details = UserBasicSerializer(source='created_by', read_only=True)

    class Meta:
        model = Countdown
        fields = [
            'id', 'title', 'description', 'target_date',
            'formatted_target_date', 'type', 'direction',
            'is_recurring', 'recurring_type',
            'recurring_month', 'recurring_day',
            'days', 'absolute_days', 'status',
            'created_by', 'created_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        验证重复类型和日期字段
        """
        is_recurring = data.get('is_recurring', self.instance.is_recurring if self.instance else False)
        recurring_type = data.get('recurring_type', self.instance.recurring_type if self.instance else None)
        recurring_month = data.get('recurring_month', self.instance.recurring_month if self.instance else None)
        recurring_day = data.get('recurring_day', self.instance.recurring_day if self.instance else None)

        if is_recurring and recurring_type == 'yearly':
            if not recurring_month or not recurring_day:
                raise serializers.ValidationError({
                    'recurring_month': '每年重复事件必须指定月份和日期'
                })
            # 验证日期是否有效
            import calendar
            max_day = calendar.monthrange(2024, recurring_month)[1]  # 使用闰年2024来验证
            if recurring_day > max_day:
                raise serializers.ValidationError({
                    'recurring_day': f'{recurring_month}月最多{max_day}天'
                })

        return data


class CountdownListSerializer(serializers.ModelSerializer):
    """
    重要日列表序列化器（精简版）
    """
    days = serializers.ReadOnlyField()
    absolute_days = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Countdown
        fields = [
            'id', 'title', 'target_date',
            'type', 'direction',
            'is_recurring', 'recurring_type',
            'recurring_month', 'recurring_day',
            'days', 'absolute_days', 'status'
        ]


# ========================================
# Metadata Serializers (用于获取分类、标签等元数据)
# ========================================

class DiaryMetadataSerializer(serializers.Serializer):
    """
    日记元数据序列化器
    """
    categories = serializers.ListField(child=serializers.CharField())
    tags = serializers.ListField(child=serializers.CharField())
    moods = serializers.ListField(child=serializers.CharField())


class CategoryListSerializer(serializers.Serializer):
    """分类列表序列化器"""
    categories = serializers.ListField(child=serializers.CharField())


class TagListSerializer(serializers.Serializer):
    """标签列表序列化器"""
    tags = serializers.ListField(child=serializers.CharField())


# ========================================
# User Serializers
# ========================================

class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'is_staff', 'date_joined']


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器（简化版：不需要邮箱）
    """
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        """验证密码：仅要求最少6个字符"""
        if len(value) < 6:
            raise serializers.ValidationError('密码至少需要6个字符')
        return value

    def create(self, validated_data):
        """创建用户"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ========================================
# Notification Serializer
# ========================================

class NotificationSerializer(serializers.ModelSerializer):
    """
    通知消息序列化器
    """
    from_user_details = UserBasicSerializer(source='from_user', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'content',
            'from_user', 'from_user_details',
            'diary', 'comment',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
