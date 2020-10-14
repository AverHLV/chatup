from django.core.management.base import BaseCommand, CommandError
from random import choice, randint

from uuid import uuid4

from ... import models
from ..utils import debug_required


class Command(BaseCommand):
    """ Populate database with needed objects count """

    help = 'Helper for database populating'
    requires_migrations_checks = True

    dests = ['broadcasts', 'messages']

    broadcast_number_default: int = 10
    message_number_default: int = 20

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '-bn',
            '--brod_num',
            type=int,
            default=0,
            dest=self.dests[0],
            help=f'Broadcasts number to create, {self.broadcast_number_default} by default'
        )

        parser.add_argument(
            '-mn',
            '--msg_num',
            type=int,
            default=0,
            dest=self.dests[1],
            help=f'Messages number to create, {self.message_number_default} by default'
        )

    def create_broadcasts(self, count: int) -> None:
        streamers = models.CustomUser.objects.filter(role__sid=models.STREAMER_ROLE_SID)

        if not len(streamers):
            raise CommandError('No streamers in database')

        broadcasts = [
            models.Broadcast(
                title=f'Stream #{uuid4()}',
                source_link=f'https://streams.com/stream{i}',
                streamer=choice(streamers),
                is_active=choice([True, False]),
                watchers_count=randint(0, 500)
            )

            for i in range(count)
        ]

        models.Broadcast.objects.bulk_create(broadcasts)
        self.stdout.write(self.style.SUCCESS(f'{len(broadcasts)} broadcasts created successfully'))

    def create_messages(self, count: int) -> None:
        broadcasts = models.Broadcast.objects.all()
        users = models.CustomUser.objects.all()
        moderators = models.CustomUser.objects.filter(role__sid=models.MODER_ROLE_SID)

        if not len(broadcasts) or not len(users) or not len(moderators):
            raise CommandError('No needed data in database')

        messages = [
            models.Message(
                text='Message text',
                broadcast=choice(broadcasts),
                author=choice(users),
                deleter=choice(moderators) if i % 5 else None
            )

            for i in range(count)
        ]

        models.Message.objects.bulk_create(messages)
        self.stdout.write(self.style.SUCCESS(f'{len(messages)} messages created successfully'))

    @debug_required
    def handle(self, *args, **options) -> None:
        if not any(options[destination] for destination in self.dests):
            self.create_broadcasts(self.broadcast_number_default)
            self.create_messages(self.message_number_default)

        else:
            if options[self.dests[0]]:
                self.create_broadcasts(options[self.dests[0]])

            if options[self.dests[1]]:
                self.create_messages(options[self.dests[1]])
