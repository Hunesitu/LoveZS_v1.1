from datetime import date
from importlib import import_module

from django.apps import apps as django_apps
from django.test import TestCase

from .models import Album, Diary, DiaryPhoto, DiaryTag, Photo
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
