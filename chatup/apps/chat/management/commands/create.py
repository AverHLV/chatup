from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from ..utils import debug_required, create_broadcasts, create_messages


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

    @debug_required
    @atomic
    def handle(self, *args, **options) -> None:
        active_broadcast = None
        broadcasts, messages = [], []

        if not any(options[destination] for destination in self.dests):
            broadcasts, active_broadcast = create_broadcasts(self.broadcast_number_default)
            messages = create_messages(self.message_number_default)

        else:
            if options[self.dests[0]]:
                broadcasts, active_broadcast = create_broadcasts(options[self.dests[0]])

            if options[self.dests[1]]:
                messages = create_messages(options[self.dests[1]])

        if active_broadcast is not None:
            self.stdout.write(
                self.style.SUCCESS(f'Broadcast #{active_broadcast.id} marked as active')
            )

        if len(broadcasts):
            self.stdout.write(
                self.style.SUCCESS(f'{len(broadcasts)} broadcasts created successfully')
            )

        if len(messages):
            self.stdout.write(self.style.SUCCESS(f'{len(messages)} messages created successfully'))
