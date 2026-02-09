"""
LoveZs 数据模型
从 Express + Mongoose 迁移到 Django + PostgreSQL

对应原文件:
- backend/src/models/Diary.ts
- backend/src/models/Photo.ts
- backend/src/models/Countdown.ts
- backend/src/models/Album.ts
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from datetime import date


# ========================================
# 选项枚举 (对应 Mongoose 的 enum)
# ========================================

class MoodChoice(models.TextChoices):
    """心情选项"""
    HAPPY = 'happy', '开心'
    SAD = 'sad', '伤心'
    EXCITED = 'excited', '兴奋'
    CALM = 'calm', '平静'
    ANGRY = 'angry', '生气'
    TIRED = 'tired', '疲惫'
    LOVED = 'loved', '被爱'
    GRATEFUL = 'grateful', '感恩'


class CountdownType(models.TextChoices):
    """重要日类型"""
    ANNIVERSARY = 'anniversary', '纪念日'
    BIRTHDAY = 'birthday', '生日'
    EVENT = 'event', '事件'
    OTHER = 'other', '其他'


class CountdownDirection(models.TextChoices):
    """重要日方向"""
    COUNTUP = 'countup', '累计'
    COUNTDOWN = 'countdown', '倒计时'


class RecurringType(models.TextChoices):
    """重复类型"""
    YEARLY = 'yearly', '每年'
    MONTHLY = 'monthly', '每月'
    DAILY = 'daily', '每天'


# ========================================
# Album 模型 (相册)
# 对应: backend/src/models/Album.ts
# ========================================

class Album(models.Model):
    """
    相册模型
    用于组织和管理照片
    """
    name = models.CharField(
        max_length=50,
        verbose_name='相册名称',
        help_text='相册名称最多50个字符'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='描述',
        help_text='相册描述最多200个字符'
    )
    cover_photo = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='封面照片',
        help_text='封面照片URL'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='是否默认',
        help_text='默认相册，只能有一个'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '相册'
        verbose_name_plural = '相册'
        indexes = [
            models.Index(fields=['is_default']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        保存时确保只有一个默认相册
        对应 Mongoose 的 pre('save') hook
        """
        if self.is_default:
            # 将其他相册的 is_default 设为 False
            Album.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


# ========================================
# Photo 模型 (照片)
# 对应: backend/src/models/Photo.ts
# ========================================

class Photo(models.Model):
    """
    照片模型
    存储照片信息、EXIF数据、位置信息
    """
    # 基本信息
    filename = models.CharField(max_length=255, verbose_name='文件名')
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    path = models.CharField(max_length=500, verbose_name='文件路径')
    url = models.CharField(max_length=500, verbose_name='访问URL')
    size = models.BigIntegerField(verbose_name='文件大小(字节)')
    mimetype = models.CharField(max_length=100, verbose_name='MIME类型')

    # 关联相册
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='所属相册'
    )

    # 描述和标签
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='描述'
    )

    # JSON字段存储复杂信息 (PostgreSQL 特性)
    # 对应 Mongoose 的嵌套对象
    location = models.JSONField(
        blank=True,
        null=True,
        verbose_name='位置信息',
        help_text='格式: {"latitude": 数字, "longitude": 数字, "address": "字符串"}'
    )
    exif = models.JSONField(
        blank=True,
        null=True,
        verbose_name='EXIF信息',
        help_text='格式: {"camera": "相机", "lens": "镜头", "aperture": "光圈", ...}'
    )

    # 压缩图URL
    compressed_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='压缩图URL'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '照片'
        verbose_name_plural = '照片'
        indexes = [
            models.Index(fields=['album', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name

    # ========================================
    # 虚拟字段 (对应 Mongoose 的 virtual)
    # ========================================

    @property
    def size_formatted(self):
        """
        格式化的文件大小
        对应 Mongoose virtual: sizeFormatted
        """
        sizes = ['Bytes', 'KB', 'MB', 'GB']
        if self.size == 0:
            return '0 Byte'
        import math
        i = math.floor(math.log(self.size) / math.log(1024))
        return f"{round(self.size / math.pow(1024, i) * 100) / 100} {sizes[i]}"

    @property
    def thumbnail_url(self):
        """
        缩略图URL
        对应 Mongoose virtual: thumbnailUrl
        """
        if not self.filename:
            return ''
        return f"{settings.MEDIA_URL}thumbnails/{self.filename}"


# ========================================
# Diary 模型 (日记)
# 对应: backend/src/models/Diary.ts
# ========================================

class Diary(models.Model):
    """
    日记模型
    存储日记内容、心情、分类、标签
    """
    title = models.CharField(
        max_length=100,
        verbose_name='标题',
        help_text='日记标题最多100个字符'
    )
    content = models.TextField(
        max_length=10000,
        verbose_name='内容',
        help_text='日记内容最多10000个字符，支持Markdown'
    )
    mood = models.CharField(
        max_length=20,
        choices=MoodChoice.choices,
        default=MoodChoice.HAPPY,
        verbose_name='心情'
    )
    category = models.CharField(
        max_length=20,
        verbose_name='分类',
        help_text='日记分类最多20个字符'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='日期',
        db_index=True
    )

    # 关联照片 (多对多关系)
    attached_photos = models.ManyToManyField(
        Photo,
        through='DiaryPhoto',
        related_name='diaries',
        blank=True,
        verbose_name='关联照片'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '日记'
        verbose_name_plural = '日记'
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['category']),
            models.Index(fields=['mood']),
        ]
        ordering = ['-date']

    def __str__(self):
        return self.title

    # ========================================
    # 虚拟字段 (对应 Mongoose 的 virtual)
    # ========================================

    @property
    def formatted_date(self):
        """
        格式化的日期
        对应 Mongoose virtual: formattedDate
        """
        return self.date.isoformat()

    @property
    def word_count(self):
        """
        字数统计
        对应 Mongoose virtual: wordCount
        """
        return len(self.content.split())

    @property
    def tags(self):
        """
        获取标签列表
        通过 DiaryTag 关联表获取
        """
        return list(DiaryTag.objects.filter(diary=self).values_list('tag', flat=True))


# ========================================
# Diary 关联模型 (多对多关系的中间表)
# ========================================

class DiaryPhoto(models.Model):
    """
    日记-照片关联表
    用于管理日记和照片的多对多关系
    """
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    attached_at = models.DateTimeField(auto_now_add=True, verbose_name='关联时间')

    class Meta:
        verbose_name = '日记照片关联'
        verbose_name_plural = '日记照片关联'
        unique_together = ('diary', 'photo')
        indexes = [
            models.Index(fields=['diary']),
            models.Index(fields=['photo']),
        ]

    def __str__(self):
        return f"{self.diary.title} - {self.photo.original_name}"


class DiaryTag(models.Model):
    """
    日记标签模型
    用于存储日记的标签
    """
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='diary_tags')
    tag = models.CharField(max_length=20, verbose_name='标签')

    class Meta:
        verbose_name = '日记标签'
        verbose_name_plural = '日记标签'
        unique_together = ('diary', 'tag')
        indexes = [
            models.Index(fields=['diary']),
            models.Index(fields=['tag']),
        ]

    def __str__(self):
        return f"{self.diary.title} - {self.tag}"


# ========================================
# Countdown 模型 (重要日)
# 对应: backend/src/models/Countdown.ts
# ========================================

class Countdown(models.Model):
    """
    重要日模型
    用于管理纪念日、生日、事件等重要日期
    """
    title = models.CharField(
        max_length=50,
        verbose_name='标题',
        help_text='重要日标题最多50个字符'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='描述',
        help_text='描述最多200个字符'
    )
    target_date = models.DateField(
        verbose_name='目标日期',
        help_text='重要日日期'
    )
    type = models.CharField(
        max_length=20,
        choices=CountdownType.choices,
        default=CountdownType.OTHER,
        verbose_name='类型'
    )
    direction = models.CharField(
        max_length=20,
        choices=CountdownDirection.choices,
        default=CountdownDirection.COUNTUP,
        verbose_name='方向',
        help_text='countup: 已过去天数, countdown: 倒计时'
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name='是否重复'
    )
    recurring_type = models.CharField(
        max_length=20,
        choices=RecurringType.choices,
        blank=True,
        verbose_name='重复类型',
        help_text='每年/每月/每天重复'
    )
    recurring_month = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='重复月份',
        help_text='每年重复时的月份 (1-12)'
    )
    recurring_day = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='重复日期',
        help_text='每年重复时的日期 (1-31)'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '重要日'
        verbose_name_plural = '重要日'
        indexes = [
            models.Index(fields=['target_date']),
            models.Index(fields=['type']),
            models.Index(fields=['direction']),
        ]
        ordering = ['target_date']

    def __str__(self):
        return self.title

    # ========================================
    # 虚拟字段 (对应 Mongoose 的 virtual)
    # ========================================

    @property
    def days(self):
        """
        计算天数差
        - 每年重复：计算距离下一个该月日的天数
        - 固定类型：计算距离目标日期的天数
        countup: 已过去的纪念日（负数）
        countdown: 倒计时（正数）
        """
        today = date.today()

        # 每年重复：计算下一个该月日
        if self.is_recurring and self.recurring_type == 'yearly' and self.recurring_month and self.recurring_day:
            try:
                target_this_year = date(today.year, self.recurring_month, self.recurring_day)
            except ValueError:
                # 处理无效日期（如2月30日），使用2月28日
                target_this_year = date(today.year, self.recurring_month, 28)

            try:
                target_next_year = date(today.year + 1, self.recurring_month, self.recurring_day)
            except ValueError:
                target_next_year = date(today.year + 1, self.recurring_month, 28)

            # 选择今年或明年的日期
            if target_this_year >= today:
                target = target_this_year
            else:
                target = target_next_year

            return (target - today).days
        else:
            # 固定日期：原有逻辑
            target = self.target_date
            diff = (target - today).days

            # 对于 countup，天数减1（纪念日当天算第1天）
            if self.direction == CountdownDirection.COUNTUP:
                diff -= 1

            return diff

    @property
    def absolute_days(self):
        """
        绝对天数（始终为正数）
        对应 Mongoose virtual: absoluteDays
        """
        return abs(self.days)

    @property
    def formatted_target_date(self):
        """
        格式化的目标日期
        对应 Mongoose virtual: formattedTargetDate
        """
        return self.target_date.isoformat()

    @property
    def status(self):
        """
        状态判断
        对应 Mongoose virtual: status
        """
        days = self.days

        if self.direction == CountdownDirection.COUNTUP:
            # countup: 已过去的纪念日
            if days <= -365:
                return 'long-time'
            if days <= -30:
                return 'month'
            return 'recent'
        else:
            # countdown: 倒计时
            if days <= 0:
                return 'today'
            if days <= 7:
                return 'urgent'
            if days <= 30:
                return 'soon'
            return 'upcoming'
