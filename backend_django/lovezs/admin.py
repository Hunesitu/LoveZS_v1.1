"""
LoveZs Django Admin 配置
提供后台管理界面
"""

from django.contrib import admin
from .models import Album, Photo, Diary, DiaryPhoto, DiaryTag, Countdown


# ========================================
# Album Admin
# ========================================

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    相册管理界面
    """
    list_display = ['name', 'is_default', 'created_at', 'photo_count']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def photo_count(self, obj):
        """显示相册中的照片数量"""
        return obj.photos.count()
    photo_count.short_description = '照片数量'


# ========================================
# Photo Admin
# ========================================

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """
    照片管理界面
    """
    list_display = ['original_name', 'album', 'size_formatted', 'created_at', 'thumbnail_preview']
    list_filter = ['album', 'created_at', 'mimetype']
    search_fields = ['original_name', 'filename', 'description']
    ordering = ['-created_at']
    readonly_fields = ['size_formatted', 'thumbnail_url', 'created_at', 'updated_at']

    def thumbnail_preview(self, obj):
        """显示缩略图预览"""
        if obj.url:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.thumbnail_url)
        return '-'
    thumbnail_preview.short_description = '预览'


# ========================================
# Diary Admin
# ========================================

class DiaryPhotoInline(admin.TabularInline):
    """
    日记照片关联内联编辑
    """
    model = DiaryPhoto
    extra = 1
    autocomplete_fields = ['photo']


class DiaryTagInline(admin.TabularInline):
    """
    日记标签内联编辑
    """
    model = DiaryTag
    extra = 1


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    """
    日记管理界面
    """
    list_display = ['title', 'category', 'mood', 'date', 'word_count', 'created_at']
    list_filter = ['category', 'mood', 'date', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'date'
    ordering = ['-date']
    inlines = [DiaryPhotoInline, DiaryTagInline]
    readonly_fields = ['formatted_date', 'word_count', 'created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'date')
        }),
        ('分类与标签', {
            'fields': ('category', 'mood')
        }),
        ('只读信息', {
            'fields': ('formatted_date', 'word_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ========================================
# Countdown Admin
# ========================================

@admin.register(Countdown)
class CountdownAdmin(admin.ModelAdmin):
    """
    重要日管理界面
    """
    list_display = ['title', 'target_date', 'type', 'direction', 'days_display', 'status_display']
    list_filter = ['type', 'direction', 'target_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'target_date'
    ordering = ['target_date']
    readonly_fields = ['days', 'absolute_days', 'status', 'created_at', 'updated_at']

    def days_display(self, obj):
        """显示天数（带颜色）"""
        days = obj.days
        from django.utils.html import format_html

        if days > 0:
            # 倒计时（绿色）
            return format_html('<span style="color: green;">{} 天</span>', days)
        elif days < 0:
            # 已过去（红色）
            return format_html('<span style="color: red;">{} 天</span>', abs(days))
        else:
            # 今天（蓝色）
            return format_html('<span style="color: blue; font-weight: bold;">今天</span>')
    days_display.short_description = '天数'

    def status_display(self, obj):
        """显示状态"""
        status = obj.status
        status_map = {
            'today': '今天',
            'urgent': '紧急',
            'soon': '即将到来',
            'upcoming': '未来',
            'recent': '最近',
            'month': '一个月内',
            'long-time': '很久以前',
        }
        return status_map.get(status, status)
    status_display.short_description = '状态'


# ========================================
# DiaryPhoto Admin (可选，用于调试)
# ========================================

@admin.register(DiaryPhoto)
class DiaryPhotoAdmin(admin.ModelAdmin):
    """
    日记-照片关联管理界面
    """
    list_display = ['diary', 'photo', 'attached_at']
    list_filter = ['attached_at']
    search_fields = ['diary__title', 'photo__original_name']
    autocomplete_fields = ['diary', 'photo']


# ========================================
# DiaryTag Admin (可选，用于调试)
# ========================================

@admin.register(DiaryTag)
class DiaryTagAdmin(admin.ModelAdmin):
    """
    日记标签管理界面
    """
    list_display = ['diary', 'tag']
    list_filter = ['tag']
    search_fields = ['diary__title', 'tag']
    autocomplete_fields = ['diary']


# ========================================
# Admin 站点配置
# ========================================

admin.site.site_header = 'LoveZs 管理后台'
admin.site.site_title = 'LoveZs'
admin.site.index_title = '欢迎使用 LoveZs 管理系统'
