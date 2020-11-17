from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS

from ..utils import debug_required


class Command(BaseCommand):
    """
    Drop specified schema of default database (including all tables, sequences, etc).
    Only for PostgreSQL
    """

    help = 'Drop specified schema of default database'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '-sh',
            '--schema',
            type=str,
            default='public',
            dest='schema',
            help='Schema name for dropping, "public" by default'
        )

        parser.add_argument(
            '-nc',
            '--noconfirm',
            type=bool,
            default=False,
            dest='noconfirm',
            help='Disable confirmation dialog'
        )

    @debug_required
    def handle(self, *args, **options) -> None:
        info = settings.DATABASES[DEFAULT_DB_ALIAS]

        if info['ENGINE'] != 'django.db.backends.postgresql':
            raise CommandError('This command can be used only with PostgreSQL')

        schema = options['schema']
        noconfirm = options['noconfirm']

        if not noconfirm:
            confirmation = input(
                f'All data from "{schema}" schema in default database will be lost. '
                f'Are you sure? [y/N] '
            )

            if confirmation != 'y':
                self.stdout.write(self.style.SUCCESS('Dropping canceled'))
                return

        with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
            cursor.execute(f'DROP SCHEMA {schema} CASCADE')
            cursor.execute(f'CREATE SCHEMA {schema}')

        self.stdout.write(self.style.SUCCESS('Successfully dropped'))
