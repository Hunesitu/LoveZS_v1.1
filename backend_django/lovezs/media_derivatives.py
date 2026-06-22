import os
from dataclasses import dataclass

from django.conf import settings
from PIL import Image, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class MediaDerivatives:
    compressed_url: str
    thumbnail_url: str


def _media_url(path: str) -> str:
    return f"{settings.MEDIA_URL}{path.replace(os.sep, '/')}"


def _prepare_image(image: Image.Image) -> Image.Image:
    prepared = ImageOps.exif_transpose(image)
    if prepared.mode in ('RGBA', 'LA'):
        return prepared
    if prepared.mode != 'RGB':
        return prepared.convert('RGB')
    return prepared


def _save_webp(image: Image.Image, path: str, max_size: tuple[int, int], quality: int) -> None:
    output = image.copy()
    output.thumbnail(max_size, Image.Resampling.LANCZOS)
    output.save(path, 'WEBP', quality=quality, method=6)


def generate_image_derivatives(filename: str) -> MediaDerivatives | None:
    original_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(original_path):
        return None

    base_name = os.path.splitext(os.path.basename(filename))[0]
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
    os.makedirs(thumbnails_dir, exist_ok=True)
    os.makedirs(compressed_dir, exist_ok=True)

    thumbnail_filename = f'{base_name}.webp'
    compressed_filename = f'{base_name}.webp'
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
    compressed_path = os.path.join(compressed_dir, compressed_filename)

    try:
        with Image.open(original_path) as source:
            image = _prepare_image(source)
            _save_webp(image, thumbnail_path, (480, 480), 72)
            _save_webp(image, compressed_path, (1600, 1200), 78)
    except (UnidentifiedImageError, OSError):
        return None

    return MediaDerivatives(
        compressed_url=_media_url(f'compressed/{compressed_filename}'),
        thumbnail_url=_media_url(f'thumbnails/{thumbnail_filename}'),
    )
