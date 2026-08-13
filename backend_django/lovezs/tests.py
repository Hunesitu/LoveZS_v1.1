import tempfile
from datetime import date
from io import BytesIO
from importlib import import_module

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from PIL import Image
from rest_framework.test import APIClient

from .models import Album, Diary, DiaryFavorite, DiaryPhoto, DiaryTag, Photo
from .serializers import DiaryCreateSerializer, DiarySerializer


class DiarySerializerTests(TestCase):
    def setUp(self):
        self.album = Album.objects.create(name='默认相册', is_default=True)
        self.photo = Photo.objects.create(
            filename='photo-a.jpg',
            original_name='photo-a.jpg',
            path='/photo-a.jpg',
            url='/media/photo-a.jpg',
            size=1024,
            mimetype='image/jpeg',
            album=self.album,
        )
        self.diary = Diary.objects.create(
            title='测试日记',
            content='测试内容',
            mood='happy',
            category='生活',
            date=date(2026, 2, 7),
        )
        DiaryPhoto.objects.create(diary=self.diary, photo=self.photo)

    def test_attached_photos_should_serialize_photo_objects(self):
        serializer = DiarySerializer(self.diary)
        data = serializer.data

        self.assertIn('attached_photos', data)
        self.assertEqual(len(data['attached_photos']), 1)
        self.assertEqual(data['attached_photos'][0]['id'], self.photo.id)
        self.assertEqual(data['attached_photos'][0]['original_name'], self.photo.original_name)


class DiaryCreateSerializerUpdateTests(TestCase):
    def setUp(self):
        self.album = Album.objects.create(name='默认相册', is_default=True)
        self.photo_a = Photo.objects.create(
            filename='photo-a.jpg',
            original_name='photo-a.jpg',
            path='/photo-a.jpg',
            url='/media/photo-a.jpg',
            size=1024,
            mimetype='image/jpeg',
            album=self.album,
        )
        self.photo_b = Photo.objects.create(
            filename='photo-b.jpg',
            original_name='photo-b.jpg',
            path='/photo-b.jpg',
            url='/media/photo-b.jpg',
            size=2048,
            mimetype='image/jpeg',
            album=self.album,
        )
        self.diary = Diary.objects.create(
            title='旧标题',
            content='旧内容',
            mood='happy',
            category='生活',
            date=date(2026, 2, 7),
        )
        DiaryTag.objects.create(diary=self.diary, tag='旧标签')
        DiaryPhoto.objects.create(diary=self.diary, photo=self.photo_a)

    def test_update_should_replace_tags_and_photo_relations(self):
        serializer = DiaryCreateSerializer(
            instance=self.diary,
            data={
                'title': '新标题',
                'tags': ['新标签'],
                'photo_ids': [self.photo_b.id],
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_diary = serializer.save()

        self.assertEqual(updated_diary.title, '新标题')
        self.assertEqual(
            list(DiaryTag.objects.filter(diary=updated_diary).values_list('tag', flat=True)),
            ['新标签'],
        )
        self.assertEqual(
            list(updated_diary.attached_photos.values_list('id', flat=True)),
            [self.photo_b.id],
        )

    def test_update_should_preserve_requested_photo_order(self):
        serializer = DiaryCreateSerializer(
            instance=self.diary,
            data={'photo_ids': [self.photo_b.id, self.photo_a.id]},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_diary = serializer.save()

        data = DiarySerializer(updated_diary).data
        self.assertEqual(
            [photo['id'] for photo in data['attached_photos']],
            [self.photo_b.id, self.photo_a.id],
        )


class MediaCompatibilityTests(TestCase):
    def setUp(self):
        self.album = Album.objects.create(name='默认相册', is_default=True)

    def test_uploads_route_should_redirect_to_media_path(self):
        response = self.client.get('/uploads/demo.jpg')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/media/demo.jpg')

    def test_photo_url_migration_helpers_should_normalize_and_rollback(self):
        photo = Photo.objects.create(
            filename='legacy.jpg',
            original_name='legacy.jpg',
            path='/legacy.jpg',
            url='/uploads/legacy.jpg',
            size=1024,
            mimetype='image/jpeg',
            album=self.album,
        )

        migration_module = import_module(
            'lovezs.migrations.0003_normalize_photo_url_uploads_to_media'
        )

        migration_module.normalize_photo_url_forward(django_apps, None)
        photo.refresh_from_db()
        self.assertEqual(photo.url, '/media/legacy.jpg')

        migration_module.normalize_photo_url_backward(django_apps, None)
        photo.refresh_from_db()
        self.assertEqual(photo.url, '/uploads/legacy.jpg')


class PhotoUploadDerivativeTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_root.cleanup)

    def make_image_file(self):
        buffer = BytesIO()
        image = Image.new('RGB', (1200, 800), '#d95984')
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile('memory.jpg', buffer.read(), content_type='image/jpeg')

    def test_upload_should_create_compressed_and_thumbnail_images(self):
        with override_settings(MEDIA_ROOT=self.media_root.name):
            response = self.client.post(
                '/api/photos/upload/',
                {'photos': [self.make_image_file()]},
            )

        self.assertEqual(response.status_code, 200)
        photo_data = response.json()['data']['photos'][0]
        self.assertTrue(photo_data['compressed_url'].startswith('/media/compressed/'))
        self.assertTrue(photo_data['compressed_url'].endswith('.webp'))
        self.assertTrue(photo_data['thumbnail_url'].startswith('/media/thumbnails/'))
        self.assertTrue(photo_data['thumbnail_url'].endswith('.webp'))


class DiaryFavoriteApiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='favorite-user', password='test-pass-123')
        self.other_user = user_model.objects.create_user(username='other-user', password='test-pass-123')
        self.diary = Diary.objects.create(
            title='可收藏日记', content='内容', mood='happy', category='生活', created_by=self.other_user
        )
        self.client = APIClient()

    def test_favorite_requires_authentication(self):
        response = self.client.post(f'/api/diaries/{self.diary.id}/favorite/')
        self.assertEqual(response.status_code, 401)

    def test_favorite_is_idempotent_and_private_to_user(self):
        self.client.force_authenticate(self.user)
        url = f'/api/diaries/{self.diary.id}/favorite/'
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(DiaryFavorite.objects.filter(user=self.user, diary=self.diary).count(), 1)

        detail = self.client.get(f'/api/diaries/{self.diary.id}/').json()['data']['diary']
        self.assertTrue(detail['is_favorited'])
        self.client.force_authenticate(self.other_user)
        detail = self.client.get(f'/api/diaries/{self.diary.id}/').json()['data']['diary']
        self.assertFalse(detail['is_favorited'])

    def test_unfavorite_and_favorites_filter(self):
        DiaryFavorite.objects.create(user=self.user, diary=self.diary)
        self.client.force_authenticate(self.user)
        diaries = self.client.get('/api/diaries/', {'favorites': 'true'}).json()['results']['diaries']
        self.assertEqual([item['id'] for item in diaries], [self.diary.id])
        self.assertEqual(self.client.delete(f'/api/diaries/{self.diary.id}/favorite/').status_code, 200)
        self.assertFalse(DiaryFavorite.objects.filter(user=self.user, diary=self.diary).exists())
