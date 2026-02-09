from django.db import migrations


def normalize_photo_url_forward(apps, schema_editor):
    Photo = apps.get_model('lovezs', 'Photo')
    for photo in Photo.objects.only('id', 'url').iterator():
        current_url = (photo.url or '').replace('\\', '/').strip()
        if not current_url:
            continue

        if current_url.startswith('/uploads/'):
            normalized_url = '/media/' + current_url[len('/uploads/'):]
        elif current_url.startswith('uploads/'):
            normalized_url = '/media/' + current_url[len('uploads/'):]
        elif current_url == '/uploads':
            normalized_url = '/media'
        elif current_url == 'uploads':
            normalized_url = '/media'
        else:
            continue

        if normalized_url != photo.url:
            photo.url = normalized_url
            photo.save(update_fields=['url'])


def normalize_photo_url_backward(apps, schema_editor):
    Photo = apps.get_model('lovezs', 'Photo')
    for photo in Photo.objects.only('id', 'url').iterator():
        current_url = (photo.url or '').replace('\\', '/').strip()
        if not current_url:
            continue

        if current_url.startswith('/media/'):
            rollback_url = '/uploads/' + current_url[len('/media/'):]
        elif current_url == '/media':
            rollback_url = '/uploads'
        else:
            continue

        if rollback_url != photo.url:
            photo.url = rollback_url
            photo.save(update_fields=['url'])


class Migration(migrations.Migration):

    dependencies = [
        ('lovezs', '0002_countdown_recurring_day_countdown_recurring_month'),
    ]

    operations = [
        migrations.RunPython(normalize_photo_url_forward, normalize_photo_url_backward),
    ]

