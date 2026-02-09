"""
Django Production Settings
生产环境专用配置
"""

from .base import *
from decouple import config

# ========================================
# 生产环境特定配置
# ========================================
DEBUG = False

# ========================================
# 安全配置
# ========================================
# 备案前 IP 调试阶段可设为 False，域名 + HTTPS 正式上线后应设为 True
ENABLE_HTTPS_SECURITY = config('ENABLE_HTTPS_SECURITY', default=True, cast=bool)

SECURE_SSL_REDIRECT = ENABLE_HTTPS_SECURITY
SESSION_COOKIE_SECURE = ENABLE_HTTPS_SECURITY
CSRF_COOKIE_SECURE = ENABLE_HTTPS_SECURITY
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if ENABLE_HTTPS_SECURITY else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = ENABLE_HTTPS_SECURITY
SECURE_HSTS_PRELOAD = ENABLE_HTTPS_SECURITY
X_FRAME_OPTIONS = "DENY"

# ========================================
# 日志配置（生产环境）
# ========================================
LOGGING['handlers']['file']['maxBytes'] = 1024 * 1024 * 50  # 50MB
LOGGING['handlers']['file']['backupCount'] = 30

# ========================================
# 静态文件
# ========================================
# 生产环境可按需启用 WhiteNoise
# INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')
# MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

