from django.core.management.base import BaseCommand
from ...tasks import cache_images


class Command(BaseCommand):
    help = 'Create cached response for images'
    requires_migrations_checks = True

    def handle(self, *args, **options) -> None:
        cache_images.delay()
        self.stdout.write('Task sent')
