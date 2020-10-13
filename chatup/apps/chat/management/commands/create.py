from django.core.management.base import BaseCommand, CommandError
from random import choice

from ... import models
from ..utils import debug_required


class Command(BaseCommand):
    """ Populate database with needed objects count """

    help = 'Helper for database populating'
    requires_migrations_checks = True

    brod_number_default: int = 10

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '-bn',
            '--brod_num',
            type=int,
            help=f'Broadcasts number to create, {self.brod_number_default} by default'
        )

    @debug_required
    def handle(self, *args, **options) -> None:
        streamers = models.CustomUser.objects.filter(role__sid=models.STREAMER_ROLE_SID)

        if not len(streamers):
            raise CommandError('No streamers in database')

        broadcasts = [
            models.Broadcast(
                title=f'Stream #{i}',
                source_link=f'https://streams.com/stream{i}',
                streamer=choice(streamers)
            )

            for i in range(options.get('--brod_num', self.brod_number_default))
        ]

        models.Broadcast.objects.bulk_create(broadcasts)
        self.stdout.write(self.style.SUCCESS(f'{len(broadcasts)} broadcasts created successfully'))
