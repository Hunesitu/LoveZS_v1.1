"""
Django Development Settings
开发环境专用配置
"""

from .base import *
from pathlib import Path

# ========================================
# 开发环境特定配置
# ========================================
DEBUG = True

# 允许所有主机（仅开发环境）
ALLOWED_HOSTS = ['*']

# ========================================
# CORS 配置（开发环境允许所有来源）
# ========================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ========================================
# 邮件配置（开发环境使用控制台后端）
# ========================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ========================================
# 静态文件和媒体文件
# ========================================
# 开发环境不需要 collectstatic

# ========================================
# 日志级别
# ========================================
for logger in LOGGING['loggers'].values():
    logger['level'] = 'DEBUG'

# ========================================
# Django Debug Toolbar（可选）
# ========================================
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']
