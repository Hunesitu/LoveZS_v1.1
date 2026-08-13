from django.core.management.base import BaseCommand

from lovezs.image_variants import generate_image_variants
from lovezs.models import Photo


class Command(BaseCommand):
    help = 'Generate thumbnail and preview files for image media.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate variants even when target files already exist.',
        )

    def handle(self, *args, **options):
        force = options['force']
        images = Photo.objects.filter(mimetype__startswith='image/')
        generated_count = 0
        skipped_count = 0

        for photo in images.iterator():
            generated = generate_image_variants(photo.filename, force=force)
            if generated:
                generated_count += len(generated)
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Generated {generated_count} variant files; skipped {skipped_count} images.'
            )
        )
