"""
Django API 测试脚本
测试所有 API 端点是否正常工作

使用方法:
    python manage.py shell < test_api.py
或
    python test_api.py
"""

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.utils import timezone
from datetime import date, timedelta
import json

from lovezs.models import Album, Photo, Diary, Countdown

def test_api():
    """测试所有 API 端点"""
    client = Client()

    print("=" * 60)
    print("LoveZs Django API 测试")
    print("=" * 60)

    # ========================================
    # 1. 健康检查
    # ========================================
    print("\n[1] 测试健康检查...")
    response = client.get('/api/health/')
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")

    # ========================================
    # 2. 创建相册
    # ========================================
    print("\n[2] 测试相册 API...")

    # 创建相册
    response = client.post('/api/photos/albums/', data=json.dumps({
        'name': '测试相册',
        'description': '这是一个测试相册',
        'is_default': False
    }), content_type='application/json')
    print(f"  POST /api/photos/albums/ - Status: {response.status_code}")
    album_id = response.json().get('data', {}).get('album', {}).get('id')

    # 获取相册列表
    response = client.get('/api/photos/albums/')
    print(f"  GET /api/photos/albums/ - Status: {response.status_code}")
    albums = response.json().get('data', {}).get('albums', [])
    print(f"  相册数量: {len(albums)}")

    # ========================================
    # 3. 创建日记
    # ========================================
    print("\n[3] 测试日记 API...")

    # 创建日记
    response = client.post('/api/diaries/', data=json.dumps({
        'title': '测试日记',
        'content': '这是今天的日记内容，记录美好生活。',
        'mood': 'happy',
        'category': '生活',
        'date': '2026-02-06',
        'tags': ['测试', '快乐'],
        'photoIds': []
    }), content_type='application/json')
    print(f"  POST /api/diaries/ - Status: {response.status_code}")
    print(f"  Response: {response.json().get('message', '')}")

    # 获取日记列表
    response = client.get('/api/diaries/')
    print(f"  GET /api/diaries/ - Status: {response.status_code}")
    diaries = response.json().get('data', {}).get('diaries', [])
    print(f"  日记数量: {len(diaries)}")

    if diaries:
        diary_id = diaries[0].get('id')
        print(f"  第一篇日记: {diaries[0].get('title')}")

        # 获取单篇日记
        response = client.get(f'/api/diaries/{diary_id}/')
        print(f"  GET /api/diaries/{diary_id}/ - Status: {response.status_code}")

    # 获取分类
    response = client.get('/api/diaries/meta/categories/')
    print(f"  GET /api/diaries/meta/categories/ - Status: {response.status_code}")
    print(f"  分类: {response.json().get('data', {}).get('categories', [])}")

    # 获取标签
    response = client.get('/api/diaries/meta/tags/')
    print(f"  GET /api/diaries/meta/tags/ - Status: {response.status_code}")
    print(f"  标签: {response.json().get('data', {}).get('tags', [])}")

    # ========================================
    # 4. 创建重要日
    # ========================================
    print("\n[4] 测试重要日 API...")

    # 创建重要日（过去日期，应该是 countup）
    response = client.post('/api/countdowns/', data=json.dumps({
        'title': '恋爱纪念日',
        'description': '我们开始交往的日子',
        'target_date': '2025-01-01',
        'type': 'anniversary',
        # direction 不设置，让系统自动判断
    }), content_type='application/json')
    print(f"  POST /api/countdowns/ - Status: {response.status_code}")
    countdown_data = response.json().get('data', {}).get('countdown', {})
    print(f"  自动判断 direction: {countdown_data.get('direction')}")
    print(f"  已过去天数: {countdown_data.get('days')}")

    # 获取重要日列表
    response = client.get('/api/countdowns/')
    print(f"  GET /api/countdowns/ - Status: {response.status_code}")
    countdowns = response.json().get('data', {}).get('countdowns', [])
    print(f"  重要日数量: {len(countdowns)}")

    # ========================================
    # 5. 测试分页
    # ========================================
    print("\n[5] 测试分页...")
    response = client.get('/api/diaries/?page=1&page_size=10')
    print(f"  GET /api/diaries/?page=1&page_size=10 - Status: {response.status_code}")

    # ========================================
    # 6. 测试过滤
    # ========================================
    print("\n[6] 测试过滤...")
    response = client.get('/api/diaries/?mood=happy')
    print(f"  GET /api/diaries/?mood=happy - Status: {response.status_code}")

    # ========================================
    # 7. 测试搜索
    # ========================================
    print("\n[7] 测试搜索...")
    response = client.get('/api/diaries/?search=测试')
    print(f"  GET /api/diaries/?search=测试 - Status: {response.status_code}")

    # ========================================
    # 完成
    # ========================================
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("  - Django Admin: http://localhost:8000/admin/")
    print("  - API Root: http://localhost:8000/api/")
    print("  - 超级用户: admin / admin123")


if __name__ == '__main__':
    test_api()
