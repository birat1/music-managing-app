# Seeding carries no marks but may help you write your tests
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Insert sample data into database for tests'

    def handle(self, *args, **options):
        print('No seeding command provided for testing')
