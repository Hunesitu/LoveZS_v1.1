from django.core.management.base import BaseCommand

from lovezs.media_derivatives import generate_image_derivatives
from lovezs.models import Photo


class Command(BaseCommand):
    help = 'Generate missing compressed and thumbnail images for uploaded photos.'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(mimetype__startswith='image/')
        total = photos.count()
        generated = 0
        skipped = 0

        for photo in photos.iterator():
            derivatives = generate_image_derivatives(photo.filename)
            if not derivatives:
                skipped += 1
                self.stdout.write(self.style.WARNING(f'Skipped {photo.filename}'))
                continue

            if photo.compressed_url != derivatives.compressed_url:
                photo.compressed_url = derivatives.compressed_url
                photo.save(update_fields=['compressed_url'])
            generated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {generated} image(s), skipped {skipped}, total {total}.'
            )
        )
