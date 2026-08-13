import os

from PIL import Image, ImageOps
from django.conf import settings


THUMBNAIL_SIZE = (480, 480)
PREVIEW_SIZE = (1280, 1280)


def _save_resized_image(source_path, target_path, size):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with Image.open(source_path) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail(size)

        save_kwargs = {}
        if image.format in {'JPEG', 'JPG'} or os.path.splitext(target_path)[1].lower() in {'.jpg', '.jpeg'}:
            if image.mode not in {'RGB', 'L'}:
                image = image.convert('RGB')
            save_kwargs = {'quality': 82, 'optimize': True}

        image.save(target_path, **save_kwargs)


def generate_image_variants(filename, force=False):
    if not filename:
        return []

    original_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(original_path):
        return []

    variants = [
        ('thumbnails', THUMBNAIL_SIZE),
        ('previews', PREVIEW_SIZE),
    ]
    generated = []

    for directory, size in variants:
        target_path = os.path.join(settings.MEDIA_ROOT, directory, filename)
        if force or not os.path.exists(target_path):
            _save_resized_image(original_path, target_path, size)
            generated.append(target_path)

    return generated
