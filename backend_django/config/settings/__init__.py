# Django Settings 包
# 根据环境变量自动选择配置文件

from decouple import config

ENV = config('DJANGO_ENV', default='development')

if ENV == 'production':
    from .production import *
elif ENV == 'testing':
    from .testing import *
else:
    from .development import *
