# You may not need this file, depending on how your project is configured
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Initial boostrapper for MyMusicMaestro deployments'

    def handle(self, *args, **options):
        print('No setup or configuration provided for first-time deplyoment')
